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

from .models import CargoDiretoria, MembroDiretoria, AtaReuniao, ResolucaoDiretoria, ModeloAta, ModeloAtaPersonalizado, ModeloAtaUnificado
from .forms import CargoDiretoriaForm, MembroDiretoriaForm, AtaReuniaoForm, ResolucaoDiretoriaForm
from core.forms import AtaReuniaoEditorForm, AtaReuniaoTemplateForm, AtaReuniaoSearchForm
from core.permissions import require_user_type


class DiretoriaDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard principal da diretoria
    """
    template_name = 'diretoria/dashboard.html'
    context_object_name = 'membros_ativos'
    
    def get_queryset(self):
        return MembroDiretoria.objects.filter(
            ativo=True,
            data_inicio__lte=timezone.now().date()
        ).select_related('associado', 'cargo').order_by('cargo__ordem_hierarquica')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas
        context['total_membros'] = MembroDiretoria.objects.filter(ativo=True).count()
        context['total_cargos'] = CargoDiretoria.objects.filter(ativo=True).count()
        context['reunioes_mes'] = AtaReuniao.objects.filter(
            data_reuniao__month=timezone.now().month,
            data_reuniao__year=timezone.now().year
        ).count()
        context['resolucoes_ano'] = ResolucaoDiretoria.objects.filter(
            data_resolucao__year=timezone.now().year
        ).count()
        
        # Últimas reuniões
        context['ultimas_reunioes'] = AtaReuniao.objects.order_by('-data_reuniao')[:5]
        
        # Últimas resoluções
        context['ultimas_resolucoes'] = ResolucaoDiretoria.objects.filter(
            status='aprovada'
        ).order_by('-data_resolucao')[:5]
        
        return context


class CargoDiretoriaListView(LoginRequiredMixin, ListView):
    """
    Lista de cargos da diretoria
    """
    model = CargoDiretoria
    template_name = 'diretoria/cargo_list.html'
    context_object_name = 'cargos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CargoDiretoria.objects.all()
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        # Filtro por status
        ativo = self.request.GET.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        return queryset.order_by('ordem_hierarquica', 'nome')


class CargoDiretoriaCreateView(LoginRequiredMixin, CreateView):
    """
    Criar novo cargo da diretoria
    """
    model = CargoDiretoria
    form_class = CargoDiretoriaForm
    template_name = 'diretoria/cargo_form.html'
    success_url = reverse_lazy('diretoria:cargo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cargo criado com sucesso!')
        return super().form_valid(form)


class CargoDiretoriaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar cargo da diretoria
    """
    model = CargoDiretoria
    form_class = CargoDiretoriaForm
    template_name = 'diretoria/cargo_form.html'
    success_url = reverse_lazy('diretoria:cargo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cargo atualizado com sucesso!')
        return super().form_valid(form)


class CargoDiretoriaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir cargo da diretoria
    """
    model = CargoDiretoria
    template_name = 'diretoria/cargo_confirm_delete.html'
    success_url = reverse_lazy('diretoria:cargo_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cargo excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class MembroDiretoriaListView(LoginRequiredMixin, ListView):
    """
    Lista de membros da diretoria
    """
    model = MembroDiretoria
    template_name = 'diretoria/membro_list.html'
    context_object_name = 'membros'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = MembroDiretoria.objects.select_related('associado', 'cargo')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(associado__nome__icontains=search) |
                Q(cargo__nome__icontains=search)
            )
        
        # Filtro por cargo
        cargo_id = self.request.GET.get('cargo')
        if cargo_id:
            queryset = queryset.filter(cargo_id=cargo_id)
        
        # Filtro por status
        ativo = self.request.GET.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        return queryset.order_by('cargo__ordem_hierarquica', 'associado__nome')


class MembroDiretoriaCreateView(LoginRequiredMixin, CreateView):
    """
    Criar novo membro da diretoria
    """
    model = MembroDiretoria
    form_class = MembroDiretoriaForm
    template_name = 'diretoria/membro_form.html'
    success_url = reverse_lazy('diretoria:membro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Membro adicionado com sucesso!')
        return super().form_valid(form)


class MembroDiretoriaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar membro da diretoria
    """
    model = MembroDiretoria
    form_class = MembroDiretoriaForm
    template_name = 'diretoria/membro_form.html'
    success_url = reverse_lazy('diretoria:membro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Membro atualizado com sucesso!')
        return super().form_valid(form)


class MembroDiretoriaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir membro da diretoria
    """
    model = MembroDiretoria
    template_name = 'diretoria/membro_confirm_delete.html'
    success_url = reverse_lazy('diretoria:membro_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Membro removido com sucesso!')
        return super().delete(request, *args, **kwargs)


class AtaReuniaoListView(LoginRequiredMixin, ListView):
    """
    Lista de atas de reunião com otimizações e filtros avançados
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_list.html'
    context_object_name = 'atas'
    paginate_by = 20
    
    def get_queryset(self):
        # Otimizar consulta com select_related e prefetch_related
        queryset = AtaReuniao.objects.select_related(
            'presidente__associado',
            'presidente__cargo',
            'secretario__associado', 
            'secretario__cargo'
        ).prefetch_related(
            'membros_presentes__associado',
            'membros_presentes__cargo',
            'membros_ausentes__associado',
            'membros_ausentes__cargo'
        ).all()
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(local__icontains=search) |
                Q(pauta__icontains=search)
            )
        
        # Filtro por tipo de reunião
        tipo_reuniao = self.request.GET.get('tipo_reuniao')
        if tipo_reuniao:
            queryset = queryset.filter(tipo_reuniao=tipo_reuniao)
        
        # Filtro por status de aprovação
        aprovada = self.request.GET.get('aprovada')
        if aprovada == 'true':
            queryset = queryset.filter(aprovada=True)
        elif aprovada == 'false':
            queryset = queryset.filter(aprovada=False)
        
        # Filtro por data
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        if data_inicio:
            queryset = queryset.filter(data_reuniao__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_reuniao__date__lte=data_fim)
        
        return queryset.order_by('-data_reuniao')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas para o contexto
        total_atas = AtaReuniao.objects.count()
        atas_aprovadas = AtaReuniao.objects.filter(aprovada=True).count()
        atas_pendentes = total_atas - atas_aprovadas
        
        # Reuniões do mês atual
        from django.utils import timezone
        agora = timezone.now()
        reunioes_mes = AtaReuniao.objects.filter(
            data_reuniao__month=agora.month,
            data_reuniao__year=agora.year
        ).count()
        
        # Últimas 5 atas
        ultimas_atas = AtaReuniao.objects.select_related(
            'presidente__associado',
            'secretario__associado'
        ).order_by('-data_reuniao')[:5]
        
        context.update({
            'total_atas': total_atas,
            'atas_aprovadas': atas_aprovadas,
            'atas_pendentes': atas_pendentes,
            'reunioes_mes': reunioes_mes,
            'ultimas_atas': ultimas_atas,
            'tipos_reuniao': AtaReuniao.TIPO_REUNIAO_CHOICES,
        })
        
        return context


