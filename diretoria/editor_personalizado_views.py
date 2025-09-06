from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import CargoDiretoria, MembroDiretoria, AtaReuniao, ResolucaoDiretoria
from .forms import CargoDiretoriaForm, MembroDiretoriaForm, AtaReuniaoForm, ResolucaoDiretoriaForm
from core.forms import AtaReuniaoEditorForm, AtaReuniaoTemplateForm, AtaReuniaoSearchForm
from core.permissions import require_user_type


class AtaEditorPersonalizadoListView(LoginRequiredMixin, ListView):
    """
    Lista de atas com acesso ao editor personalizado
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_editor_personalizado_list.html'
    context_object_name = 'atas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AtaReuniao.objects.select_related('presidente__associado', 'secretario__associado')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(pauta__icontains=search) |
                Q(deliberacoes__icontains=search)
            )
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_reuniao=tipo)
        
        # Filtro por data
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_reuniao__date__gte=data_inicio)
        
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_reuniao__date__lte=data_fim)
        
        return queryset.order_by('-data_reuniao')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AtaReuniaoSearchForm(self.request.GET)
        context['total_atas'] = AtaReuniao.objects.count()
        return context


class AtaEditorPersonalizadoCreateView(LoginRequiredMixin, CreateView):
    """
    Criar nova ata de reunião com editor personalizado
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_personalizado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = None
        context['template_form'] = AtaReuniaoTemplateForm()
        context['is_creating'] = True
        return context
    
    def form_valid(self, form):
        # Salvar a ata (os campos data_criacao e data_atualizacao são automáticos)
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Ata "{form.instance.titulo}" criada com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_personalizado_edit', kwargs={'pk': self.object.pk})


class AtaEditorPersonalizadoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar ata de reunião com editor personalizado
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_personalizado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = self.object
        context['template_form'] = AtaReuniaoTemplateForm()
        context['is_creating'] = False
        return context
    
    def form_valid(self, form):
        # Salvar a ata (os campos data_criacao e data_atualizacao são automáticos)
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Ata "{form.instance.titulo}" atualizada com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_personalizado_edit', kwargs={'pk': self.object.pk})


class AtaEditorPersonalizadoDetailView(LoginRequiredMixin, DetailView):
    """
    Visualizar ata de reunião com editor personalizado
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_editor_personalizado_detail.html'
    context_object_name = 'ata'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = True  # Você pode adicionar lógica de permissão aqui
        return context


@login_required
def salvar_ata_personalizado_ajax(request, pk=None):
    """
    Salvar ata via AJAX (salvamento automático)
    """
    if request.method == 'POST':
        try:
            if pk:
                ata = get_object_or_404(AtaReuniao, pk=pk)
                form = AtaReuniaoEditorForm(request.POST, instance=ata)
            else:
                form = AtaReuniaoEditorForm(request.POST)
            
            if form.is_valid():
                ata = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Ata salva com sucesso!',
                    'ata_id': ata.pk
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro de validação',
                    'errors': form.errors
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao salvar: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })


@login_required
def aplicar_template_personalizado_ajax(request):
    """
    Aplicar template pré-definido via AJAX
    """
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        
        # Templates pré-definidos
        templates = {
            '1': {
                'titulo': 'ATA DE REUNIÃO ORDINÁRIA',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO ORDINÁRIA</h2>
                    <p><strong>Tipo:</strong> Reunião Ordinária</p>
                    <p><strong>Data:</strong> [Data e Hora]</p>
                    <p><strong>Local:</strong> [Local da Reunião]</p>
                    <p><strong>Presidente:</strong> [Nome do Presidente]</p>
                    <p><strong>Secretário:</strong> [Nome do Secretário]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[Lista de membros presentes]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[Lista de membros ausentes]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>[Item 1]</li>
                        <li>[Item 2]</li>
                        <li>[Item 3]</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>[Decisões tomadas na reunião]</p>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>[Observações adicionais]</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes.</em></p>
                '''
            },
            '2': {
                'titulo': 'ATA DE REUNIÃO EXTRAORDINÁRIA',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO EXTRAORDINÁRIA</h2>
                    <p><strong>Tipo:</strong> Reunião Extraordinária</p>
                    <p><strong>Data:</strong> [Data e Hora]</p>
                    <p><strong>Local:</strong> [Local da Reunião]</p>
                    <p><strong>Presidente:</strong> [Nome do Presidente]</p>
                    <p><strong>Secretário:</strong> [Nome do Secretário]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[Lista de membros presentes]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[Lista de membros ausentes]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>[Item 1]</li>
                        <li>[Item 2]</li>
                        <li>[Item 3]</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>[Decisões tomadas na reunião]</p>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>[Observações adicionais]</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes.</em></p>
                '''
            },
            '3': {
                'titulo': 'ATA DE REUNIÃO DE EMERGÊNCIA',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO DE EMERGÊNCIA</h2>
                    <p><strong>Tipo:</strong> Reunião de Emergência</p>
                    <p><strong>Data:</strong> [Data e Hora]</p>
                    <p><strong>Local:</strong> [Local da Reunião]</p>
                    <p><strong>Presidente:</strong> [Nome do Presidente]</p>
                    <p><strong>Secretário:</strong> [Nome do Secretário]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[Lista de membros presentes]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[Lista de membros ausentes]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>[Item 1]</li>
                        <li>[Item 2]</li>
                        <li>[Item 3]</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>[Decisões tomadas na reunião]</p>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>[Observações adicionais]</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes.</em></p>
                '''
            }
        }
        
        if template_id in templates:
            return JsonResponse({
                'success': True,
                'template': templates[template_id]
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Template não encontrado'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })
