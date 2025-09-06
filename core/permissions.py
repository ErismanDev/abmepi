from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from functools import wraps
from .models import Usuario


def get_user_permissions(user):
    """
    Retorna as permissões baseadas no tipo de usuário
    """
    if not hasattr(user, 'tipo_usuario'):
        return []
    
    permissions = {
        'administrador_sistema': [
            # Acesso total ao sistema
            'full_access'
        ],
        'advogado': [
            # Acesso ao módulo ASEJUS e funcionalidades relacionadas
            'assejus_access',
            'assejus_full_access'
        ],
        'psicologo': [
            # Acesso ao módulo de psicologia e funcionalidades relacionadas
            'psicologia_access',
            'psicologia_full_access',
            'paciente_ficha_access'
        ],
        'atendente_advogado': [
            # Acesso limitado ao módulo ASEJUS
            'assejus_access',
            'assejus_limited_access'
        ],
        'atendente_psicologo': [
            # Acesso limitado ao módulo de psicologia
            'psicologia_access',
            'psicologia_limited_access'
        ],
        'atendente_geral': [
            # Acesso básico ao sistema
            'basic_access'
        ],
        'associado': [
            # Acesso apenas às informações próprias
            'self_info_access',
            # Acesso limitado ao hotel de trânsito (apenas reservas)
            'hotel_transito_reserva_access'
        ]
    }
    
    return permissions.get(user.tipo_usuario, [])


def has_permission(user, required_permission):
    """
    Verifica se o usuário tem a permissão necessária
    """
    user_permissions = get_user_permissions(user)
    return required_permission in user_permissions


def can_access_hotel_transito_reservas(user):
    """
    Verifica se o usuário pode acessar funcionalidades de reserva do hotel de trânsito
    """
    return user.tipo_usuario == 'associado' or has_permission(user, 'hotel_transito_reserva_access')


def can_edit_profile(user):
    """
    Verifica se o usuário pode editar seu perfil
    """
    return user.tipo_usuario != 'associado'


def require_permission(permission):
    """
    Decorator para verificar permissões
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not has_permission(request.user, permission):
                raise PermissionDenied("Você não tem permissão para acessar esta funcionalidade.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_user_type(allowed_types):
    """
    Decorator para verificar tipo de usuário
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar se é uma requisição AJAX
            is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                request.headers.get('Accept') == 'application/json' or
                request.path.endswith('/modal/') or
                'modal' in request.path or
                request.method == 'POST'  # Requisições POST para modais são consideradas AJAX
            )
            
            if not request.user.is_authenticated:
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Usuário não autenticado',
                        'redirect': '/login/',
                        'error_type': 'authentication_required'
                    })
                else:
                    return redirect('login')
            
            if not hasattr(request.user, 'tipo_usuario'):
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Tipo de usuário não definido.',
                        'error_type': 'user_type_undefined'
                    })
                else:
                    raise PermissionDenied("Tipo de usuário não definido.")
            
            if request.user.tipo_usuario not in allowed_types:
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': 'Você não tem permissão para acessar esta funcionalidade.',
                        'error_type': 'permission_denied',
                        'user_type': getattr(request.user, 'tipo_usuario', 'N/A'),
                        'allowed_types': allowed_types
                    })
                else:
                    raise PermissionDenied("Você não tem permissão para acessar esta funcionalidade.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Mixins para views baseadas em classe
class PermissionRequiredMixin:
    """
    Mixin para verificar permissões em views baseadas em classe
    """
    permission_required = None
    user_types_allowed = None
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se é uma requisição AJAX
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Accept') == 'application/json' or
            request.path.endswith('/modal/') or
            'modal' in request.path or
            request.method == 'POST'  # Requisições POST para modais são consideradas AJAX
        )
        
        if not request.user.is_authenticated:
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'message': 'Usuário não autenticado',
                    'redirect': '/login/',
                    'error_type': 'authentication_required'
                })
            else:
                return redirect('login')
        
        # Verificar tipo de usuário
        if self.user_types_allowed and request.user.tipo_usuario not in self.user_types_allowed:
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para acessar esta funcionalidade.',
                    'error_type': 'permission_denied',
                    'user_type': getattr(request.user, 'tipo_usuario', 'N/A'),
                    'allowed_types': self.user_types_allowed
                })
            else:
                raise PermissionDenied("Você não tem permissão para acessar esta funcionalidade.")
        
        # Verificar permissão específica
        if self.permission_required and not has_permission(request.user, self.permission_required):
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para acessar esta funcionalidade.',
                    'error_type': 'permission_denied',
                    'permission_required': self.permission_required
                })
            else:
                raise PermissionDenied("Você não tem permissão para acessar esta funcionalidade.")
        
        return super().dispatch(request, *args, **kwargs)


