from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from django_tables2 import SingleTableView

from .models import Psicologo, Paciente, Sessao, Prontuario, Evolucao, Documento, Agenda, PacientePsicologo
from .forms import (
    PsicologoForm, PacienteForm, SessaoForm, SessaoFromPacienteForm,
    ProntuarioForm, ProntuarioFromPacienteForm, EvolucaoForm, DocumentoForm, DocumentoFromPacienteForm, 
    AgendaForm, SessaoFilterForm, PacientePsicologoForm, GerenciarPsicologosForm
)
from associados.models import Associado
from core.permissions import (
    PsicologiaAccessMixin, PsicologiaFullAccessMixin,
    require_user_type, require_permission
)


# Dashboard
@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def dashboard(request):
    """Dashboard principal do módulo de psicologia"""
    # Filtrar dados baseado no tipo de usuário
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        # Psicólogo vê apenas seus próprios dados
        psicologo = request.user.psicologo
        total_pacientes = Paciente.objects.filter(
            psicologo_responsavel=psicologo,
            ativo=True
        ).count()
        total_sessoes = Sessao.objects.filter(psicologo=psicologo).count()
        sessoes_hoje = Sessao.objects.filter(
            psicologo=psicologo,
            data_hora__date=timezone.localtime(timezone.now()).date()
        ).count()
        pacientes_recentes = Paciente.objects.filter(
            psicologo_responsavel=psicologo,
            ativo=True
        ).order_by('-data_cadastro')[:10]
    else:
        # Administradores e atendentes veem todos os dados
        total_pacientes = Paciente.objects.filter(ativo=True).count()
        total_sessoes = Sessao.objects.count()
        sessoes_hoje = Sessao.objects.filter(
            data_hora__date=timezone.localtime(timezone.now()).date()
        ).count()
        pacientes_recentes = Paciente.objects.filter(ativo=True).order_by('-data_cadastro')[:10]
    
    context = {
        'total_psicologos': Psicologo.objects.filter(ativo=True).count(),
        'total_pacientes': total_pacientes,
        'total_sessoes': total_sessoes,
        'sessoes_hoje': sessoes_hoje,
        'pacientes_recentes': pacientes_recentes,
        'is_psicologo': request.user.tipo_usuario == 'psicologo',
    }
    return render(request, 'psicologia/dashboard.html', context)


@require_user_type(['psicologo'])
def psicologo_dashboard(request):
    """Dashboard específico para psicólogos - mostra suas sessões agendadas"""
    if not hasattr(request.user, 'psicologo'):
        messages.error(request, 'Usuário não possui perfil de psicólogo.')
        return redirect('psicologia:dashboard')
    
    psicologo = request.user.psicologo
    
    # Sessões de hoje - usar timezone local para evitar problemas de data
    hoje = timezone.localtime(timezone.now()).date()
    sessoes_hoje = Sessao.objects.filter(
        psicologo=psicologo,
        data_hora__date=hoje
    ).order_by('data_hora')
    
    # Próximas sessões (próximos 7 dias)
    proxima_semana = hoje + timedelta(days=7)
    proximas_sessoes = Sessao.objects.filter(
        psicologo=psicologo,
        data_hora__date__gte=hoje,
        data_hora__date__lte=proxima_semana
    ).exclude(data_hora__date=hoje).order_by('data_hora')
    
    # Sessões pendentes (agendadas e confirmadas)
    sessoes_pendentes = Sessao.objects.filter(
        psicologo=psicologo,
        status__in=['agendada', 'confirmada']
    ).order_by('data_hora')
    
    # Estatísticas
    total_pacientes = Paciente.objects.filter(
        psicologo_responsavel=psicologo,
        ativo=True
    ).count()
    
    total_sessoes_mes = Sessao.objects.filter(
        psicologo=psicologo,
        data_hora__month=hoje.month,
        data_hora__year=hoje.year
    ).count()
    
    # Pacientes recentes
    pacientes_recentes = Paciente.objects.filter(
        psicologo_responsavel=psicologo,
        ativo=True
    ).order_by('-data_cadastro')[:5]
    
    context = {
        'psicologo': psicologo,
        'sessoes_hoje': sessoes_hoje,
        'proximas_sessoes': proximas_sessoes,
        'sessoes_pendentes': sessoes_pendentes,
        'total_pacientes': total_pacientes,
        'total_sessoes_mes': total_sessoes_mes,
        'pacientes_recentes': pacientes_recentes,
        'hoje': hoje,
        'proxima_semana': proxima_semana,
    }
    return render(request, 'psicologia/psicologo_dashboard.html', context)


