from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from core.models import LogAtividade
from .models import PreCadastroAssociado


class PreCadastroListView(LoginRequiredMixin, ListView):
    """
    Lista de pré-cadastros pendentes de aprovação
    """
    model = PreCadastroAssociado
    template_name = 'associados/pre_cadastro_list.html'
    context_object_name = 'pre_cadastros'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PreCadastroAssociado.objects.filter(status='pendente').order_by('-data_solicitacao')
        
        # Filtros de busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(cpf__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Pré-Cadastros Pendentes'
        context['subtitle'] = 'Aguardando Aprovação'
        context['search'] = self.request.GET.get('search', '')
        return context


@login_required
def pre_cadastro_detail(request, pk):
    """
    Detalhes de um pré-cadastro específico
    """
    pre_cadastro = get_object_or_404(PreCadastroAssociado, pk=pk)
    
    # Carregar dependentes relacionados
    dependentes = pre_cadastro.dependentes.all()
    
    context = {
        'pre_cadastro': pre_cadastro,
        'dependentes': dependentes,
        'title': f'Pré-Cadastro - {pre_cadastro.nome}',
        'subtitle': 'Detalhes do Pré-Cadastro'
    }
    
    return render(request, 'associados/pre_cadastro_detail.html', context)


@login_required
def aprovar_pre_cadastro(request, pk):
    """
    Aprova um pré-cadastro e o converte para associado
    """
    pre_cadastro = get_object_or_404(PreCadastroAssociado, pk=pk, status='pendente')
    
    try:
        # Contar dependentes e documentos antes da conversão
        num_dependentes = pre_cadastro.dependentes.count()
        num_documentos = 0
        if pre_cadastro.copia_rg:
            num_documentos += 1
        if pre_cadastro.copia_cpf:
            num_documentos += 1
        if pre_cadastro.comprovante_residencia:
            num_documentos += 1
        
        # Converter para associado
        associado = pre_cadastro.converter_para_associado(request.user)
        
        # Mensagem detalhada de sucesso
        mensagem = f'Pré-cadastro de {pre_cadastro.nome} aprovado com sucesso! '
        mensagem += f'Associado criado com ID: {associado.id}'
        
        if num_dependentes > 0:
            mensagem += f' | {num_dependentes} dependente(s) transferido(s)'
        
        if num_documentos > 0:
            mensagem += f' | {num_documentos} documento(s) transferido(s)'
        
        messages.success(request, mensagem)
        
        # Log da atividade
        detalhes_log = f'Aprovou pré-cadastro de {pre_cadastro.nome} (ID: {pre_cadastro.id}) e converteu para associado ID: {associado.id}'
        if num_dependentes > 0:
            detalhes_log += f'. Transferidos {num_dependentes} dependentes'
        if num_documentos > 0:
            detalhes_log += f'. Transferidos {num_documentos} documentos'
        
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Aprovar pré-cadastro',
            detalhes=detalhes_log,
            modulo='associados'
        )
        
    except Exception as e:
        messages.error(request, f'Erro ao aprovar pré-cadastro: {str(e)}')
    
    return redirect('associados:pre_cadastro_list')


@login_required
def rejeitar_pre_cadastro(request, pk):
    """
    Rejeita um pré-cadastro
    """
    pre_cadastro = get_object_or_404(PreCadastroAssociado, pk=pk, status='pendente')
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        
        # Atualizar status
        pre_cadastro.status = 'rejeitado'
        pre_cadastro.data_analise = timezone.now()
        pre_cadastro.analisado_por = request.user
        pre_cadastro.observacoes = f"{pre_cadastro.observacoes or ''}\n\nRejeitado em {timezone.now().strftime('%d/%m/%Y às %H:%M')} por {request.user.get_full_name() or request.user.username}.\nMotivo: {motivo}"
        pre_cadastro.save()
        
        messages.success(request, f'Pré-cadastro de {pre_cadastro.nome} rejeitado com sucesso!')
        
        # Log da atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Rejeitar pré-cadastro',
            detalhes=f'Rejeitou pré-cadastro de {pre_cadastro.nome} (ID: {pre_cadastro.id}). Motivo: {motivo}',
            modulo='associados'
        )
        
        return redirect('associados:pre_cadastro_list')
    
    context = {
        'pre_cadastro': pre_cadastro,
        'title': f'Rejeitar Pré-Cadastro - {pre_cadastro.nome}',
        'subtitle': 'Confirmar Rejeição'
    }
    
    return render(request, 'associados/pre_cadastro_rejeitar.html', context)


@login_required
def pre_cadastro_historico(request):
    """
    Histórico de todos os pré-cadastros (aprovados e rejeitados)
    """
    queryset = PreCadastroAssociado.objects.exclude(status='pendente').order_by('-data_analise')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(nome__icontains=search) |
            Q(cpf__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    pre_cadastros = paginator.get_page(page_number)
    
    context = {
        'pre_cadastros': pre_cadastros,
        'title': 'Histórico de Pré-Cadastros',
        'subtitle': 'Aprovados e Rejeitados',
        'search': search,
        'status_filter': status_filter,
        'status_choices': PreCadastroAssociado.STATUS_CHOICES
    }
    
    return render(request, 'associados/pre_cadastro_historico.html', context)