# Permissões específicas para módulos
class AssejusAccessMixin(PermissionRequiredMixin):
    """
    Mixin para acesso ao módulo ASEJUS
    """
    user_types_allowed = ['administrador_sistema', 'advogado', 'atendente_advogado']


class PsicologiaAccessMixin(PermissionRequiredMixin):
    """
    Mixin para acesso ao módulo de psicologia
    """
    user_types_allowed = ['administrador_sistema', 'psicologo', 'atendente_psicologo']


class PsicologiaFullAccessMixin(PermissionRequiredMixin):
    """
    Mixin para acesso completo ao módulo de psicologia (incluindo fichas)
    """
    user_types_allowed = ['administrador_sistema', 'psicologo']


class PsicologoRestrictedMixin(PermissionRequiredMixin):
    """
    Mixin para psicólogos que só podem ver seus próprios pacientes
    """
    user_types_allowed = ['psicologo']
    
    def get_queryset(self):
        """
        Filtra o queryset para mostrar apenas os pacientes do psicólogo logado
        """
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'psicologo'):
            return queryset.filter(psicologo_responsavel=self.request.user.psicologo)
        return queryset.none()


class AssejusFullAccessMixin(PermissionRequiredMixin):
    """
    Mixin para acesso completo ao módulo ASEJUS
    """
    user_types_allowed = ['administrador_sistema', 'advogado']


# Funções auxiliares para verificar permissões em templates
def can_access_assejus(user):
    """Verifica se o usuário pode acessar o módulo ASEJUS"""
    return user.is_authenticated and user.tipo_usuario in ['administrador_sistema', 'advogado', 'atendente_advogado']


def can_access_psicologia(user):
    """Verifica se o usuário pode acessar o módulo de psicologia"""
    return user.is_authenticated and user.tipo_usuario in ['administrador_sistema', 'psicologo', 'atendente_psicologo']


def can_access_paciente_ficha(user):
    """Verifica se o usuário pode acessar a ficha completa do paciente"""
    return user.is_authenticated and user.tipo_usuario in ['administrador_sistema', 'psicologo']


def can_access_assejus_full(user):
    """Verifica se o usuário pode acessar funcionalidades completas do ASEJUS"""
    return user.is_authenticated and user.tipo_usuario in ['administrador_sistema', 'advogado']


def can_access_psicologia_full(user):
    """Verifica se o usuário pode acessar funcionalidades completas da psicologia"""
    return user.is_authenticated and user.tipo_usuario in ['administrador_sistema', 'psicologo']


def can_edit_psicologia(user):
    """Verifica se o usuário pode editar dados da psicologia"""
    return user.is_authenticated and user.tipo_usuario == 'administrador_sistema'


def is_psicologo_own_patient(user, paciente):
    """Verifica se o psicólogo é responsável pelo paciente"""
    if not user.is_authenticated or user.tipo_usuario != 'psicologo':
        return False
    if hasattr(user, 'psicologo'):
        return paciente.psicologo_responsavel == user.psicologo
    return False