# Views para Psicólogos
class PsicologoListView(PsicologiaFullAccessMixin, ListView):
    model = Psicologo
    template_name = 'psicologia/psicologo_list.html'
    context_object_name = 'psicologos'
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        """Lista de psicólogos com filtros avançados"""
        
        # Verificar se é admin/superuser ou psicólogo específico
        is_admin_or_superuser = (request.user.tipo_usuario == 'administrador_sistema' or 
                                request.user.is_superuser)
        
        if not is_admin_or_superuser and request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Usuário psicólogo específico - mostrar apenas seu perfil
            try:
                # Buscar o psicólogo associado ao usuário
                psicologo = request.user.psicologo
                print(f"🔒 Usuário psicólogo {request.user.username} - Redirecionando para próprio perfil: {psicologo.nome_completo}")
                
                # Redirecionar para o perfil do psicólogo
                return redirect('psicologia:psicologo_detail', pk=psicologo.pk)
                
            except Exception as e:
                print(f"❌ Erro ao buscar psicólogo para usuário {request.user.username}: {e}")
                messages.error(request, f'Erro ao carregar perfil: {str(e)}')
                return redirect('psicologia:dashboard')
        else:
            # Admin/Superuser - mostrar lista completa
            print(f"🔍 Administrador/Superuser {request.user.username} - Mostrando lista completa de psicólogos")
            return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        # Admin/Superuser - mostrar todos os psicólogos
        queryset = Psicologo.objects.all()
        
        # Aplicar busca se fornecida
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_completo__icontains=search) |
                Q(crp__icontains=search) |
                Q(especialidade__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('nome_completo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verificar se é admin/superuser
        is_admin_or_superuser = (self.request.user.tipo_usuario == 'administrador_sistema' or 
                                self.request.user.is_superuser)
        
        # Adicionar estatísticas
        context['total_psicologos'] = Psicologo.objects.count()
        context['psicologos_ativos'] = Psicologo.objects.filter(ativo=True).count()
        context['is_admin_view'] = is_admin_or_superuser
        context['is_psicologo_user'] = self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo')
        context['can_create'] = self.request.user.tipo_usuario in ['administrador_sistema', 'atendente_psicologo']
        return context


class PsicologoDetailView(PsicologiaFullAccessMixin, DetailView):
    model = Psicologo
    template_name = 'psicologia/psicologo_detail.html'
    context_object_name = 'psicologo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        psicologo = self.get_object()
        
        # Filtrar dados baseado no tipo de usuário
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo vê apenas suas próprias sessões e pacientes
            if psicologo == self.request.user.psicologo:
                context['sessoes'] = Sessao.objects.filter(psicologo=psicologo).order_by('-data_hora')[:10]
                context['pacientes'] = Paciente.objects.filter(
                    psicologo_responsavel=psicologo
                ).distinct()
                context['can_edit_own'] = False  # Não pode editar sua própria ficha
            else:
                # Não pode ver ficha de outros psicólogos
                context['sessoes'] = []
                context['pacientes'] = []
                context['can_edit_own'] = False
        else:
            # Administradores veem tudo
            context['sessoes'] = Sessao.objects.filter(psicologo=psicologo).order_by('-data_hora')[:10]
            context['pacientes'] = Paciente.objects.filter(
                psicologo_responsavel=psicologo
            ).distinct()
            context['can_edit_own'] = True
        
        context['is_own_profile'] = self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo') and psicologo == self.request.user.psicologo
        return context


class PsicologoCreateView(PsicologiaFullAccessMixin, CreateView):
    model = Psicologo
    form_class = PsicologoForm
    template_name = 'psicologia/psicologo_form.html'
    success_url = reverse_lazy('psicologia:psicologo_list')
    
    def form_valid(self, form):
        # Criar um usuário automaticamente para o psicólogo
        Usuario = get_user_model()
        
        # Verificar se já existe um usuário com este CPF
        cpf = form.cleaned_data.get('cpf')
        email = form.cleaned_data.get('email')
        nome_completo = form.cleaned_data.get('nome_completo')
        
        if cpf:
            user, created = Usuario.objects.get_or_create(
                username=cpf,
                defaults={
                    'email': email or '',
                    'first_name': nome_completo.split()[0] if nome_completo else '',
                    'last_name': ' '.join(nome_completo.split()[1:]) if nome_completo and len(nome_completo.split()) > 1 else '',
                    'tipo_usuario': 'psicologo',
                    'is_active': True,
                }
            )
            
            if created:
                # Definir uma senha padrão (recomenda-se que o usuário mude na primeira vez)
                user.set_password('123456')  # Senha padrão
                user.save()
                
            # Associar o usuário ao psicólogo
            form.instance.user = user
        else:
            # Se não há CPF, criar um usuário temporário respeitando o limite de 14 caracteres
            if email and len(email) <= 14:
                username_temp = email
            else:
                # Usar nome truncado ou gerar ID único
                nome_base = nome_completo.replace(' ', '_').lower()[:8] if nome_completo else 'psic'
                username_temp = f"psic_{nome_base}"[:14]
                
                # Se ainda assim for muito longo, usar um ID único
                if len(username_temp) > 14:
                    import uuid
                    username_temp = f"psic_{str(uuid.uuid4())[:8]}"[:14]
            
            user, created = Usuario.objects.get_or_create(
                username=username_temp,
                defaults={
                    'email': email or '',
                    'first_name': nome_completo.split()[0] if nome_completo else '',
                    'last_name': ' '.join(nome_completo.split()[1:]) if nome_completo and len(nome_completo.split()) > 1 else '',
                    'tipo_usuario': 'psicologo',  # Corrigido para o tipo correto
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password('123456')
                user.save()
                
            form.instance.user = user
        
        messages.success(self.request, 'Psicólogo cadastrado com sucesso!')
        return super().form_valid(form)


class PsicologoUpdateView(PsicologiaFullAccessMixin, UpdateView):
    model = Psicologo
    form_class = PsicologoForm
    template_name = 'psicologia/psicologo_form.html'
    success_url = reverse_lazy('psicologia:psicologo_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Psicólogos não podem editar sua própria ficha
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            psicologo = self.get_object()
            if psicologo == request.user.psicologo:
                messages.error(request, 'Você não pode editar sua própria ficha de cadastro.')
                return redirect('psicologia:psicologo_detail', pk=psicologo.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Psicólogo atualizado com sucesso!')
        return super().form_valid(form)


class PsicologoDeleteView(PsicologiaFullAccessMixin, DeleteView):
    model = Psicologo
    template_name = 'psicologia/psicologo_confirm_delete.html'
    success_url = reverse_lazy('psicologia:psicologo_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Psicólogos não podem excluir sua própria ficha
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            psicologo = self.get_object()
            if psicologo == request.user.psicologo:
                messages.error(request, 'Você não pode excluir sua própria ficha de cadastro.')
                return redirect('psicologia:psicologo_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        psicologo = self.get_object()
        
        # Verificar se o psicólogo tem pacientes associados
        if psicologo.pacientes.exists():
            messages.error(
                request, 
                f'Não é possível excluir o psicólogo {psicologo.nome_completo} '
                f'pois ele possui {psicologo.pacientes.count} paciente(s) associado(s). '
                f'Transfira os pacientes para outro psicólogo antes de excluí-lo.'
            )
            return redirect('psicologia:psicologo_detail', pk=psicologo.pk)
        
        # Armazenar informações para mensagem
        nome = psicologo.nome_completo
        crp = psicologo.crp
        
        messages.success(
            request, 
            f'Psicólogo {nome} (CRP: {crp}) foi excluído com sucesso!'
        )
        
        return super().delete(request, *args, **kwargs)


# Views para Pacientes
class PacienteListView(PsicologiaAccessMixin, ListView):
    model = Paciente
    template_name = 'psicologia/paciente_list.html'
    context_object_name = 'pacientes'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo vê seus pacientes usando o sistema de psicólogo responsável
            psicologo = self.request.user.psicologo
            queryset = Paciente.objects.filter(
                psicologo_responsavel=psicologo,
                ativo=True
            ).select_related('associado')
        else:
            # Administradores e atendentes veem todos os pacientes
            queryset = Paciente.objects.select_related('associado').filter(ativo=True)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(associado__nome__icontains=search) |
                Q(associado__cpf__icontains=search)
            )
        
        # Não precisamos anotar tem_sessoes_realizadas pois é uma propriedade do modelo
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_psicologo'] = self.request.user.tipo_usuario == 'psicologo'
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            context['psicologo_usuario'] = self.request.user.psicologo
        
        context['is_superuser'] = self.request.user.is_superuser
        
        # Adicionar informação sobre o psicólogo atual para o template
        user_psicologo = None
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            user_psicologo = self.request.user.psicologo
        
        context['user_psicologo'] = user_psicologo
        
        # Adicionar lista de psicólogos para o modal de criação
        from .models import Psicologo
        context['psicologos'] = Psicologo.objects.filter(ativo=True).order_by('nome_completo')
        
        # Adicionar lista de associados e dependentes para o modal de criação
        from associados.models import Associado, Dependente
        context['associados'] = Associado.objects.filter(ativo=True).order_by('nome')
        context['dependentes'] = Dependente.objects.filter(ativo=True).order_by('nome')
        
        return context


class PacienteDetailView(PsicologiaAccessMixin, DetailView):
    model = Paciente
    template_name = 'psicologia/paciente_detail.html'
    context_object_name = 'paciente'
    
    def get_queryset(self):
        # Todos os usuários autorizados podem ver todos os pacientes
        return Paciente.objects.select_related('associado').all()
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se o usuário pode acessar a ficha do paciente"""
        paciente = self.get_object()
        
        # Verificar se o paciente tem sessões realizadas
        tem_sessoes_realizadas = Sessao.objects.filter(
            paciente=paciente,
            status='realizada'
        ).exists()
        
        # Se o paciente tem sessões realizadas, apenas o psicólogo responsável pode visualizar
        if tem_sessoes_realizadas:
            if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
                # Verificar se é o psicólogo responsável pelo paciente
                if paciente.psicologo_responsavel != request.user.psicologo:
                    messages.error(
                        request, 
                        f'Acesso restrito: Este paciente já teve sessões realizadas. '
                        f'Apenas o psicólogo responsável ({paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else "Não definido"}) '
                        f'pode acessar esta ficha.'
                    )
                    return redirect('psicologia:paciente_list')
            else:
                # TODOS os outros usuários (incluindo administradores) ficam restritos após primeira sessão realizada
                messages.error(
                    request, 
                    f'Acesso restrito: Este paciente já teve sessões realizadas. '
                    f'Apenas o psicólogo responsável ({paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else "Não definido"}) '
                    f'pode acessar esta ficha.'
                )
                return redirect('psicologia:paciente_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.get_object()
        
        # Filtrar sessões baseado no tipo de usuário
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo responsável atual vê TODOS os dados clínicos do paciente
            if paciente.psicologo_responsavel == self.request.user.psicologo:
                # Psicólogo responsável vê tudo para continuidade do tratamento
                context['sessoes'] = Sessao.objects.select_related('psicologo').filter(
                    paciente=paciente
                ).order_by('-data_hora')
                context['evolucoes'] = Evolucao.objects.select_related('sessao__psicologo').filter(
                    sessao__paciente=paciente
                ).order_by('-data_evolucao')
                context['documentos'] = Documento.objects.filter(
                    paciente=paciente
                ).order_by('-data_criacao')
            else:
                # Psicólogo não responsável vê apenas o que ele criou
                context['sessoes'] = Sessao.objects.select_related('psicologo').filter(
                    paciente=paciente, 
                    psicologo=self.request.user.psicologo
                ).order_by('-data_hora')
                context['evolucoes'] = Evolucao.objects.select_related('sessao__psicologo').filter(
                    sessao__paciente=paciente,
                    sessao__psicologo=self.request.user.psicologo
                ).order_by('-data_evolucao')
                context['documentos'] = Documento.objects.filter(
                    paciente=paciente,
                    psicologo=self.request.user.psicologo
                ).order_by('-data_criacao')
        else:
            # Administradores e atendentes só veem dados se não houver sessões realizadas
            # Se houver sessões realizadas, eles não conseguem acessar a view (bloqueados no dispatch)
            context['sessoes'] = Sessao.objects.select_related('psicologo').filter(paciente=paciente).order_by('-data_hora')
            context['evolucoes'] = Evolucao.objects.select_related('sessao__psicologo').filter(
                sessao__paciente=paciente
            ).order_by('-data_evolucao')
            context['documentos'] = Documento.objects.filter(paciente=paciente).order_by('-data_criacao')
        
        try:
            context['prontuario'] = Prontuario.objects.get(paciente=paciente)
            print(f"DEBUG: Prontuário encontrado para paciente {paciente.pk}: {context['prontuario'].pk}")
        except Prontuario.DoesNotExist:
            context['prontuario'] = None
            print(f"DEBUG: Nenhum prontuário encontrado para paciente {paciente.pk}")
        except Exception as e:
            context['prontuario'] = None
            print(f"DEBUG: Erro ao buscar prontuário para paciente {paciente.pk}: {e}")
        
        # Adicionar contexto para verificar permissões
        context['can_edit'] = self.request.user.tipo_usuario in ['administrador_sistema', 'atendente_psicologo']
        context['is_psicologo'] = self.request.user.tipo_usuario == 'psicologo'
        context['is_atendente'] = self.request.user.tipo_usuario == 'atendente_psicologo'
        
        # Verificar se o psicólogo atual pode gerenciar este paciente específico
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            context['can_manage_clinical'] = paciente.psicologo_responsavel == self.request.user.psicologo
            context['can_view_all'] = True
            context['is_my_patient'] = paciente.psicologo_responsavel == self.request.user.psicologo
        elif self.request.user.tipo_usuario == 'atendente_psicologo':
            context['can_manage_clinical'] = True
            context['can_view_all'] = True
            context['is_my_patient'] = False
        else:
            context['can_manage_clinical'] = False
            context['can_view_all'] = False
            context['is_my_patient'] = False
        
        # Adicionar lista de psicólogos para o modal de edição
        from .models import Psicologo
        context['psicologos'] = Psicologo.objects.filter(ativo=True).order_by('nome_completo')
        
        return context


class PacienteCreateView(PsicologiaAccessMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'psicologia/paciente_form.html'
    success_url = reverse_lazy('psicologia:paciente_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Administradores, psicólogos e atendentes podem criar pacientes
        if request.user.tipo_usuario not in ['administrador_sistema', 'psicologo', 'atendente_psicologo']:
            messages.error(request, 'Você não tem permissão para criar novos pacientes.')
            return redirect('psicologia:paciente_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Se for psicólogo, definir automaticamente como psicólogo responsável
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            form.instance.psicologo_responsavel = self.request.user.psicologo
        
        messages.success(self.request, 'Paciente cadastrado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Trata erros de validação do formulário"""
        # Capturar erros específicos e mostrar mensagens mais claras
        if 'associado' in form.errors:
            messages.error(
                self.request, 
                'Erro: Este associado já é paciente no sistema. '
                'Verifique se não está tentando cadastrar o mesmo associado duas vezes.'
            )
        else:
            messages.error(
                self.request, 
                'Erro ao cadastrar paciente. Verifique os dados informados.'
            )
        return super().form_invalid(form)


class PacienteCreateModalView(PsicologiaAccessMixin, View):
    """View para criar paciente via modal"""
    
    def dispatch(self, request, *args, **kwargs):
        # Administradores, psicólogos e atendentes podem criar pacientes
        if request.user.tipo_usuario not in ['administrador_sistema', 'psicologo', 'atendente_psicologo']:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para criar novos pacientes.'
            }, status=403)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            # Debug: log dos dados recebidos
            print(f"DEBUG: Dados POST recebidos: {dict(request.POST)}")
            print(f"DEBUG: Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
            print(f"DEBUG: X-Requested-With: {request.META.get('HTTP_X_REQUESTED_WITH', 'N/A')}")
            
            # Obter dados do formulário
            associado_id = request.POST.get('associado')
            psicologo_responsavel_id = request.POST.get('psicologo_responsavel')
            data_primeira_consulta = request.POST.get('data_primeira_consulta')
            observacoes_iniciais = request.POST.get('observacoes_iniciais')
            
            # Validar dados obrigatórios
            if not associado_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Associado é obrigatório.'
                }, status=400)
            
            # Buscar associado
            from associados.models import Associado
            try:
                associado = Associado.objects.get(pk=associado_id)
            except Associado.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Associado não encontrado.'
                }, status=404)
            
            # Verificar se já é paciente
            if Paciente.objects.filter(associado=associado).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'O associado {associado.nome} já é paciente no sistema.'
                }, status=400)
            
            # Criar paciente
            paciente = Paciente.objects.create(
                associado=associado,
                psicologo_responsavel_id=psicologo_responsavel_id if psicologo_responsavel_id else None,
                data_primeira_consulta=data_primeira_consulta if data_primeira_consulta else None,
                observacoes_iniciais=observacoes_iniciais or '',
                ativo=True
            )
            
            # Se for psicólogo, definir automaticamente como psicólogo responsável
            if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
                paciente.psicologo_responsavel = request.user.psicologo
                paciente.save()
            
            response_data = {
                'success': True,
                'message': f'Paciente {associado.nome} cadastrado com sucesso!',
                'paciente_id': paciente.pk,
                'redirect_url': reverse('psicologia:paciente_list')
            }
            print(f"DEBUG: Retornando JSON de sucesso: {response_data}")
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao cadastrar paciente: {str(e)}'
            }, status=500)


