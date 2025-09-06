from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import ModeloAtaUnificado
from .forms import ModeloAtaUnificadoForm


class ModeloAtaUnificadoListView(LoginRequiredMixin, ListView):
    """
    Lista de modelos de ata unificados
    """
    model = ModeloAtaUnificado
    template_name = 'diretoria/modelo_unificado_list.html'
    context_object_name = 'modelos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ModeloAtaUnificado.objects.filter(
            Q(publico=True) | Q(criado_por=self.request.user)
        ).filter(ativo=True).select_related('criado_por')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(categoria__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Filtro por categoria
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        # Filtro por tipo de conteúdo
        tipo_conteudo = self.request.GET.get('tipo_conteudo')
        if tipo_conteudo:
            queryset = queryset.filter(tipo_conteudo=tipo_conteudo)
        
        # Filtro por tags
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        return queryset.order_by('-data_atualizacao')
    
    def get_context_data(self, **kwargs):
        # Definir atributos necessários se não estiverem definidos
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        if not hasattr(self, 'kwargs'):
            self.kwargs = {}
        
        context = super().get_context_data(**kwargs)
        context['categorias'] = ModeloAtaUnificado.CATEGORIA_CHOICES
        context['tipos_conteudo'] = ModeloAtaUnificado.TIPO_CONTEUDO_CHOICES
        context['search'] = self.request.GET.get('search', '')
        context['categoria_atual'] = self.request.GET.get('categoria', '')
        context['tipo_atual'] = self.request.GET.get('tipo_conteudo', '')
        context['tag_atual'] = self.request.GET.get('tag', '')
        
        # Tags mais usadas para filtro
        context['tags_populares'] = ModeloAtaUnificado.objects.filter(
            ativo=True
        ).exclude(tags='').values_list('tags', flat=True)
        
        return context


class ModeloAtaUnificadoCreateView(LoginRequiredMixin, CreateView):
    """
    Criar novo modelo de ata unificado
    """
    model = ModeloAtaUnificado
    form_class = ModeloAtaUnificadoForm
    template_name = 'diretoria/modelo_unificado_form.html'
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Modelo "{form.instance.nome}" criado com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:modelo_unificado_list')


class ModeloAtaUnificadoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar modelo de ata unificado
    """
    model = ModeloAtaUnificado
    form_class = ModeloAtaUnificadoForm
    template_name = 'diretoria/modelo_unificado_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.can_edit(request.user):
            raise PermissionDenied("Você não tem permissão para editar este modelo.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Modelo "{form.instance.nome}" atualizado com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:modelo_unificado_list')


class ModeloAtaUnificadoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir modelo de ata unificado
    """
    model = ModeloAtaUnificado
    template_name = 'diretoria/modelo_unificado_confirm_delete.html'
    success_url = reverse_lazy('diretoria:modelo_unificado_list')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.can_delete(request.user):
            raise PermissionDenied("Você não tem permissão para excluir este modelo.")
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request, 
            f'Modelo "{obj.nome}" excluído com sucesso!'
        )
        return super().delete(request, *args, **kwargs)


@login_required
def usar_modelo_ajax(request, pk):
    """
    Usar modelo via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        modelo = get_object_or_404(ModeloAtaUnificado, pk=pk, ativo=True)
        
        # Verificar permissão
        if not (modelo.publico or modelo.criado_por == request.user):
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Incrementar contador de uso
        modelo.incrementar_uso()
        
        return JsonResponse({
            'success': True,
            'modelo': {
                'id': modelo.id,
                'nome': modelo.nome,
                'conteudo': modelo.get_conteudo_final(),
                'tipo_conteudo': modelo.tipo_conteudo,
                'categoria': modelo.categoria,
                'tags': modelo.get_tags_list()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def listar_modelos_ajax(request):
    """
    API para listar modelos disponíveis via AJAX
    """
    try:
        modelos = ModeloAtaUnificado.objects.filter(
            Q(publico=True) | Q(criado_por=request.user)
        ).filter(ativo=True).order_by('-data_atualizacao')
        
        # Filtros
        categoria = request.GET.get('categoria')
        if categoria:
            modelos = modelos.filter(categoria=categoria)
        
        tipo_conteudo = request.GET.get('tipo_conteudo')
        if tipo_conteudo:
            modelos = modelos.filter(tipo_conteudo=tipo_conteudo)
        
        search = request.GET.get('search')
        if search:
            modelos = modelos.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(tags__icontains=search)
            )
        
        modelos_data = []
        for modelo in modelos:
            modelos_data.append({
                'id': modelo.id,
                'nome': modelo.nome,
                'descricao': modelo.descricao,
                'categoria': modelo.categoria,
                'categoria_display': modelo.get_categoria_display(),
                'tipo_conteudo': modelo.tipo_conteudo,
                'tipo_conteudo_display': modelo.get_tipo_conteudo_display(),
                'vezes_usado': modelo.vezes_usado,
                'data_criacao': modelo.data_criacao.strftime('%d/%m/%Y'),
                'criado_por': modelo.criado_por.get_full_name() or modelo.criado_por.username,
                'publico': modelo.publico,
                'tags': modelo.get_tags_list()
            })
        
        return JsonResponse({
            'success': True,
            'modelos': modelos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def duplicar_modelo(request, pk):
    """
    Duplicar um modelo existente
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        modelo_original = get_object_or_404(ModeloAtaUnificado, pk=pk, ativo=True)
        
        # Verificar permissão
        if not (modelo_original.publico or modelo_original.criado_por == request.user):
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Criar cópia
        novo_modelo = ModeloAtaUnificado.objects.create(
            nome=f"{modelo_original.nome} (Cópia)",
            descricao=modelo_original.descricao,
            categoria=modelo_original.categoria,
            tipo_conteudo=modelo_original.tipo_conteudo,
            conteudo=modelo_original.conteudo,
            conteudo_html=modelo_original.conteudo_html,
            titulo_original=modelo_original.titulo_original,
            tags=modelo_original.tags,
            publico=False,  # Cópia sempre privada
            criado_por=request.user
        )
        
        return JsonResponse({
            'success': True,
            'modelo_id': novo_modelo.id,
            'message': f'Modelo "{novo_modelo.nome}" duplicado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
