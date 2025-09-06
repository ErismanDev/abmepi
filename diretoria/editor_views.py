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

from .models import AtaReuniao
from core.forms import AtaReuniaoEditorForm, AtaReuniaoTemplateForm, AtaReuniaoSearchForm


class AtaEditorView(LoginRequiredMixin, CreateView):
    """
    View para criar ata com editor avançado similar ao SEI
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_avancado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = None
        context['template_form'] = AtaReuniaoTemplateForm()
        return context
    
    def form_valid(self, form):
        # Definir usuário que criou a ata
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = timezone.now()
        
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Ata "{form.instance.titulo}" criada com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_edit', kwargs={'pk': self.object.pk})


class AtaEditorEditView(LoginRequiredMixin, UpdateView):
    """
    View para editar ata com editor avançado
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_avancado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = self.object
        context['template_form'] = AtaReuniaoTemplateForm()
        return context
    
    def form_valid(self, form):
        # Atualizar data de modificação
        form.instance.data_atualizacao = timezone.now()
        form.instance.modificado_por = self.request.user
        
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Ata "{form.instance.titulo}" atualizada com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_edit', kwargs={'pk': self.object.pk})


class AtaEditorListView(LoginRequiredMixin, ListView):
    """
    Lista de atas com filtros avançados
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_editor_list.html'
    context_object_name = 'atas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AtaReuniao.objects.all().order_by('-data_reuniao')
        
        # Aplicar filtros
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(local__icontains=search) |
                Q(conteudo_completo__icontains=search)
            )
        
        tipo_reuniao = self.request.GET.get('tipo_reuniao')
        if tipo_reuniao:
            queryset = queryset.filter(tipo_reuniao=tipo_reuniao)
        
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_reuniao__date__gte=data_inicio)
        
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_reuniao__date__lte=data_fim)
        
        aprovada = self.request.GET.get('aprovada')
        if aprovada == 'true':
            queryset = queryset.filter(aprovada=True)
        elif aprovada == 'false':
            queryset = queryset.filter(aprovada=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AtaReuniaoSearchForm(self.request.GET)
        return context


@login_required
def salvar_ata_ajax(request, pk=None):
    """
    API para salvar ata via AJAX (auto-save)
    """
    try:
        if request.method == 'POST':
            if pk:
                # Atualizar ata existente
                try:
                    ata = AtaReuniao.objects.get(pk=pk)
                    form = AtaReuniaoEditorForm(request.POST, instance=ata)
                except AtaReuniao.DoesNotExist:
                    return JsonResponse({'error': 'Ata não encontrada'}, status=404)
            else:
                # Criar nova ata
                form = AtaReuniaoEditorForm(request.POST)
            
            if form.is_valid():
                ata = form.save(commit=False)
                if not pk:
                    ata.criado_por = request.user
                    ata.data_criacao = timezone.now()
                else:
                    ata.modificado_por = request.user
                    ata.data_atualizacao = timezone.now()
                
                ata.save()
                form.save_m2m()  # Salvar relacionamentos many-to-many
                
                return JsonResponse({
                    'success': True,
                    'message': 'Ata salva com sucesso!',
                    'ata_id': ata.id,
                    'data_atualizacao': ata.data_atualizacao.strftime('%d/%m/%Y %H:%M')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        else:
            return JsonResponse({'error': 'Método não permitido'}, status=405)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def aplicar_template_ajax(request):
    """
    API para aplicar template de ata
    """
    try:
        template_type = request.POST.get('template')
        titulo = request.POST.get('titulo', '')
        
        templates = {
            'basico': '''
                <h2 style="text-align: center; color: #2c3e50;">ATA DE REUNIÃO</h2>
                <p style="text-align: center; font-weight: bold; color: #34495e;">
                    [Tipo da Reunião] - [Data e Hora]
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; background: #f8f9fa; font-weight: bold;">Local:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">[Local da Reunião]</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; background: #f8f9fa; font-weight: bold;">Presidente:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">[Nome do Presidente]</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; background: #f8f9fa; font-weight: bold;">Secretário:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">[Nome do Secretário]</td>
                    </tr>
                </table>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">PRESENTES:</h3>
                <ul>
                    <li>[Lista de membros presentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">AUSENTES:</h3>
                <ul>
                    <li>[Lista de membros ausentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">PAUTA:</h3>
                <ol>
                    <li>[Item 1]</li>
                    <li>[Item 2]</li>
                    <li>[Item 3]</li>
                </ol>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">DELIBERAÇÕES:</h3>
                <p>[Decisões tomadas na reunião]</p>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">OBSERVAÇÕES:</h3>
                <p>[Observações adicionais]</p>
                
                <p style="text-align: center; font-style: italic; margin-top: 30px; color: #7f8c8d;">
                    Esta ata foi aprovada pelos presentes.
                </p>
            ''',
            'completa': '''
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">ASSOCIAÇÃO BENEFICENTE DOS MILITARES DO ESTADO DO PIAUÍ</h1>
                    <h2 style="color: #34495e; margin-bottom: 20px;">ATA DE REUNIÃO</h2>
                    <p style="font-size: 16px; color: #7f8c8d;">[Tipo da Reunião]</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold; width: 30%;">Data e Hora:</td>
                            <td style="padding: 8px;">[Data e Hora da Reunião]</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Local:</td>
                            <td style="padding: 8px;">[Local da Reunião]</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Presidente:</td>
                            <td style="padding: 8px;">[Nome do Presidente]</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Secretário:</td>
                            <td style="padding: 8px;">[Nome do Secretário]</td>
                        </tr>
                    </table>
                </div>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">MEMBROS PRESENTES:</h3>
                <ul>
                    <li>[Lista de membros presentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">MEMBROS AUSENTES:</h3>
                <ul>
                    <li>[Lista de membros ausentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">PAUTA:</h3>
                <ol>
                    <li>[Item 1]</li>
                    <li>[Item 2]</li>
                    <li>[Item 3]</li>
                </ol>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">DELIBERAÇÕES:</h3>
                <p>[Decisões tomadas na reunião]</p>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">OBSERVAÇÕES:</h3>
                <p>[Observações adicionais]</p>
                
                <div style="margin-top: 40px; text-align: center;">
                    <p style="font-style: italic; color: #7f8c8d;">
                        Esta ata foi aprovada pelos presentes e assinada pelo presidente e secretário.
                    </p>
                    <div style="margin-top: 30px; display: flex; justify-content: space-around;">
                        <div style="text-align: center;">
                            <p style="border-top: 1px solid #000; width: 200px; margin: 0 auto; padding-top: 5px;">
                                [Nome do Presidente]<br>
                                <small>Presidente</small>
                            </p>
                        </div>
                        <div style="text-align: center;">
                            <p style="border-top: 1px solid #000; width: 200px; margin: 0 auto; padding-top: 5px;">
                                [Nome do Secretário]<br>
                                <small>Secretário</small>
                            </p>
                        </div>
                    </div>
                </div>
            ''',
            'extraordinaria': '''
                <h2 style="text-align: center; color: #e74c3c;">ATA DE REUNIÃO EXTRAORDINÁRIA</h2>
                <p style="text-align: center; font-weight: bold; color: #c0392b;">
                    [Data e Hora] - [Local]
                </p>
                
                <div style="background: #fdf2f2; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0;">
                    <p><strong>Motivo da Convocação:</strong> [Descrever o motivo da reunião extraordinária]</p>
                    <p><strong>Convocante:</strong> [Nome do convocante]</p>
                </div>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">PRESENTES:</h3>
                <ul>
                    <li>[Lista de membros presentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">AUSENTES:</h3>
                <ul>
                    <li>[Lista de membros ausentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">PAUTA:</h3>
                <ol>
                    <li>[Item 1]</li>
                    <li>[Item 2]</li>
                    <li>[Item 3]</li>
                </ol>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">DELIBERAÇÕES:</h3>
                <p>[Decisões tomadas na reunião]</p>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">OBSERVAÇÕES:</h3>
                <p>[Observações adicionais]</p>
                
                <p style="text-align: center; font-style: italic; margin-top: 30px; color: #7f8c8d;">
                    Esta ata foi aprovada pelos presentes em reunião extraordinária.
                </p>
            ''',
            'emergencia': '''
                <h2 style="text-align: center; color: #d63031;">ATA DE REUNIÃO DE EMERGÊNCIA</h2>
                <p style="text-align: center; font-weight: bold; color: #a29bfe;">
                    [Data e Hora] - [Local]
                </p>
                
                <div style="background: #fff5f5; border: 2px solid #d63031; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h4 style="color: #d63031; margin-top: 0;">⚠️ SITUAÇÃO DE EMERGÊNCIA</h4>
                    <p><strong>Natureza da Emergência:</strong> [Descrever a situação de emergência]</p>
                    <p><strong>Urgência:</strong> [Justificar a urgência da reunião]</p>
                    <p><strong>Convocante:</strong> [Nome do convocante]</p>
                </div>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #d63031; padding-bottom: 5px;">PRESENTES:</h3>
                <ul>
                    <li>[Lista de membros presentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #d63031; padding-bottom: 5px;">AUSENTES:</h3>
                <ul>
                    <li>[Lista de membros ausentes]</li>
                </ul>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #d63031; padding-bottom: 5px;">PAUTA:</h3>
                <ol>
                    <li>[Item 1]</li>
                    <li>[Item 2]</li>
                    <li>[Item 3]</li>
                </ol>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #d63031; padding-bottom: 5px;">DELIBERAÇÕES:</h3>
                <p>[Decisões tomadas na reunião de emergência]</p>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #d63031; padding-bottom: 5px;">OBSERVAÇÕES:</h3>
                <p>[Observações adicionais sobre a situação de emergência]</p>
                
                <p style="text-align: center; font-style: italic; margin-top: 30px; color: #7f8c8d;">
                    Esta ata foi aprovada pelos presentes em reunião de emergência.
                </p>
            '''
        }
        
        if template_type in templates:
            return JsonResponse({
                'success': True,
                'content': templates[template_type]
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Template não encontrado'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