class PacienteUpdateView(PsicologiaAccessMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'psicologia/paciente_form.html'
    success_url = reverse_lazy('psicologia:paciente_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se o usuário pode editar a ficha do paciente"""
        paciente = self.get_object()
        
        # Verificar se o paciente tem sessões realizadas
        tem_sessoes_realizadas = Sessao.objects.filter(
            paciente=paciente,
            status='realizada'
        ).exists()
        
        # Se o paciente tem sessões realizadas, apenas o psicólogo responsável pode editar
        if tem_sessoes_realizadas:
            if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
                # Verificar se é o psicólogo responsável pelo paciente
                if paciente.psicologo_responsavel != request.user.psicologo:
                    messages.error(
                        request, 
                        f'Edição restrita: Este paciente já teve sessões realizadas. '
                        f'Apenas o psicólogo responsável ({paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else "Não definido"}) '
                        f'pode editar esta ficha.'
                    )
                    return redirect('psicologia:paciente_list')
            else:
                # TODOS os outros usuários (incluindo administradores) ficam restritos após primeira sessão realizada
                messages.error(
                    request, 
                    f'Edição restrita: Este paciente já teve sessões realizadas. '
                    f'Apenas o psicólogo responsável ({paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else "Não definido"}) '
                    f'pode editar esta ficha.'
                )
                return redirect('psicologia:paciente_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar seus próprios pacientes
            return Paciente.objects.filter(psicologo_responsavel=self.request.user.psicologo)
        elif self.request.user.tipo_usuario == 'atendente_psicologo':
            # Atendente pode editar todos os pacientes
            return Paciente.objects.all()
        # Administradores podem editar todos os pacientes
        return Paciente.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'Paciente atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Trata erros de validação do formulário"""
        # Capturar erros específicos e mostrar mensagens mais claras
        if 'associado' in form.errors:
            messages.error(
                self.request, 
                'Erro: Este associado já é paciente no sistema. '
                'Verifique se não está tentando alterar para um associado que já é paciente.'
            )
        else:
            messages.error(
                self.request, 
                'Erro ao atualizar paciente. Verifique os dados informados.'
            )
        return super().form_invalid(form)


class PacienteUpdateModalView(PsicologiaAccessMixin, View):
    """View para atualizar paciente via modal"""
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o paciente tem sessões realizadas
        paciente = get_object_or_404(Paciente, pk=kwargs['pk'])
        
        # Se o paciente tem sessões realizadas, apenas o psicólogo responsável pode editar
        if paciente.tem_sessoes_realizadas:
            if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
                if paciente.psicologo_responsavel != request.user.psicologo:
                    return JsonResponse({
                        'success': False,
                        'message': 'Após a primeira sessão, apenas o psicólogo responsável pode editar este paciente.'
                    }, status=403)
            else:
                # Administradores e atendentes não podem editar pacientes com sessões realizadas
                return JsonResponse({
                    'success': False,
                    'message': 'Após a primeira sessão, apenas o psicólogo responsável pode editar este paciente.'
                }, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            paciente = get_object_or_404(Paciente, pk=kwargs['pk'])
            
            # Obter dados do formulário
            associado_id = request.POST.get('associado')
            psicologo_responsavel_id = request.POST.get('psicologo_responsavel')
            data_primeira_consulta = request.POST.get('data_primeira_consulta')
            observacoes_iniciais = request.POST.get('observacoes_iniciais')
            
            # Validar dados obrigatórios
            if not associado_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Associado é obrigatório.'
                }, status=400)
            
            # Buscar associado
            from associados.models import Associado
            try:
                associado = Associado.objects.get(pk=associado_id)
            except Associado.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Associado não encontrado.'
                }, status=404)
            
            # Atualizar paciente
            paciente.associado = associado
            paciente.psicologo_responsavel_id = psicologo_responsavel_id if psicologo_responsavel_id else None
            paciente.data_primeira_consulta = data_primeira_consulta if data_primeira_consulta else None
            paciente.observacoes_iniciais = observacoes_iniciais
            paciente.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Paciente atualizado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar paciente: {str(e)}'
            }, status=500)