class AtaReuniaoDetailView(LoginRequiredMixin, DetailView):
    """
    Detalhes da ata de reunião
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_detail.html'
    context_object_name = 'ata'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membros_diretoria'] = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
        
        # Separar associados em duas listas
        from associados.models import Associado
        
        # Lista de membros da diretoria
        membros_diretoria_ids = list(MembroDiretoria.objects.filter(ativo=True).values_list('associado_id', flat=True))
        
        # IDs dos membros da diretoria que já estão presentes
        membros_presentes_ids = list(self.object.membros_presentes.values_list('associado_id', flat=True))
        
        # IDs dos associados comuns que já estão presentes
        associados_presentes_ids = list(self.object.associados_presentes.values_list('id', flat=True))
        
        # Lista de membros da diretoria disponíveis (não presentes)
        context['membros_diretoria_associados'] = Associado.objects.filter(
            id__in=membros_diretoria_ids, 
            ativo=True
        ).exclude(
            id__in=membros_presentes_ids
        ).distinct().order_by('nome')
        
        # Lista de demais associados (não membros da diretoria) disponíveis (não presentes)
        context['demais_associados'] = Associado.objects.filter(
            ativo=True
        ).exclude(
            id__in=membros_diretoria_ids
        ).exclude(
            id__in=associados_presentes_ids
        ).distinct().order_by('nome')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Processar requisições AJAX para gerenciar membros presentes
        """
        import json
        from django.http import JsonResponse
        
        self.object = self.get_object()
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'salvar_membros_presentes':
            return self.salvar_membros_presentes(data)
        elif action == 'adicionar_membro_presente':
            return self.adicionar_membro_presente(data)
        elif action == 'remover_membro_presente':
            return self.remover_membro_presente(data)
        else:
            return JsonResponse({'success': False, 'message': 'Ação não reconhecida'})
    
    def salvar_membros_presentes(self, data):
        """
        Salvar lista de membros presentes
        """
        from django.http import JsonResponse
        from associados.models import Associado
        
        try:
            associados_ids = data.get('associados_ids', [])
            
            # Limpar membros presentes atuais
            self.object.membros_presentes.clear()
            
            # Adicionar novos membros presentes
            for associado_id in associados_ids:
                try:
                    associado = Associado.objects.get(id=associado_id, ativo=True)
                    # Verificar se o associado é membro da diretoria
                    membro_diretoria = MembroDiretoria.objects.filter(
                        associado=associado, 
                        ativo=True
                    ).first()
                    
                    if membro_diretoria:
                        self.object.membros_presentes.add(membro_diretoria)
                except Associado.DoesNotExist:
                    continue
            
            # Preparar dados para resposta
            membros_presentes = []
            for membro in self.object.membros_presentes.all():
                membros_presentes.append({
                    'id': membro.id,
                    'associado_id': membro.associado.id,
                    'associado_nome': membro.associado.nome,
                    'cargo_nome': membro.cargo.nome
                })
            
            return JsonResponse({
                'success': True,
                'membros_presentes': membros_presentes
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    def adicionar_membro_presente(self, data):
        """
        Adicionar um membro à lista de presentes
        """
        from django.http import JsonResponse
        from associados.models import Associado
        
        try:
            associado_id = data.get('associado_id')
            print(f"DEBUG ADICIONAR: Associado ID recebido: {associado_id}")
            associado = Associado.objects.get(id=associado_id, ativo=True)
            print(f"DEBUG ADICIONAR: Associado encontrado: {associado.nome}")
            
            # Verificar se o associado é membro da diretoria
            membro_diretoria = MembroDiretoria.objects.filter(
                associado=associado, 
                ativo=True
            ).first()
            
            print(f"DEBUG ADICIONAR: Membro da diretoria encontrado: {membro_diretoria}")
            
            # Se for membro da diretoria, adicionar à lista de membros presentes
            if membro_diretoria:
                self.object.membros_presentes.add(membro_diretoria)
                print(f"DEBUG ADICIONAR: Adicionado à lista de membros presentes")
            else:
                # Se não for membro da diretoria, adicionar à lista de associados presentes
                self.object.associados_presentes.add(associado)
                print(f"DEBUG ADICIONAR: Adicionado à lista de associados presentes")
            
            # Preparar dados para resposta
            membros_presentes = []
            
            # Adicionar membros da diretoria presentes
            for membro in self.object.membros_presentes.all():
                membro_data = {
                    'id': membro.id,
                    'associado_id': membro.associado.id,
                    'associado_nome': membro.associado.nome,
                    'cargo_nome': membro.cargo.nome,
                    'tipo': 'membro_diretoria'
                }
                print(f"DEBUG ADICIONAR: Membro da diretoria: {membro_data}")
                membros_presentes.append(membro_data)
            
            # Adicionar associados presentes (não membros da diretoria)
            for associado in self.object.associados_presentes.all():
                associado_data = {
                    'id': associado.id,
                    'associado_id': associado.id,
                    'associado_nome': associado.nome,
                    'cargo_nome': 'Associado',
                    'tipo': 'associado'
                }
                print(f"DEBUG ADICIONAR: Associado comum: {associado_data}")
                membros_presentes.append(associado_data)
            
            print(f"DEBUG ADICIONAR: Lista final: {membros_presentes}")
            
            return JsonResponse({
                'success': True,
                'membros_presentes': membros_presentes
            })
            
        except Associado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Associado não encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    def remover_membro_presente(self, data):
        """
        Remover membro da lista de presentes
        """
        from django.http import JsonResponse
        from associados.models import Associado
        
        try:
            associado_id = data.get('associado_id')
            associado = Associado.objects.get(id=associado_id, ativo=True)
            
            # Verificar se é membro da diretoria
            membro_diretoria = MembroDiretoria.objects.filter(
                associado=associado, 
                ativo=True
            ).first()
            
            if membro_diretoria:
                # Remover da lista de membros presentes
                self.object.membros_presentes.remove(membro_diretoria)
            else:
                # Remover da lista de associados presentes
                self.object.associados_presentes.remove(associado)
            
            # Preparar dados para resposta
            membros_presentes = []
            
            # Adicionar membros da diretoria presentes
            for membro in self.object.membros_presentes.all():
                membros_presentes.append({
                    'id': membro.id,
                    'associado_id': membro.associado.id,
                    'associado_nome': membro.associado.nome,
                    'cargo_nome': membro.cargo.nome,
                    'tipo': 'membro_diretoria'
                })
            
            # Adicionar associados presentes (não membros da diretoria)
            for associado in self.object.associados_presentes.all():
                membros_presentes.append({
                    'id': associado.id,
                    'associado_id': associado.id,
                    'associado_nome': associado.nome,
                    'cargo_nome': 'Associado',
                    'tipo': 'associado'
                })
            
            return JsonResponse({
                'success': True,
                'membros_presentes': membros_presentes
            })
            
        except Associado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Associado não encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })


