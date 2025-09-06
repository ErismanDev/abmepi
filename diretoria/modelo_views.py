from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import ModeloAtaPersonalizado, AtaReuniao


class ModeloAtaListView(LoginRequiredMixin, ListView):
    """
    Lista de modelos de ata personalizados
    """
    model = ModeloAtaPersonalizado
    template_name = 'diretoria/modelo_ata_list.html'
    context_object_name = 'modelos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ModeloAtaPersonalizado.objects.filter(
            Q(publico=True) | Q(criado_por=self.request.user)
        ).filter(ativo=True)
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(categoria__icontains=search)
            )
        
        # Filtro por categoria
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        # Filtro por tipo de reunião
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_reuniao=tipo)
        
        return queryset.order_by('-data_atualizacao')


class ModeloAtaCreateView(LoginRequiredMixin, CreateView):
    """
    Criar novo modelo de ata
    """
    model = ModeloAtaPersonalizado
    template_name = 'diretoria/modelo_ata_form.html'
    fields = ['nome', 'descricao', 'categoria', 'publico']
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        form.instance.conteudo_html = self.request.POST.get('conteudo_html', '')
        form.instance.titulo_original = self.request.POST.get('titulo_original', '')
        form.instance.tipo_reuniao = self.request.POST.get('tipo_reuniao', 'ordinaria')
        
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Modelo "{form.instance.nome}" criado com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:modelo_ata_list')


class ModeloAtaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar modelo de ata
    """
    model = ModeloAtaPersonalizado
    template_name = 'diretoria/modelo_ata_form.html'
    fields = ['nome', 'descricao', 'categoria', 'publico', 'ativo']
    
    def get_queryset(self):
        return ModeloAtaPersonalizado.objects.filter(criado_por=self.request.user)
    
    def form_valid(self, form):
        form.instance.conteudo_html = self.request.POST.get('conteudo_html', '')
        form.instance.titulo_original = self.request.POST.get('titulo_original', '')
        form.instance.tipo_reuniao = self.request.POST.get('tipo_reuniao', 'ordinaria')
        
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Modelo "{form.instance.nome}" atualizado com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:modelo_ata_list')


class ModeloAtaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir modelo de ata
    """
    model = ModeloAtaPersonalizado
    template_name = 'diretoria/modelo_ata_confirm_delete.html'
    success_url = reverse_lazy('diretoria:modelo_ata_list')
    
    def get_queryset(self):
        return ModeloAtaPersonalizado.objects.filter(criado_por=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Modelo excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def salvar_modelo_ajax(request):
    """
    API para salvar modelo de ata via AJAX
    """
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            categoria = request.POST.get('categoria', 'geral')
            conteudo_html = request.POST.get('conteudo_html', '')
            titulo_original = request.POST.get('titulo_original', '')
            tipo_reuniao = request.POST.get('tipo_reuniao', 'ordinaria')
            publico = request.POST.get('publico') == 'true'
            
            if not nome or not conteudo_html:
                return JsonResponse({
                    'success': False,
                    'error': 'Nome e conteúdo são obrigatórios'
                }, status=400)
            
            # Verificar se já existe um modelo com o mesmo nome
            if ModeloAtaPersonalizado.objects.filter(
                nome=nome, 
                criado_por=request.user
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe um modelo com este nome'
                }, status=400)
            
            # Criar o modelo
            modelo = ModeloAtaPersonalizado.objects.create(
                nome=nome,
                descricao=descricao,
                categoria=categoria,
                conteudo_html=conteudo_html,
                titulo_original=titulo_original,
                tipo_reuniao=tipo_reuniao,
                publico=publico,
                criado_por=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Modelo salvo com sucesso!',
                'modelo_id': modelo.id,
                'modelo_nome': modelo.nome
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def aplicar_modelo_ajax(request):
    """
    API para aplicar modelo de ata via AJAX
    """
    if request.method == 'POST':
        try:
            modelo_id = request.POST.get('modelo_id')
            
            if not modelo_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID do modelo é obrigatório'
                }, status=400)
            
            modelo = get_object_or_404(
                ModeloAtaPersonalizado.objects.filter(
                    Q(publico=True) | Q(criado_por=request.user)
                ).filter(ativo=True),
                id=modelo_id
            )
            
            # Incrementar contador de uso
            modelo.incrementar_uso()
            
            return JsonResponse({
                'success': True,
                'conteudo_html': modelo.conteudo_html,
                'titulo_sugestao': modelo.titulo_original,
                'tipo_reuniao': modelo.tipo_reuniao,
                'modelo_nome': modelo.nome
            })
            
        except ModeloAtaPersonalizado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Modelo não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def listar_modelos_ajax(request):
    """
    API para listar modelos disponíveis via AJAX
    """
    try:
        modelos = ModeloAtaPersonalizado.objects.filter(
            Q(publico=True) | Q(criado_por=request.user)
        ).filter(ativo=True).order_by('-data_atualizacao')
        
        # Filtro por categoria se fornecido
        categoria = request.GET.get('categoria')
        if categoria:
            modelos = modelos.filter(categoria=categoria)
        
        # Filtro por tipo se fornecido
        tipo = request.GET.get('tipo')
        if tipo:
            modelos = modelos.filter(tipo_reuniao=tipo)
        
        modelos_data = []
        for modelo in modelos:
            modelos_data.append({
                'id': modelo.id,
                'nome': modelo.nome,
                'descricao': modelo.descricao,
                'categoria': modelo.categoria,
                'tipo_reuniao': modelo.tipo_reuniao,
                'tipo_reuniao_display': modelo.get_tipo_reuniao_display(),
                'vezes_usado': modelo.vezes_usado,
                'data_criacao': modelo.data_criacao.strftime('%d/%m/%Y'),
                'criado_por': modelo.criado_por.get_full_name() or modelo.criado_por.username,
                'publico': modelo.publico
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