class PacienteTransferirModalView(PsicologiaAccessMixin, View):
    """View para transferir paciente via modal"""
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário pode transferir este paciente
        paciente = get_object_or_404(Paciente, pk=kwargs['pk'])
        
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            if paciente.psicologo_responsavel != request.user.psicologo:
                return JsonResponse({
                    'success': False,
                    'message': 'Você só pode transferir pacientes que você atende.'
                }, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Método GET para verificar se a view está acessível"""
        try:
            paciente = get_object_or_404(Paciente, pk=kwargs['pk'])
            return JsonResponse({
                'success': True,
                'message': 'View de transferência acessível',
                'paciente_id': paciente.pk,
                'paciente_nome': paciente.associado.nome if paciente.associado else 'N/A'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao acessar paciente: {str(e)}'
            }, status=400)
    
    def post(self, request, *args, **kwargs):
        try:
            paciente = get_object_or_404(Paciente, pk=kwargs['pk'])
            
            # Obter dados do formulário
            novo_psicologo_id = request.POST.get('novo_psicologo')
            motivo_transferencia = request.POST.get('motivo_transferencia', '')
            observacoes = request.POST.get('observacoes', '')
            
            if not novo_psicologo_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Selecione um psicólogo para transferir o paciente.'
                }, status=400)
            
            # Validar motivo da transferência
            if not motivo_transferencia or len(motivo_transferencia.strip()) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'O motivo da transferência deve ter pelo menos 3 caracteres.'
                }, status=400)
            
            try:
                novo_psicologo = Psicologo.objects.get(pk=novo_psicologo_id, ativo=True)
            except Psicologo.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Psicólogo não encontrado.'
                }, status=404)
            
            # Realizar a transferência
            sucesso, mensagem = paciente.transferir_para_psicologo(
                novo_psicologo, 
                motivo_transferencia, 
                observacoes
            )
            
            if sucesso:
                return JsonResponse({
                    'success': True,
                    'message': mensagem
                })
            else:
                # Melhorar a mensagem para casos específicos
                if "já está sendo atendido por este psicólogo" in mensagem:
                    mensagem = f"Este paciente já está sendo atendido por {novo_psicologo.nome_completo}. Selecione um psicólogo diferente."
                return JsonResponse({
                    'success': False,
                    'message': mensagem
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao transferir paciente: {str(e)}'
            }, status=500)


class PacienteDeleteView(PsicologiaAccessMixin, DeleteView):
    """View para excluir um paciente"""
    model = Paciente
    template_name = 'psicologia/paciente_confirm_delete.html'
    success_url = reverse_lazy('psicologia:paciente_list')
    
    def dispatch(self, request, *args, **kwargs):
        paciente = self.get_object()
        
        # Verificar se o paciente pode ser excluído
        if paciente.tem_sessoes_realizadas and request.user.tipo_usuario != 'administrador_sistema':
            messages.error(request, 'Pacientes com sessões realizadas só podem ser excluídos por administradores do sistema.')
            return redirect('psicologia:paciente_detail', pk=paciente.pk)
        
        # Verificar se o usuário pode excluir este paciente
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            if paciente.psicologo_responsavel != request.user.psicologo:
                messages.error(request, 'Você só pode excluir pacientes que você atende.')
                return redirect('psicologia:paciente_detail', pk=paciente.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        paciente = self.get_object()
        
        # Verificar novamente antes de excluir
        if paciente.tem_sessoes_realizadas and request.user.tipo_usuario != 'administrador_sistema':
            messages.error(request, 'Pacientes com sessões realizadas só podem ser excluídos por administradores do sistema.')
            return redirect('psicologia:paciente_detail', pk=paciente.pk)
        
        # Excluir o paciente
        paciente.delete()
        messages.success(request, f'Paciente "{paciente.associado.nome if paciente.associado else "N/A"}" excluído com sucesso.')
        
        return redirect(self.success_url)


@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def remover_psicologo_paciente(request, paciente_id):
    """View para remover o psicólogo responsável por um paciente"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar se o usuário pode remover o psicólogo deste paciente
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        if paciente.psicologo_responsavel != request.user.psicologo:
            messages.error(request, 'Você só pode remover psicólogos de pacientes que você atende.')
            return redirect('psicologia:paciente_detail', pk=paciente_id)
    
    if request.method == 'POST':
        motivo_encerramento = request.POST.get('motivo_encerramento', '')
        
        # Realizar a remoção
        sucesso, mensagem = paciente.remover_psicologo(
            paciente.psicologo_responsavel, 
            motivo_encerramento
        )
        
        if sucesso:
            messages.success(request, mensagem)
            return redirect('psicologia:paciente_detail', pk=paciente_id)
        else:
            messages.error(request, mensagem)
    
    context = {
        'paciente': paciente,
    }
    
    return render(request, 'psicologia/remover_psicologo_paciente.html', context)


@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def finalizar_sessao(request, paciente_id, pk):
    """View para finalizar/atualizar o status de uma sessão"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    sessao = get_object_or_404(Sessao, pk=pk, paciente=paciente)
    
    # Verificar se o usuário pode finalizar esta sessão
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        if sessao.psicologo != request.user.psicologo and paciente.psicologo_responsavel != request.user.psicologo:
            messages.error(request, 'Você só pode finalizar sessões de pacientes que você atende.')
            return redirect('psicologia:paciente_detail', pk=paciente_id)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        observacoes = request.POST.get('observacoes', '')
        
        if novo_status:
            # Atualizar o status da sessão
            sessao.status = novo_status
            if observacoes:
                sessao.observacoes = observacoes
            sessao.save()
            
            # Mensagem de sucesso baseada no status
            if novo_status == 'realizada':
                messages.success(request, 'Sessão marcada como realizada com sucesso!')
            elif novo_status == 'cancelada':
                messages.success(request, 'Sessão cancelada com sucesso!')
            elif novo_status == 'remarcada':
                messages.success(request, 'Sessão marcada como remarcada!')
            elif novo_status == 'ausente':
                messages.success(request, 'Sessão marcada como ausente!')
            else:
                messages.success(request, f'Status da sessão atualizado para "{sessao.get_status_display()}"!')
            
            return redirect('psicologia:paciente_detail', pk=paciente_id)
        else:
            messages.error(request, 'Selecione um status válido para a sessão.')
    
    # Se não for POST, redirecionar para a ficha do paciente
    return redirect('psicologia:paciente_detail', pk=paciente_id)


# Views para Sessões
class SessaoListView(PsicologiaAccessMixin, ListView):
    model = Sessao
    template_name = 'psicologia/sessao_list.html'
    context_object_name = 'sessoes'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo vê apenas suas próprias sessões
            queryset = Sessao.objects.filter(psicologo=self.request.user.psicologo)
        else:
            # Administradores e atendentes veem todas as sessões
            queryset = Sessao.objects.all()
        
        # Aplicar filtros se fornecidos
        try:
            form = SessaoFilterForm(self.request.GET)
            if form.is_valid():
                if form.cleaned_data.get('paciente'):
                    queryset = queryset.filter(paciente=form.cleaned_data['paciente'])
                if form.cleaned_data.get('psicologo'):
                    queryset = queryset.filter(psicologo=form.cleaned_data['psicologo'])
                if form.cleaned_data.get('status'):
                    queryset = queryset.filter(status=form.cleaned_data['status'])
                if form.cleaned_data.get('tipo_sessao'):
                    queryset = queryset.filter(tipo_sessao=form.cleaned_data['tipo_sessao'])
                if form.cleaned_data.get('data_inicio'):
                    queryset = queryset.filter(data_hora__date__gte=form.cleaned_data['data_inicio'])
                if form.cleaned_data.get('data_fim'):
                    queryset = queryset.filter(data_hora__date__lte=form.cleaned_data['data_fim'])
        except Exception as e:
            # Em caso de erro no formulário, apenas retornar o queryset básico
            pass
        
        return queryset.order_by('-data_hora')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = SessaoFilterForm(self.request.GET)
        return context


class SessaoDetailView(PsicologiaAccessMixin, DetailView):
    model = Sessao
    template_name = 'psicologia/sessao_detail.html'
    context_object_name = 'sessao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessao = self.get_object()
        context['evolucoes'] = Evolucao.objects.filter(sessao=sessao).order_by('-data_evolucao')
        return context


class SessaoCreateView(PsicologiaAccessMixin, CreateView):
    model = Sessao
    form_class = SessaoForm
    template_name = 'psicologia/sessao_form.html'
    success_url = reverse_lazy('psicologia:sessao_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Psicólogos podem criar sessões para qualquer paciente
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            pass  # Permitir criação
        # Atendentes podem criar sessões para qualquer paciente
        elif request.user.tipo_usuario == 'atendente_psicologo':
            pass  # Permitir criação
        # Administradores podem criar sessões para qualquer paciente
        elif request.user.tipo_usuario == 'administrador_sistema':
            pass  # Permitir criação
        else:
            messages.error(request, 'Você não tem permissão para criar sessões.')
            return redirect('psicologia:sessao_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Se for psicólogo, definir automaticamente o psicólogo da sessão
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            form.instance.psicologo = self.request.user.psicologo
        
        # Garantir que o status padrão seja 'agendada'
        if not form.instance.status:
            form.instance.status = 'agendada'
        
        messages.success(self.request, 'Sessão agendada com sucesso!')
        return super().form_valid(form)


class SessaoFromPacienteCreateView(PsicologiaAccessMixin, CreateView):
    """View para criar sessão a partir da ficha do paciente"""
    model = Sessao
    form_class = SessaoFromPacienteForm
    template_name = 'psicologia/sessao_from_paciente_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs.get('paciente_id')
        context['paciente'] = get_object_or_404(Paciente, pk=paciente_id)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário pode criar sessão para este paciente
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogos podem criar sessões para:
            # 1. Pacientes que eles atendem (são responsáveis)
            # 2. Pacientes sem psicólogo responsável
            # 3. Pacientes que eles já atenderam anteriormente
            psicologo = request.user.psicologo
            
            pode_criar = (
                paciente.psicologo_responsavel == psicologo or  # É o responsável atual
                not paciente.psicologo_responsavel or  # Paciente sem psicólogo
                paciente.psicologos.filter(id=psicologo.id).exists()  # Já atendeu o paciente
            )
            
            if not pode_criar:
                messages.error(request, 'Você não pode criar sessão para este paciente.')
                return redirect('psicologia:paciente_detail', pk=paciente_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        # Preencher automaticamente paciente
        form.instance.paciente = paciente
        
        # Definir psicólogo da sessão
        if hasattr(self.request.user, 'psicologo'):
            # Se o usuário logado é psicólogo, usar ele mesmo
            form.instance.psicologo = self.request.user.psicologo
        elif paciente.psicologo_responsavel:
            # Se não, usar o psicólogo responsável pelo paciente
            form.instance.psicologo = paciente.psicologo_responsavel
        else:
            messages.error(self.request, 'É necessário definir um psicólogo responsável para o paciente.')
            return self.form_invalid(form)
        
        # Garantir que a sessão tenha valores padrão se não fornecidos
        if not form.instance.status:
            form.instance.status = 'agendada'
        if not form.instance.tipo_sessao:
            form.instance.tipo_sessao = 'terapia'
        if not form.instance.duracao:
            form.instance.duracao = 50
        
        try:
            messages.success(self.request, 'Sessão agendada com sucesso!')
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao agendar sessão: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        return reverse_lazy('psicologia:paciente_detail', kwargs={'pk': paciente_id})


class SessaoUpdateView(PsicologiaAccessMixin, UpdateView):
    model = Sessao
    form_class = SessaoForm
    template_name = 'psicologia/sessao_form.html'
    success_url = reverse_lazy('psicologia:sessao_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar suas próprias sessões
            return Sessao.objects.filter(psicologo=self.request.user.psicologo)
        return Sessao.objects.all()
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se a sessão pode ser editada"""
        sessao = self.get_object()
        if sessao.status == 'realizada':
            messages.error(request, 'Não é possível editar uma sessão que já foi realizada.')
            return redirect('psicologia:sessao_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Sessão atualizada com sucesso!')
        return super().form_valid(form)


class SessaoDeleteView(PsicologiaAccessMixin, DeleteView):
    model = Sessao
    template_name = 'psicologia/sessao_confirm_delete.html'
    success_url = reverse_lazy('psicologia:sessao_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode excluir suas próprias sessões
            return Sessao.objects.filter(psicologo=self.request.user.psicologo)
        return Sessao.objects.all()
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se a sessão pode ser excluída"""
        sessao = self.get_object()
        if sessao.status == 'realizada':
            messages.error(request, 'Não é possível excluir uma sessão que já foi realizada.')
            return redirect('psicologia:sessao_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Sessão excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Prontuários
class ProntuarioListView(PsicologiaFullAccessMixin, ListView):
    model = Prontuario
    template_name = 'psicologia/prontuario_list.html'
    context_object_name = 'prontuarios'
    paginate_by = 20


class ProntuarioDetailView(PsicologiaFullAccessMixin, DetailView):
    model = Prontuario
    template_name = 'psicologia/prontuario_detail.html'
    context_object_name = 'prontuario'


class ProntuarioCreateView(PsicologiaFullAccessMixin, CreateView):
    model = Prontuario
    form_class = ProntuarioForm
    template_name = 'psicologia/prontuario_form.html'
    success_url = reverse_lazy('psicologia:prontuario_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Prontuário criado com sucesso!')
        return super().form_valid(form)


class ProntuarioFromPacienteCreateView(PsicologiaFullAccessMixin, CreateView):
    """View para criar prontuário a partir da ficha do paciente"""
    model = Prontuario
    form_class = ProntuarioFromPacienteForm
    template_name = 'psicologia/prontuario_from_paciente_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs.get('paciente_id')
        context['paciente'] = get_object_or_404(Paciente, pk=paciente_id)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário pode criar prontuário para este paciente
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogos podem criar prontuários para pacientes que já atenderam
            if not paciente.pode_ser_atendido_por(request.user.psicologo):
                messages.error(request, 'Você não pode criar prontuário para este paciente.')
                return redirect('psicologia:paciente_detail', pk=paciente_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        # Preencher automaticamente o paciente
        form.instance.paciente = paciente
        
        messages.success(self.request, 'Prontuário criado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        return reverse_lazy('psicologia:paciente_detail', kwargs={'pk': paciente_id})


class ProntuarioUpdateView(PsicologiaFullAccessMixin, UpdateView):
    model = Prontuario
    form_class = ProntuarioForm
    template_name = 'psicologia/prontuario_form.html'
    success_url = reverse_lazy('psicologia:prontuario_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar prontuários dos seus pacientes
            return Prontuario.objects.filter(paciente__psicologo_responsavel=self.request.user.psicologo)
        return Prontuario.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'Prontuário atualizado com sucesso!')
        return super().form_valid(form)


class ProntuarioDeleteView(PsicologiaFullAccessMixin, DeleteView):
    model = Prontuario
    template_name = 'psicologia/prontuario_confirm_delete.html'
    success_url = reverse_lazy('psicologia:prontuario_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode excluir prontuários dos seus pacientes
            return Prontuario.objects.filter(paciente__psicologo_responsavel=self.request.user.psicologo)
        return Prontuario.objects.all()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Prontuário excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Evoluções
class EvolucaoListView(PsicologiaFullAccessMixin, ListView):
    model = Evolucao
    template_name = 'psicologia/evolucao_list.html'
    context_object_name = 'evolucoes'
    paginate_by = 20


class EvolucaoDetailView(PsicologiaFullAccessMixin, DetailView):
    model = Evolucao
    template_name = 'psicologia/evolucao_detail.html'
    context_object_name = 'evolucao'


class EvolucaoCreateView(PsicologiaFullAccessMixin, CreateView):
    model = Evolucao
    form_class = EvolucaoForm
    template_name = 'psicologia/evolucao_form.html'
    success_url = reverse_lazy('psicologia:evolucao_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Psicólogos podem criar evoluções para sessões de pacientes que já atenderam
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            sessao_id = request.POST.get('sessao')
            if sessao_id:
                try:
                    sessao = Sessao.objects.get(pk=sessao_id)
                    # Verificar se o psicólogo pode atender este paciente
                    if not sessao.paciente.pode_ser_atendido_por(request.user.psicologo):
                        messages.error(request, 'Você não pode criar evoluções para este paciente.')
                        return redirect('psicologia:evolucao_list')
                except Sessao.DoesNotExist:
                    messages.error(request, 'Sessão não encontrada.')
                    return redirect('psicologia:evolucao_list')
        # Atendentes podem criar evoluções para qualquer sessão
        elif request.user.tipo_usuario == 'atendente_psicologo':
            pass  # Permitir criação
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Evolução registrada com sucesso!')
        return super().form_valid(form)


class EvolucaoFromPacienteCreateView(PsicologiaAccessMixin, CreateView):
    """View para criar evolução a partir da ficha do paciente"""
    model = Evolucao
    form_class = EvolucaoForm
    template_name = 'psicologia/evolucao_from_paciente_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs.get('paciente_id')
        context['paciente'] = get_object_or_404(Paciente, pk=paciente_id)
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        # Verificar se o campo sessao existe no formulário
        if 'sessao' not in form.fields:
            return form
        
        # Filtrar sessões baseado no tipo de usuário
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogos podem ver sessões de pacientes que eles atendem
            psicologo = self.request.user.psicologo
            if paciente.psicologo_responsavel == psicologo:
                # Psicólogo responsável pelo paciente pode ver todas as sessões
                form.fields['sessao'].queryset = Sessao.objects.filter(paciente_id=paciente_id)
            else:
                # Psicólogo não responsável só pode ver suas próprias sessões com este paciente
                form.fields['sessao'].queryset = Sessao.objects.filter(
                    paciente_id=paciente_id,
                    psicologo=psicologo
                )
        else:
            # Administradores e atendentes veem todas as sessões do paciente
            form.fields['sessao'].queryset = Sessao.objects.filter(paciente_id=paciente_id)
        
        return form
    
    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        return reverse_lazy('psicologia:paciente_detail', kwargs={'pk': paciente_id})
    
    def form_valid(self, form):
        # Verificar se a sessão foi selecionada
        if not form.cleaned_data.get('sessao'):
            messages.error(self.request, 'É necessário selecionar uma sessão para criar a evolução.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Evolução registrada com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


class EvolucaoUpdateView(PsicologiaFullAccessMixin, UpdateView):
    model = Evolucao
    form_class = EvolucaoForm
    template_name = 'psicologia/evolucao_form.html'
    success_url = reverse_lazy('psicologia:evolucao_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar suas próprias evoluções
            return Evolucao.objects.filter(sessao__psicologo=self.request.user.psicologo)
        return Evolucao.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'Evolução atualizada com sucesso!')
        return super().form_valid(form)


class EvolucaoDeleteView(PsicologiaFullAccessMixin, DeleteView):
    model = Evolucao
    template_name = 'psicologia/evolucao_confirm_delete.html'
    success_url = reverse_lazy('psicologia:evolucao_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode excluir suas próprias evoluções
            return Evolucao.objects.filter(sessao__psicologo=self.request.user.psicologo)
        return Evolucao.objects.all()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Evolução excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Documentos
class DocumentoListView(PsicologiaAccessMixin, ListView):
    model = Documento
    template_name = 'psicologia/documento_list.html'
    context_object_name = 'documentos'
    paginate_by = 20


class DocumentoDetailView(PsicologiaAccessMixin, DetailView):
    model = Documento
    template_name = 'psicologia/documento_detail.html'
    context_object_name = 'documento'


class DocumentoCreateView(PsicologiaAccessMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'psicologia/documento_form.html'
    success_url = reverse_lazy('psicologia:documento_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Documento criado com sucesso!')
        return super().form_valid(form)


class DocumentoFromPacienteCreateView(PsicologiaAccessMixin, CreateView):
    """View para criar documento a partir da ficha do paciente"""
    model = Documento
    form_class = DocumentoFromPacienteForm
    template_name = 'psicologia/documento_from_paciente_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs.get('paciente_id')
        context['paciente'] = get_object_or_404(Paciente, pk=paciente_id)
        print(f"DEBUG: Formulário de documento - Paciente: {context['paciente']}")
        print(f"DEBUG: Formulário de documento - Form: {context.get('form', 'Não encontrado')}")
        return context
    

    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário pode criar documento para este paciente
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogos podem criar documentos para pacientes que já atenderam
            if not paciente.pode_ser_atendido_por(request.user.psicologo):
                messages.error(request, 'Você não pode criar documento para este paciente.')
                return redirect('psicologia:paciente_detail', pk=paciente_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        paciente_id = self.kwargs.get('paciente_id')
        paciente = get_object_or_404(Paciente, pk=paciente_id)
        
        # Preencher automaticamente paciente
        form.instance.paciente = paciente
        
        # Definir psicólogo do documento
        if hasattr(self.request.user, 'psicologo'):
            # Se o usuário logado é psicólogo, usar ele mesmo
            form.instance.psicologo = self.request.user.psicologo
        elif paciente.psicologo_responsavel:
            # Se não, usar o psicólogo responsável pelo paciente
            form.instance.psicologo = paciente.psicologo_responsavel
        else:
            # Para atendentes, permitir criar documento sem psicólogo específico
            if self.request.user.tipo_usuario != 'atendente_psicologo':
                messages.error(self.request, 'É necessário definir um psicólogo responsável para o paciente.')
                return self.form_invalid(form)
        
        messages.success(self.request, 'Documento criado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        return reverse_lazy('psicologia:paciente_detail', kwargs={'pk': paciente_id})


class DocumentoUpdateView(PsicologiaAccessMixin, UpdateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'psicologia/documento_form.html'
    success_url = reverse_lazy('psicologia:documento_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar seus próprios documentos
            return Documento.objects.filter(psicologo=self.request.user.psicologo)
        return Documento.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'Documento atualizado com sucesso!')
        return super().form_valid(form)


class DocumentoDeleteView(PsicologiaAccessMixin, DeleteView):
    model = Documento
    template_name = 'psicologia/documento_confirm_delete.html'
    success_url = reverse_lazy('psicologia:documento_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode excluir seus próprios documentos
            return Documento.objects.filter(psicologo=self.request.user.psicologo)
        return Documento.objects.all()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Documento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Agenda
class AgendaListView(PsicologiaAccessMixin, ListView):
    model = Agenda
    template_name = 'psicologia/agenda_list.html'
    context_object_name = 'agendas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Agenda.objects.all().order_by('data', 'hora_inicio')
        
        # Filtros
        psicologo = self.request.GET.get('psicologo')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        disponivel = self.request.GET.get('disponivel')
        
        if psicologo:
            queryset = queryset.filter(psicologo_id=psicologo)
        
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        
        if disponivel in ['0', '1']:
            queryset = queryset.filter(disponivel=bool(int(disponivel)))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['psicologos'] = Psicologo.objects.filter(ativo=True).order_by('nome_completo')
        return context


class AgendaDetailView(PsicologiaAccessMixin, DetailView):
    model = Agenda
    template_name = 'psicologia/agenda_detail.html'
    context_object_name = 'agenda'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agenda = self.get_object()
        
        # Sessões agendadas neste horário
        context['sessoes'] = Sessao.objects.filter(
            psicologo=agenda.psicologo,
            data_hora__date=agenda.data,
            data_hora__time__gte=agenda.hora_inicio,
            data_hora__time__lte=agenda.hora_fim
        ).order_by('data_hora')
        
        # Estatísticas do psicólogo
        context['total_sessoes'] = Sessao.objects.filter(psicologo=agenda.psicologo).count()
        context['total_pacientes'] = Paciente.objects.filter(psicologo_responsavel=agenda.psicologo).count()
        
        return context


class AgendaCreateView(PsicologiaAccessMixin, CreateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'psicologia/agenda_form.html'
    success_url = reverse_lazy('psicologia:agenda_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        # Se for psicólogo, definir automaticamente o psicólogo da agenda
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            form.instance.psicologo = self.request.user.psicologo
        messages.success(self.request, 'Horário agendado com sucesso!')
        return super().form_valid(form)


class AgendaUpdateView(PsicologiaAccessMixin, UpdateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'psicologia/agenda_form.html'
    success_url = reverse_lazy('psicologia:agenda_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode editar sua própria agenda
            return Agenda.objects.filter(psicologo=self.request.user.psicologo)
        return Agenda.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'Horário atualizado com sucesso!')
        return super().form_valid(form)


class AgendaDeleteView(PsicologiaAccessMixin, DeleteView):
    model = Agenda
    template_name = 'psicologia/agenda_confirm_delete.html'
    success_url = reverse_lazy('psicologia:agenda_list')
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            # Psicólogo só pode excluir sua própria agenda
            return Agenda.objects.filter(psicologo=self.request.user.psicologo)
        return Agenda.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agenda = self.get_object()
        
        # Sessões agendadas neste horário para mostrar aviso
        context['sessoes'] = Sessao.objects.filter(
            psicologo=agenda.psicologo,
            data_hora__date=agenda.data,
            data_hora__time__gte=agenda.hora_inicio,
            data_hora__time__lte=agenda.hora_fim
        ).order_by('data_hora')
        
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Horário excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views auxiliares
@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def buscar_associados(request):
    """Busca associados para cadastro de pacientes"""
    termo = request.GET.get('termo', '')
    if termo:
        associados = Associado.objects.filter(
            Q(nome__icontains=termo) | Q(cpf__icontains=termo)
        )[:10]
        data = [{'id': a.id, 'nome': a.nome, 'cpf': a.cpf} for a in associados]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def verificar_disponibilidade(request):
    """Verifica disponibilidade de horário para agendamento"""
    psicologo_id = request.GET.get('psicologo')
    data = request.GET.get('data')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')
    
    if psicologo_id and data and hora_inicio and hora_fim:
        # Verifica se já existe sessão agendada neste horário
        sessao_existe = Sessao.objects.filter(
            psicologo_id=psicologo_id,
            data_hora__date=data,
            data_hora__time__range=(hora_inicio, hora_fim)
        ).exists()
        
        # Verifica se o horário está disponível na agenda
        agenda_disponivel = Agenda.objects.filter(
            psicologo_id=psicologo_id,
            data=data,
            hora_inicio__lte=hora_inicio,
            hora_fim__gte=hora_fim,
            disponivel=True
        ).exists()
        
        return JsonResponse({
            'disponivel': not sessao_existe and agenda_disponivel,
            'sessao_existe': sessao_existe,
            'agenda_disponivel': agenda_disponivel
        })
    
    return JsonResponse({'disponivel': False})


# Views para gerenciamento dentro da ficha do paciente

class SessaoFromPacienteUpdateView(PsicologiaAccessMixin, UpdateView):
    """View para editar sessão a partir da ficha do paciente"""
    model = Sessao
    form_class = SessaoFromPacienteForm
    template_name = 'psicologia/sessao_from_paciente_form.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se a sessão pode ser editada"""
        sessao = self.get_object()
        if sessao.status == 'realizada':
            messages.error(request, 'Não é possível editar uma sessão que já foi realizada.')
            return redirect('psicologia:paciente_detail', pk=self.kwargs['paciente_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Sessão atualizada com sucesso!')
        return super().form_valid(form)


class SessaoFromPacienteDeleteView(PsicologiaAccessMixin, DeleteView):
    """View para excluir sessão a partir da ficha do paciente"""
    model = Sessao
    template_name = 'psicologia/sessao_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se a sessão pode ser excluída"""
        sessao = self.get_object()
        if sessao.status == 'realizada':
            messages.error(request, 'Não é possível excluir uma sessão que já foi realizada.')
            return redirect('psicologia:paciente_detail', pk=self.kwargs['paciente_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Sessão excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class ProntuarioFromPacienteUpdateView(PsicologiaAccessMixin, UpdateView):
    """View para editar prontuário a partir da ficha do paciente"""
    model = Prontuario
    form_class = ProntuarioFromPacienteForm
    template_name = 'psicologia/prontuario_from_paciente_form.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Prontuário atualizado com sucesso!')
        return super().form_valid(form)


class ProntuarioFromPacienteDeleteView(PsicologiaAccessMixin, DeleteView):
    """View para excluir prontuário a partir da ficha do paciente"""
    model = Prontuario
    template_name = 'psicologia/prontuario_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Prontuário excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class EvolucaoFromPacienteUpdateView(PsicologiaAccessMixin, UpdateView):
    """View para editar evolução a partir da ficha do paciente"""
    model = Evolucao
    form_class = EvolucaoForm
    template_name = 'psicologia/evolucao_from_paciente_form.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Evolução atualizada com sucesso!')
        return super().form_valid(form)


class EvolucaoFromPacienteDeleteView(PsicologiaAccessMixin, DeleteView):
    """View para excluir evolução a partir da ficha do paciente"""
    model = Evolucao
    template_name = 'psicologia/evolucao_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Evolução excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class DocumentoFromPacienteUpdateView(PsicologiaAccessMixin, UpdateView):
    """View para editar documento a partir da ficha do paciente"""
    model = Documento
    form_class = DocumentoFromPacienteForm
    template_name = 'psicologia/documento_from_paciente_form.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Documento atualizado com sucesso!')
        return super().form_valid(form)


class DocumentoFromPacienteDeleteView(PsicologiaAccessMixin, DeleteView):
    """View para excluir documento a partir da ficha do paciente"""
    model = Documento
    template_name = 'psicologia/documento_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('psicologia:paciente_detail', kwargs={'pk': self.kwargs['paciente_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Documento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para transferência de pacientes
@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def transferir_paciente(request, paciente_id):
    """View para transferir um paciente para outro psicólogo"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar se o usuário pode transferir este paciente
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        if paciente.psicologo_responsavel != request.user.psicologo:
            messages.error(request, 'Você só pode transferir pacientes que você atende.')
            return redirect('psicologia:paciente_detail', pk=paciente_id)
    
    if request.method == 'POST':
        novo_psicologo_id = request.POST.get('novo_psicologo')
        motivo_transferencia = request.POST.get('motivo_transferencia', '')
        observacoes = request.POST.get('observacoes', '')
        
        if novo_psicologo_id:
            try:
                novo_psicologo = Psicologo.objects.get(pk=novo_psicologo_id, ativo=True)
                
                # Realizar a transferência
                sucesso, mensagem = paciente.transferir_para_psicologo(
                    novo_psicologo, 
                    motivo_transferencia, 
                    observacoes
                )
                
                if sucesso:
                    messages.success(request, mensagem)
                    return redirect('psicologia:paciente_detail', pk=paciente_id)
                else:
                    messages.error(request, mensagem)
            except Psicologo.DoesNotExist:
                messages.error(request, 'Psicólogo não encontrado.')
        else:
            messages.error(request, 'Selecione um psicólogo para transferir o paciente.')
    
    # Listar psicólogos disponíveis (excluindo o atual)
    psicologos_disponiveis = Psicologo.objects.filter(ativo=True).exclude(
        id=paciente.psicologo_responsavel.id if paciente.psicologo_responsavel else 0
    ).order_by('nome_completo')
    
    context = {
        'paciente': paciente,
        'psicologos_disponiveis': psicologos_disponiveis,
    }
    
    return render(request, 'psicologia/transferir_paciente.html', context)


@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def remover_psicologo_paciente(request, paciente_id):
    """View para remover o psicólogo responsável por um paciente"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Verificar se o usuário pode remover o psicólogo deste paciente
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        if paciente.psicologo_responsavel != request.user.psicologo:
            messages.error(request, 'Você só pode remover psicólogos de pacientes que você atende.')
            return redirect('psicologia:paciente_detail', pk=paciente_id)
    
    if request.method == 'POST':
        motivo_encerramento = request.POST.get('motivo_encerramento', '')
        
        # Realizar a remoção
        sucesso, mensagem = paciente.remover_psicologo(
            paciente.psicologo_responsavel, 
            motivo_encerramento
        )
        
        if sucesso:
            messages.success(request, mensagem)
            return redirect('psicologia:paciente_detail', pk=paciente_id)
        else:
            messages.error(request, mensagem)
    
    context = {
        'paciente': paciente,
    }
    
    return render(request, 'psicologia/remover_psicologo_paciente.html', context)


@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def finalizar_sessao(request, paciente_id, pk):
    """View para finalizar/atualizar o status de uma sessão"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    sessao = get_object_or_404(Sessao, pk=pk, paciente=paciente)
    
    # Verificar se o usuário pode finalizar esta sessão
    if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
        if sessao.psicologo != request.user.psicologo and paciente.psicologo_responsavel != request.user.psicologo:
            messages.error(request, 'Você só pode finalizar sessões de pacientes que você atende.')
            return redirect('psicologia:paciente_detail', pk=paciente_id)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        observacoes = request.POST.get('observacoes', '')
        
        if novo_status:
            # Atualizar o status da sessão
            sessao.status = novo_status
            if observacoes:
                sessao.observacoes = observacoes
            sessao.save()
            
            # Mensagem de sucesso baseada no status
            if novo_status == 'realizada':
                messages.success(request, 'Sessão marcada como realizada com sucesso!')
            elif novo_status == 'cancelada':
                messages.success(request, 'Sessão cancelada com sucesso!')
            elif novo_status == 'remarcada':
                messages.success(request, 'Sessão marcada como remarcada!')
            elif novo_status == 'ausente':
                messages.success(request, 'Sessão marcada como ausente!')
            else:
                messages.success(request, f'Status da sessão atualizado para "{sessao.get_status_display()}"!')
            
            return redirect('psicologia:paciente_detail', pk=paciente_id)
        else:
            messages.error(request, 'Selecione um status válido para a sessão.')
    
    # Se não for POST, redirecionar para a ficha do paciente
    return redirect('psicologia:paciente_detail', pk=paciente_id)


@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def documento_dados_json(request, pk):
    """View para retornar dados do documento em JSON para uso em modais"""
    try:
        documento = get_object_or_404(Documento, pk=pk)
        
        # Verificar se o usuário pode acessar este documento
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogo pode ver documentos de pacientes que atende ou documentos que criou
            if documento.paciente.psicologo_responsavel != request.user.psicologo and documento.psicologo != request.user.psicologo:
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para acessar este documento.'
                }, status=403)
        
        # Preparar dados do documento
        data = {
            'success': True,
            'documento': {
                'titulo': documento.titulo,
                'tipo_display': documento.get_tipo_display(),
                'descricao': documento.descricao or '',
                'data_criacao': documento.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'paciente_nome': documento.paciente.associado.nome if documento.paciente and documento.paciente.associado else 'N/A',
                'psicologo_nome': documento.psicologo.nome_completo if documento.psicologo else 'N/A',
                'arquivo_url': documento.arquivo.url if documento.arquivo else None,
                'arquivo_nome': documento.arquivo.name.split('/')[-1] if documento.arquivo else None,
                'arquivo_tamanho': f"{documento.arquivo.size / 1024:.1f} KB" if documento.arquivo and hasattr(documento.arquivo, 'size') else None,
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar dados do documento: {str(e)}'
        }, status=500)

@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def sessao_dados_json(request, pk):
    """View para retornar dados da sessão em JSON para uso em modais"""
    try:
        sessao = get_object_or_404(Sessao, pk=pk)
        
        # Verificar se o usuário pode acessar esta sessão
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogo pode ver sessões de pacientes que atende ou sessões que criou
            if sessao.paciente.psicologo_responsavel != request.user.psicologo and sessao.psicologo != request.user.psicologo:
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para acessar esta sessão.'
                }, status=403)
        
        # Preparar dados da sessão
        data = {
            'success': True,
            'sessao': {
                'id': sessao.pk,
                'paciente_nome': sessao.paciente.associado.nome if sessao.paciente and sessao.paciente.associado else 'N/A',
                'psicologo_nome': sessao.psicologo.nome_completo if sessao.psicologo else 'N/A',
                'data_hora': sessao.data_hora.strftime('%Y-%m-%dT%H:%M') if sessao.data_hora else 'N/A',
                'duracao': sessao.duracao,
                'tipo_sessao': sessao.tipo_sessao,
                'tipo_sessao_display': sessao.get_tipo_sessao_display(),
                'status': sessao.status,
                'status_display': sessao.get_status_display(),
                'valor': float(sessao.valor) if sessao.valor else 0.0,
                'observacoes': sessao.observacoes or '',
                'data_criacao': sessao.data_criacao.strftime('%d/%m/%Y %H:%M') if sessao.data_criacao else 'N/A',
                'pode_editar': sessao.status != 'realizada',
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar dados da sessão: {str(e)}'
        }, status=500)

@require_user_type(['administrador_sistema', 'atendente_psicologo', 'psicologo'])
def agenda_dados_json(request, pk):
    """View para retornar dados da agenda em JSON para uso em modais"""
    try:
        agenda = get_object_or_404(Agenda, pk=pk)
        
        # Verificar se o usuário pode acessar esta agenda
        if request.user.tipo_usuario == 'psicologo' and hasattr(request.user, 'psicologo'):
            # Psicólogo só pode ver sua própria agenda
            if agenda.psicologo != request.user.psicologo:
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para acessar esta agenda.'
                }, status=403)
        
        # Preparar dados da agenda
        data = {
            'success': True,
            'agenda': {
                'id': agenda.pk,
                'psicologo_nome': agenda.psicologo.nome_completo if agenda.psicologo else 'N/A',
                'data': agenda.data.strftime('%Y-%m-%d') if agenda.data else 'N/A',
                'hora_inicio': agenda.hora_inicio.strftime('%H:%M') if agenda.hora_inicio else 'N/A',
                'hora_fim': agenda.hora_fim.strftime('%H:%M') if agenda.hora_fim else 'N/A',
                'disponivel': agenda.disponivel,
                'observacoes': agenda.observacoes or '',
                'data_criacao': agenda.data.strftime('%d/%m/%Y') if agenda.data else 'N/A',
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar dados da agenda: {str(e)}'
        }, status=500)

# ============================================================================
# VIEWS PARA MODAIS
# ============================================================================

@require_user_type(['administrador_sistema', 'atendente_psicologo'])
def psicologo_modal_create(request):
    """View para criar psicólogo via modal"""
    try:
        if request.method == 'POST':
            form = PsicologoForm(request.POST, request.FILES)
            if form.is_valid():
                psicologo = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Psicólogo {psicologo.nome_completo} criado com sucesso!',
                    'reload': True,
                    'id': psicologo.id,
                    'nome': psicologo.nome_completo
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro na validação do formulário.',
                    'errors': form.errors
                })
        
        form = PsicologoForm()
        form_html = render_to_string('psicologia/forms/psicologo_form_modal.html', {'form': form}, request=request)
        return JsonResponse({
            'success': True,
            'html': form_html
        })
    except Exception as e:
        import traceback
        print(f"Erro na view psicologo_modal_create: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)


@require_user_type(['administrador_sistema'])
def psicologo_modal_update(request, pk):
    """View para editar psicólogo via modal"""
    try:
        psicologo = get_object_or_404(Psicologo, pk=pk)
        
        if request.method == 'POST':
            form = PsicologoForm(request.POST, request.FILES, instance=psicologo)
            if form.is_valid():
                psicologo = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Psicólogo atualizado com sucesso!',
                    'reload': True,
                    'id': psicologo.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro na validação do formulário.',
                    'errors': form.errors
                })
        
        # Teste simples primeiro
        form = PsicologoForm(instance=psicologo)
        
        # Verificar se o formulário está sendo criado corretamente
        if not form:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao criar formulário'
            }, status=500)
        
        form_html = render_to_string('psicologia/forms/psicologo_form_modal.html', {'form': form}, request=request)
        return JsonResponse({
            'success': True,
            'html': form_html
        })
        
    except Exception as e:
        import traceback
        print(f"Erro na view psicologo_modal_update: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def paciente_modal_create(request):
    """View para criar paciente via modal"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Paciente {paciente.nome_completo} criado com sucesso!',
                'reload': True,
                'id': paciente.id,
                'nome': paciente.nome_completo
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = PacienteForm()
    form_html = render_to_string('psicologia/forms/paciente_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def paciente_modal_update(request, pk):
    """View para editar paciente via modal"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            paciente = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Paciente atualizado com sucesso!',
                'reload': True,
                'id': paciente.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = PacienteForm(instance=paciente)
    
    form_html = render_to_string('psicologia/forms/paciente_form_modal.html', {'form': form}, request=request)
    
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def sessao_modal_create(request):
    """View para criar sessão via modal"""
    if request.method == 'POST':
        form = SessaoForm(request.POST)
        if form.is_valid():
            sessao = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Sessão criada com sucesso para {sessao.paciente.nome_completo}!',
                'reload': True,
                'id': sessao.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = SessaoForm()
    form_html = render_to_string('psicologia/forms/sessao_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def sessao_modal_update(request, pk):
    """View para editar sessão via modal"""
    sessao = get_object_or_404(Sessao, pk=pk)
    
    if request.method == 'POST':
        form = SessaoForm(request.POST, instance=sessao)
        if form.is_valid():
            sessao = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Sessão atualizada com sucesso!',
                'reload': True,
                'id': sessao.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = SessaoForm(instance=sessao)
    
    form_html = render_to_string('psicologia/forms/sessao_form_modal.html', {'form': form}, request=request)
    
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo'])
def prontuario_modal_create(request):
    """View para criar prontuário via modal"""
    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            prontuario = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Prontuário criado com sucesso para {prontuario.paciente.nome_completo}!',
                'reload': True,
                'id': prontuario.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = ProntuarioForm()
    form_html = render_to_string('psicologia/forms/prontuario_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo'])
def prontuario_modal_update(request, pk):
    """View para editar prontuário via modal"""
    prontuario = get_object_or_404(Prontuario, pk=pk)
    
    if request.method == 'POST':
        form = ProntuarioForm(request.POST, instance=prontuario)
        if form.is_valid():
            prontuario = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Prontuário atualizado com sucesso!',
                'reload': True,
                'id': prontuario.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = ProntuarioForm(instance=prontuario)
    form_html = render_to_string('psicologia/forms/prontuario_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo'])
def evolucao_modal_create(request):
    """View para criar evolução via modal"""
    if request.method == 'POST':
        form = EvolucaoForm(request.POST)
        if form.is_valid():
            evolucao = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Evolução criada com sucesso!',
                'reload': True,
                'id': evolucao.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = EvolucaoForm()
    form_html = render_to_string('psicologia/forms/evolucao_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo'])
def evolucao_modal_update(request, pk):
    """View para editar evolução via modal"""
    evolucao = get_object_or_404(Evolucao, pk=pk)
    
    if request.method == 'POST':
        form = EvolucaoForm(request.POST, instance=evolucao)
        if form.is_valid():
            evolucao = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Evolução atualizada com sucesso!',
                'reload': True,
                'id': evolucao.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = EvolucaoForm(instance=evolucao)
    form_html = render_to_string('psicologia/forms/evolucao_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def documento_modal_create(request):
    """View para criar documento via modal"""
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Documento {documento.titulo} criado com sucesso!',
                'reload': True,
                'id': documento.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DocumentoForm()
    form_html = render_to_string('psicologia/forms/documento_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def documento_modal_update(request, pk):
    """View para editar documento via modal"""
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Documento {documento.titulo} atualizado com sucesso!',
                'reload': True,
                'id': documento.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DocumentoForm(instance=documento)
    form_html = render_to_string('psicologia/forms/documento_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def agenda_modal_create(request):
    """View para criar agenda via modal"""
    if request.method == 'POST':
        form = AgendaForm(request.POST, request=request)
        if form.is_valid():
            agenda = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Agenda criada com sucesso!',
                'reload': True,
                'id': agenda.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AgendaForm(request=request)
    form_html = render_to_string('psicologia/forms/agenda_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })


@require_user_type(['administrador_sistema', 'psicologo', 'atendente_psicologo'])
def agenda_modal_update(request, pk):
    """View para editar agenda via modal"""
    agenda = get_object_or_404(Agenda, pk=pk)
    
    if request.method == 'POST':
        form = AgendaForm(request.POST, request=request, instance=agenda)
        if form.is_valid():
            agenda = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Agenda atualizada com sucesso!',
                'reload': True,
                'id': agenda.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AgendaForm(request=request, instance=agenda)
    form_html = render_to_string('psicologia/forms/agenda_form_modal.html', {'form': form}, request=request)
    return JsonResponse({
        'success': True,
        'html': form_html
    })

def psicologo_detail_modal(request, pk):
    """View para retornar detalhes do psicólogo em formato JSON para modal"""
    try:
        psicologo = Psicologo.objects.get(pk=pk)
        
        # Renderizar o HTML do modal
        html = render_to_string('psicologia/psicologo_detail_modal.html', {
            'psicologo': psicologo
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'psicologo': {
                'id': psicologo.pk,
                'nome_completo': psicologo.nome_completo,
                'crp': psicologo.crp,
                'ativo': psicologo.ativo
            },
            'html': html
        })
    except Psicologo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Psicólogo não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