class AtaReuniaoCreateView(LoginRequiredMixin, CreateView):
    """
    Criar nova ata de reunião com editor avançado
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_avancado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = None
        context['template_form'] = AtaReuniaoTemplateForm()
        context['is_creating'] = True
        context['membros_diretoria'] = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
        return context
    
    def form_valid(self, form):
        # Debug: verificar se o formulário tem dados
        print("=" * 50)
        print("DEBUG FORM_VALID")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Form cleaned_data: {form.cleaned_data}")
        print(f"Form errors: {form.errors}")
        print(f"Form non_field_errors: {form.non_field_errors()}")
        print("=" * 50)
        
        try:
            # Gerar número sequencial automaticamente
            if not form.instance.numero_sequencial:
                form.instance.numero_sequencial = form.instance.gerar_numero_sequencial()
            
            # Salvar a ata (os campos data_criacao e data_atualizacao são automáticos)
            response = super().form_valid(form)
            print(f"Ata salva com sucesso! ID: {self.object.pk}")
            print(f"Número da ata: {self.object.get_numero_formatado()}")
            messages.success(
                self.request, 
                f'Ata "{form.instance.titulo}" criada com sucesso! Número: {self.object.get_numero_formatado()}'
            )
            return response
        except Exception as e:
            print(f"Erro ao salvar ata: {e}")
            messages.error(
                self.request, 
                f'Erro ao salvar ata: {e}'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Debug: verificar erros de validação
        print(f"Form is invalid. Errors: {form.errors}")
        print(f"Form data: {form.data}")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_edit', kwargs={'pk': self.object.pk})


class AtaReuniaoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar ata de reunião com editor avançado
    """
    model = AtaReuniao
    form_class = AtaReuniaoEditorForm
    template_name = 'diretoria/ata_editor_avancado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ata'] = self.object
        context['template_form'] = AtaReuniaoTemplateForm()
        context['is_creating'] = False
        context['membros_diretoria'] = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
        return context
    
    def form_valid(self, form):
        # Salvar a ata (o campo data_atualizacao é automático)
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Ata "{form.instance.titulo}" atualizada com sucesso!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_editor_edit', kwargs={'pk': self.object.pk})


class AtaReuniaoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir ata de reunião
    """
    model = AtaReuniao
    template_name = 'diretoria/ata_confirm_delete.html'
    success_url = reverse_lazy('diretoria:ata_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ata excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class ResolucaoDiretoriaListView(LoginRequiredMixin, ListView):
    """
    Lista de resoluções da diretoria
    """
    model = ResolucaoDiretoria
    template_name = 'diretoria/resolucao_list.html'
    context_object_name = 'resolucoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ResolucaoDiretoria.objects.select_related('ata_reuniao')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(titulo__icontains=search) |
                Q(ementa__icontains=search)
            )
        
        # Filtro por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por ano
        ano = self.request.GET.get('ano')
        if ano:
            queryset = queryset.filter(data_resolucao__year=ano)
        
        return queryset.order_by('-data_resolucao', '-numero')


class ResolucaoDiretoriaDetailView(LoginRequiredMixin, DetailView):
    """
    Detalhes da resolução da diretoria
    """
    model = ResolucaoDiretoria
    template_name = 'diretoria/resolucao_detail.html'
    context_object_name = 'resolucao'


class ResolucaoDiretoriaCreateView(LoginRequiredMixin, CreateView):
    """
    Criar nova resolução da diretoria
    """
    model = ResolucaoDiretoria
    form_class = ResolucaoDiretoriaForm
    template_name = 'diretoria/resolucao_form.html'
    success_url = reverse_lazy('diretoria:resolucao_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Resolução criada com sucesso!')
        return super().form_valid(form)


class ResolucaoDiretoriaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editar resolução da diretoria
    """
    model = ResolucaoDiretoria
    form_class = ResolucaoDiretoriaForm
    template_name = 'diretoria/resolucao_form.html'
    success_url = reverse_lazy('diretoria:resolucao_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Resolução atualizada com sucesso!')
        return super().form_valid(form)


class ResolucaoDiretoriaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Excluir resolução da diretoria
    """
    model = ResolucaoDiretoria
    template_name = 'diretoria/resolucao_confirm_delete.html'
    success_url = reverse_lazy('diretoria:resolucao_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Resolução excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views AJAX para autocomplete
@login_required
def buscar_associados_ajax(request):
    """
    Buscar associados para autocomplete
    """
    from associados.models import Associado
    from django.http import JsonResponse
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    associados = Associado.objects.filter(
        Q(nome__icontains=query) | Q(cpf__icontains=query)
    ).values('id', 'nome', 'cpf', 'matricula_militar')[:10]
    
    results = []
    for associado in associados:
        results.append({
            'id': associado['id'],
            'text': f"{associado['nome']} - CPF: {associado['cpf'] or 'N/A'} - Matrícula: {associado['matricula_militar'] or 'N/A'}"
        })
    
    return JsonResponse({'results': results})


@login_required
def buscar_cargos_ajax(request):
    """
    Buscar cargos para autocomplete
    """
    from django.http import JsonResponse
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    cargos = CargoDiretoria.objects.filter(
        Q(nome__icontains=query) | Q(descricao__icontains=query),
        ativo=True
    ).values('id', 'nome', 'descricao')[:10]
    
    results = []
    for cargo in cargos:
        results.append({
            'id': cargo['id'],
            'text': f"{cargo['nome']} - {cargo['descricao'] or 'Sem descrição'}"
        })
    
    return JsonResponse({'results': results})


# Views para Modelos de Ata
@login_required
def listar_modelos_ata(request):
    """
    Listar modelos de ata disponíveis para AJAX
    """
    try:
        # Buscar modelos que o usuário pode acessar
        modelos = ModeloAta.objects.filter(
            Q(publico=True) | Q(criado_por=request.user),
            ativo=True
        ).order_by('-data_criacao')
        
        # Aplicar filtros
        search = request.GET.get('search', '')
        if search:
            modelos = modelos.filter(
                Q(nome__icontains=search) | 
                Q(descricao__icontains=search)
            )
        
        categoria = request.GET.get('categoria', '')
        if categoria:
            modelos = modelos.filter(categoria=categoria)
        
        # Renderizar apenas os cards dos modelos
        context = {
            'modelos': modelos,
            'categorias': ModeloAta.CATEGORIA_CHOICES,
            'categoria_atual': categoria,
            'search': search
        }
        
        return render(request, 'diretoria/modelos_ata_list.html', context)
        
    except Exception as e:
        return render(request, 'diretoria/modelos_ata_list.html', {
            'modelos': [],
            'error': str(e)
        })


@login_required
def salvar_modelo_ata(request):
    """
    Salvar modelo de ata via AJAX
    """
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            categoria = request.POST.get('categoria', 'geral')
            publico = request.POST.get('publico') == 'true'
            conteudo = request.POST.get('conteudo', '').strip()
            
            if not nome:
                return JsonResponse({
                    'success': False,
                    'message': 'Nome do modelo é obrigatório.'
                })
            
            if not conteudo:
                return JsonResponse({
                    'success': False,
                    'message': 'Conteúdo do modelo é obrigatório.'
                })
            
            # Criar modelo
            modelo = ModeloAta.objects.create(
                nome=nome,
                descricao=descricao,
                categoria=categoria,
                conteudo=conteudo,
                publico=publico,
                criado_por=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Modelo salvo com sucesso!',
                'modelo_id': modelo.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao salvar modelo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido.'
    })


@login_required
def obter_modelo_ata(request, modelo_id):
    """
    Obter conteúdo de um modelo específico
    """
    try:
        modelo = get_object_or_404(
            ModeloAta,
            id=modelo_id,
            ativo=True
        )
        
        # Verificar se o usuário pode acessar o modelo
        if not modelo.publico and modelo.criado_por != request.user:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para acessar este modelo.'
            })
        
        return JsonResponse({
            'success': True,
            'conteudo': modelo.conteudo,
            'nome': modelo.nome
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter modelo: {str(e)}'
        })