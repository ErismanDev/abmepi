from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from datetime import date, timedelta
import csv
from decimal import Decimal
from datetime import datetime

from .models import TipoMensalidade, Mensalidade, Pagamento, Despesa, RelatorioFinanceiro, ConfiguracaoCobranca
from .forms import (
    TipoMensalidadeForm, MensalidadeForm, PagamentoForm, DespesaForm,
    MensalidadeSearchForm, DespesaSearchForm, ConfiguracaoCobrancaForm
)
from associados.models import Associado


# Dashboard Financeiro
@login_required
def dashboard_financeiro(request):
    """
    Dashboard principal do módulo financeiro
    """
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Estatísticas de mensalidades de associados (recorrentes)
    mensalidades_associados_mes = Mensalidade.objects.filter(
        data_vencimento__month=mes_atual,
        data_vencimento__year=ano_atual,
        tipo__categoria='mensalidade'
    )
    
    total_mensalidades_associados = mensalidades_associados_mes.aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    mensalidades_associados_pagas = mensalidades_associados_mes.filter(status='pago').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    mensalidades_associados_pendentes = mensalidades_associados_mes.filter(status='pendente').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    mensalidades_associados_atrasadas = mensalidades_associados_mes.filter(
        status='pendente',
        data_vencimento__lt=hoje
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    # Estatísticas de despesas
    despesas_mes = Despesa.objects.filter(
        data_despesa__month=mes_atual,
        data_despesa__year=ano_atual
    )
    
    total_despesas = despesas_mes.aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    despesas_pagas = despesas_mes.filter(pago=True).aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    # Cálculo do saldo (incluindo todos os recebimentos)
    total_receitas_pagas = mensalidades_associados_pagas
    saldo_mes = total_receitas_pagas - despesas_pagas
    
    # Mensalidades vencendo em breve
    proximos_vencimentos = Mensalidade.objects.filter(
        status='pendente',
        data_vencimento__gte=hoje,
        data_vencimento__lte=hoje + timedelta(days=7)
    ).select_related('associado', 'tipo').order_by('data_vencimento')[:10]
    
    # Mensalidades em atraso
    mensalidades_atraso = Mensalidade.objects.filter(
        status='pendente',
        data_vencimento__lt=hoje
    ).select_related('associado', 'tipo').order_by('data_vencimento')[:10]
    
    # Gráfico de receitas por mês (últimos 12 meses)
    receitas_por_mes = []
    for i in range(12):
        mes = hoje - timedelta(days=30*i)
        receita = Mensalidade.objects.filter(
            status='pago',
            data_pagamento__month=mes.month,
            data_pagamento__year=mes.year
        ).aggregate(total=Sum('valor'))['total'] or 0
        receitas_por_mes.append({
            'mes': mes.strftime('%b/%Y'),
            'valor': float(receita)
        })
    
    receitas_por_mes.reverse()
    
    context = {
        # Mensalidades de associados
        'total_mensalidades_associados': total_mensalidades_associados,
        'mensalidades_associados_pagas': mensalidades_associados_pagas,
        'mensalidades_associados_pendentes': mensalidades_associados_pendentes,
        'mensalidades_associados_atrasadas': mensalidades_associados_atrasadas,
        
        # Despesas e saldo
        'total_despesas': total_despesas,
        'despesas_pagas': despesas_pagas,
        'saldo_mes': saldo_mes,
        
        # Outros dados
        'proximos_vencimentos': proximos_vencimentos,
        'mensalidades_atraso': mensalidades_atraso,
        'receitas_por_mes': receitas_por_mes,
    }
    
    return render(request, 'financeiro/dashboard.html', context)


# Views para Tipos de Mensalidade
class TipoMensalidadeListView(LoginRequiredMixin, ListView):
    model = TipoMensalidade
    template_name = 'financeiro/tipo_recebimento_list.html'
    context_object_name = 'tipos_mensalidade'
    paginate_by = 20
    ordering = ['nome']


class TipoMensalidadeCreateView(LoginRequiredMixin, CreateView):
    model = TipoMensalidade
    form_class = TipoMensalidadeForm
    template_name = 'financeiro/tipo_recebimento_form.html'
    success_url = reverse_lazy('financeiro:tipo_mensalidade_list')
    
    def form_valid(self, form):
        try:
            result = super().form_valid(form)
            messages.success(self.request, 'Tipo de mensalidade criado com sucesso!')
            return result
        except Exception as e:
            messages.error(self.request, f'Erro ao criar tipo de mensalidade: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


class TipoMensalidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoMensalidade
    form_class = TipoMensalidadeForm
    template_name = 'financeiro/tipo_recebimento_form.html'
    success_url = reverse_lazy('financeiro:tipo_mensalidade_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Tipo de mensalidade atualizado com sucesso!')
        return super().form_valid(form)


class TipoMensalidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoMensalidade
    template_name = 'financeiro/tipo_recebimento_confirm_delete.html'
    success_url = reverse_lazy('financeiro:tipo_mensalidade_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tipo de mensalidade excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Mensalidades
class MensalidadeListView(LoginRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 25
    ordering = ['-data_vencimento']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('associado', 'tipo')
        # Filtrar apenas mensalidades de associados (recorrentes)
        queryset = queryset.filter(tipo__categoria='mensalidade')
        
        form = MensalidadeSearchForm(self.request.GET)
        if form.is_valid():
            associado = form.cleaned_data.get('associado')
            status = form.cleaned_data.get('status')
            tipo = form.cleaned_data.get('tipo')
            data_inicio = form.cleaned_data.get('data_inicio')
            data_fim = form.cleaned_data.get('data_fim')
            
            if associado:
                queryset = queryset.filter(
                    Q(associado__nome__icontains=associado) |
                    Q(associado__cpf__icontains=associado)
                )
            
            if status:
                queryset = queryset.filter(status=status)
            
            if tipo:
                queryset = queryset.filter(tipo=tipo)
            
            if data_inicio:
                queryset = queryset.filter(data_vencimento__gte=data_inicio)
            
            if data_fim:
                queryset = queryset.filter(data_vencimento__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MensalidadeSearchForm(self.request.GET)
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_recebiveis'] = queryset.aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pagos'] = queryset.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pendentes'] = queryset.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_atrasados'] = queryset.filter(
            status='pendente',
            data_vencimento__lt=date.today()
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Dados para o modal de geração em lote
        from .models import TipoMensalidade
        context['tipos_mensalidade'] = TipoMensalidade.objects.filter(ativo=True, categoria='mensalidade').order_by('nome')
        
        # Associados ativos para seleção no modal
        from associados.models import Associado
        context['associados_ativos'] = Associado.objects.filter(ativo=True).order_by('nome')
        
        # Anos disponíveis (atual e próximos 2 anos)
        ano_atual = date.today().year
        context['anos_disponiveis'] = range(ano_atual, ano_atual + 3)
        
        return context


class MensalidadeCreateView(LoginRequiredMixin, CreateView):
    model = Mensalidade
    form_class = MensalidadeForm
    template_name = 'financeiro/mensalidade_form.html'
    success_url = reverse_lazy('financeiro:mensalidade_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar dados dos tipos de mensalidade para o JavaScript
        from .models import TipoMensalidade
        tipos = TipoMensalidade.objects.filter(ativo=True).values('id', 'nome', 'descricao', 'valor', 'recorrente')
        context['tipos_json'] = list(tipos)
        return context
    
    def form_valid(self, form):
        mensalidade = form.save(commit=False)
        
        # Salvar a mensalidade
        mensalidade.save()
        
        messages.success(self.request, 'Recebível criado com sucesso!')
        return redirect('financeiro:mensalidade_list')


class MensalidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = Mensalidade
    form_class = MensalidadeForm
    template_name = 'financeiro/mensalidade_form.html'
    success_url = reverse_lazy('financeiro:mensalidade_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar dados dos tipos de mensalidade para o JavaScript
        from .models import TipoMensalidade
        tipos = TipoMensalidade.objects.filter(ativo=True).values('id', 'nome', 'descricao', 'valor', 'recorrente')
        context['tipos_json'] = list(tipos)
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        # Para edição, garantir que o valor seja preenchido baseado no tipo
        if self.object and self.object.tipo:
            initial['valor'] = self.object.tipo.valor
        
        # Para edição, garantir que a data de vencimento seja preservada
        if self.object and self.object.data_vencimento:
            # Converter a data para o formato YYYY-MM-DD para compatibilidade com input type="date"
            from datetime import datetime
            if isinstance(self.object.data_vencimento, str):
                try:
                    # Se for string, tentar converter para datetime
                    data_obj = datetime.strptime(self.object.data_vencimento, '%Y-%m-%d').date()
                    initial['data_vencimento'] = data_obj
                except ValueError:
                    initial['data_vencimento'] = self.object.data_vencimento
            else:
                initial['data_vencimento'] = self.object.data_vencimento
        
        return initial
    
    def form_valid(self, form):
        mensalidade = form.save(commit=False)
        
        # Salvar a mensalidade
        mensalidade.save()
        
        messages.success(self.request, 'Recebível atualizado com sucesso!')
        return redirect('financeiro:mensalidade_list')


class MensalidadeDetailView(LoginRequiredMixin, DetailView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_detail.html'
    context_object_name = 'mensalidade'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagamentos'] = self.object.pagamentos.all().order_by('-data_pagamento')
        context['today'] = date.today()
        return context


class MensalidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_confirm_delete.html'
    success_url = reverse_lazy('financeiro:mensalidade_list')
    
    def delete(self, request, *args, **kwargs):
        mensalidade = self.get_object()
        
        messages.success(request, 'Mensalidade excluída com sucesso!')
        return redirect('financeiro:mensalidade_list')


# Views para Pagamentos
class PagamentoCreateView(LoginRequiredMixin, CreateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'financeiro/pagamento_form.html'
    success_url = reverse_lazy('financeiro:mensalidade_list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Aceitar tanto 'mensalidade' quanto 'recebimento' como parâmetros
        mensalidade_id = self.request.GET.get('mensalidade') or self.request.GET.get('recebimento')
        if mensalidade_id:
            try:
                mensalidade = Mensalidade.objects.get(pk=mensalidade_id)
                initial['mensalidade'] = mensalidade
            except Mensalidade.DoesNotExist:
                pass
        
        # Definir data atual como padrão
        from datetime import datetime
        initial['data_pagamento'] = datetime.now()
        
        return initial
    
    def form_valid(self, form):
        pagamento = form.save(commit=False)
        pagamento.usuario_registro = self.request.user
        
        # Atualizar status da mensalidade
        mensalidade = pagamento.mensalidade
        mensalidade.status = 'pago'
        mensalidade.data_pagamento = timezone.now().date()
        mensalidade.save()
        
        pagamento.save()
        
        messages.success(self.request, 'Pagamento registrado com sucesso!')
        return redirect('financeiro:mensalidade_list')


# Views para Despesas
class DespesaListView(LoginRequiredMixin, ListView):
    model = Despesa
    template_name = 'financeiro/despesa_list.html'
    context_object_name = 'despesas'
    paginate_by = 25
    ordering = ['-data_despesa']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = DespesaSearchForm(self.request.GET)
        
        if form.is_valid():
            descricao = form.cleaned_data.get('descricao')
            categoria = form.cleaned_data.get('categoria')
            fornecedor = form.cleaned_data.get('fornecedor')
            pago = form.cleaned_data.get('pago')
            data_inicio = form.cleaned_data.get('data_inicio')
            data_fim = form.cleaned_data.get('data_fim')
            
            if descricao:
                queryset = queryset.filter(descricao__icontains=descricao)
            
            if categoria:
                queryset = queryset.filter(categoria=categoria)
            
            if fornecedor:
                queryset = queryset.filter(fornecedor__icontains=fornecedor)
            
            if pago:
                queryset = queryset.filter(pago=pago == 'True')
            
            if data_inicio:
                queryset = queryset.filter(data_despesa__gte=data_inicio)
            
            if data_fim:
                queryset = queryset.filter(data_despesa__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DespesaSearchForm(self.request.GET)
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_despesas'] = queryset.aggregate(total=Sum('valor'))['total'] or 0
        context['despesas_pagas'] = queryset.filter(pago=True).aggregate(total=Sum('valor'))['total'] or 0
        context['despesas_pendentes'] = queryset.filter(pago=False).aggregate(total=Sum('valor'))['total'] or 0
        
        return context


class DespesaCreateView(LoginRequiredMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'financeiro/despesa_form.html'
    success_url = reverse_lazy('financeiro:despesa_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Despesa criada com sucesso!')
        return super().form_valid(form)


class DespesaUpdateView(LoginRequiredMixin, UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'financeiro/despesa_form.html'
    success_url = reverse_lazy('financeiro:despesa_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Despesa atualizada com sucesso!')
        return super().form_valid(form)


class DespesaDeleteView(LoginRequiredMixin, DeleteView):
    model = Despesa
    template_name = 'financeiro/despesa_confirm_delete.html'
    success_url = reverse_lazy('financeiro:despesa_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Despesa excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class DespesaDetailView(LoginRequiredMixin, DetailView):
    model = Despesa
    template_name = 'financeiro/despesa_detail.html'
    context_object_name = 'despesa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context


@login_required
def dar_baixa_despesa(request, pk):
    """
    Marca uma despesa como paga (dá baixa)
    """
    try:
        despesa = Despesa.objects.get(pk=pk)
        
        if request.method == 'POST':
            if not despesa.pago:
                despesa.pago = True
                despesa.save()
                messages.success(request, f'Despesa "{despesa.descricao}" marcada como paga com sucesso!')
            else:
                messages.warning(request, 'Esta despesa já está marcada como paga.')
            
            return redirect('financeiro:despesa_detail', pk=pk)
        
        # Se for GET, redireciona para a página de detalhes
        return redirect('financeiro:despesa_detail', pk=pk)
        
    except Despesa.DoesNotExist:
        messages.error(request, 'Despesa não encontrada.')
        return redirect('financeiro:despesa_list')


# Exportação de dados
@login_required
def export_mensalidades_csv(request):
    """
    Exporta mensalidades para CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mensalidades.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Associado', 'CPF', 'Tipo', 'Valor', 'Data Vencimento', 
        'Status', 'Data Pagamento', 'Forma Pagamento', 'Observações'
    ])
    
    mensalidades = Mensalidade.objects.select_related('associado', 'tipo').all()
    
    for mensalidade in mensalidades:
        writer.writerow([
            mensalidade.associado.nome,
            mensalidade.associado.cpf,
            mensalidade.tipo.nome,
            mensalidade.valor,
            mensalidade.data_vencimento.strftime('%d/%m/%Y'),
            mensalidade.get_status_display(),
            mensalidade.data_pagamento.strftime('%d/%m/%Y') if mensalidade.data_pagamento else '',
            mensalidade.forma_pagamento or '',
            mensalidade.observacoes or ''
        ])
    
    return response


@login_required
def export_despesas_csv(request):
    """
    Exporta despesas para CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="despesas.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Descrição', 'Categoria', 'Valor', 'Data Despesa', 'Data Vencimento',
        'Pago', 'Fornecedor', 'Nota Fiscal', 'Observações'
    ])
    
    despesas = Despesa.objects.all()
    
    for despesa in despesas:
        writer.writerow([
            despesa.descricao,
            despesa.get_categoria_display(),
            despesa.valor,
            despesa.data_despesa.strftime('%d/%m/%Y'),
            despesa.data_vencimento.strftime('%d/%m/%Y') if despesa.data_vencimento else '',
            'Sim' if despesa.pago else 'Não',
            despesa.fornecedor or '',
            despesa.nota_fiscal or '',
            despesa.observacoes or ''
        ])
    
    return response


# Geração automática de mensalidades
@login_required
def gerar_mensalidades_mensais(request):
    """
    Gera mensalidades mensais para todos os associados ativos
    """
    if request.method == 'POST':
        try:
            mes = int(request.POST.get('mes'))
            ano = int(request.POST.get('ano'))
            quantidade_meses = int(request.POST.get('quantidade_meses', 1))
            
            # Buscar tipos de mensalidade recorrentes
            tipos_recorrentes = TipoMensalidade.objects.filter(ativo=True, recorrente=True)
            
            # Buscar associados ativos
            associados_ativos = Associado.objects.filter(ativo=True)
            
            mensalidades_criadas = 0
            
            # Gerar mensalidades para cada mês
            for i in range(quantidade_meses):
                mes_atual = mes + i
                ano_atual = ano
                
                # Ajustar mês e ano se passar de dezembro
                if mes_atual > 12:
                    mes_atual = mes_atual - 12
                    ano_atual = ano + 1
                
                for associado in associados_ativos:
                    for tipo in tipos_recorrentes:
                        # Verificar se já existe mensalidade para este mês/ano
                        if not Mensalidade.objects.filter(
                            associado=associado,
                            tipo=tipo,
                            data_vencimento__month=mes_atual,
                            data_vencimento__year=ano_atual
                        ).exists():
                            # Calcular data de vencimento (dia 10 do mês)
                            data_vencimento = date(ano_atual, mes_atual, 10)
                            
                            Mensalidade.objects.create(
                                associado=associado,
                                tipo=tipo,
                                valor=tipo.valor,
                                data_vencimento=data_vencimento,
                                status='pendente'
                            )
                            mensalidades_criadas += 1
            
            if quantidade_meses == 1:
                messages.success(
                    request, 
                    f'{mensalidades_criadas} mensalidades foram geradas para {mes}/{ano}!'
                )
            else:
                messages.success(
                    request, 
                    f'{mensalidades_criadas} mensalidades foram geradas para {quantidade_meses} mês(es) a partir de {mes}/{ano}!'
                )
            
        except (ValueError, TypeError):
            messages.error(request, 'Dados inválidos fornecidos.')
        except Exception as e:
            messages.error(request, f'Erro ao gerar mensalidades: {str(e)}')
    
    return redirect('financeiro:mensalidade_list')


# Views para Gerenciamento em Lote
@login_required
def gerar_mensalidades_lote(request):
    """
    Gera mensalidades em lote para associados selecionados ou todos os ativos
    """
    if request.method == 'POST':
        try:
            mes_inicial = int(request.POST.get('mes_inicial'))
            ano = int(request.POST.get('ano'))
            quantidade_meses = int(request.POST.get('quantidade_meses'))
            dia_vencimento = int(request.POST.get('dia_vencimento'))
            tipo_id = int(request.POST.get('tipo_mensalidade'))
            tipo_geracao = request.POST.get('tipo_geracao', 'todos')
            
            # Validar dados
            if not (1 <= mes_inicial <= 12 and 2020 <= ano <= 2030 and 1 <= dia_vencimento <= 31 and 1 <= quantidade_meses <= 12):
                messages.error(request, 'Dados inválidos fornecidos.')
                return redirect('financeiro:mensalidade_list')
            
            # Buscar tipo de mensalidade
            try:
                tipo = TipoMensalidade.objects.get(id=tipo_id, ativo=True, categoria='mensalidade')
            except TipoMensalidade.DoesNotExist:
                messages.error(request, 'Tipo de mensalidade inválido.')
                return redirect('financeiro:mensalidade_list')
            
            # Determinar quais associados usar
            if tipo_geracao == 'selecionados':
                associados_ids = request.POST.getlist('associados')
                if not associados_ids:
                    messages.error(request, 'Nenhum associado foi selecionado.')
                    return redirect('financeiro:mensalidade_list')
                associados_ativos = Associado.objects.filter(id__in=associados_ids, ativo=True)
            else:
                # Todos os associados ativos
                associados_ativos = Associado.objects.filter(ativo=True)
            
            mensalidades_criadas = 0
            mensalidades_duplicadas = 0
            
            # Gerar mensalidades para cada mês
            for i in range(quantidade_meses):
                mes_atual = mes_inicial + i
                ano_atual = ano
                
                # Ajustar mês e ano se passar de dezembro
                if mes_atual > 12:
                    mes_atual = mes_atual - 12
                    ano_atual = ano + 1
                
                for associado in associados_ativos:
                    # Verificar se já existe mensalidade para este mês/ano
                    if not Mensalidade.objects.filter(
                        associado=associado,
                        tipo=tipo,
                        data_vencimento__month=mes_atual,
                        data_vencimento__year=ano_atual
                    ).exists():
                        # Calcular data de vencimento
                        try:
                            data_vencimento = date(ano_atual, mes_atual, dia_vencimento)
                        except ValueError:
                            # Se o dia não existe no mês, usar o último dia do mês
                            if mes_atual == 12:
                                data_vencimento = date(ano_atual + 1, 1, 1) - timedelta(days=1)
                            else:
                                data_vencimento = date(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
                        
                        Mensalidade.objects.create(
                            associado=associado,
                            tipo=tipo,
                            valor=tipo.valor,
                            data_vencimento=data_vencimento,
                            status='pendente'
                        )
                        mensalidades_criadas += 1
                    else:
                        mensalidades_duplicadas += 1
            
            if mensalidades_criadas > 0:
                if tipo_geracao == 'selecionados':
                    messages.success(
                        request, 
                        f'{mensalidades_criadas} mensalidades foram geradas para {len(associados_ativos)} associado(s) selecionado(s) em {quantidade_meses} mês(es) a partir de {mes_inicial}/{ano}!'
                    )
                else:
                    messages.success(
                        request, 
                        f'{mensalidades_criadas} mensalidades foram geradas para todos os associados ativos em {quantidade_meses} mês(es) a partir de {mes_inicial}/{ano}!'
                    )
            
            if mensalidades_duplicadas > 0:
                messages.warning(
                    request,
                    f'{mensalidades_duplicadas} mensalidades já existiam para o período.'
                )
            
        except (ValueError, TypeError):
            messages.error(request, 'Dados inválidos fornecidos.')
        except Exception as e:
            messages.error(request, f'Erro ao gerar mensalidades: {str(e)}')
    
    return redirect('financeiro:mensalidade_list')


@login_required
def gerar_mensalidades_associado_lote(request):
    """
    Gera mensalidades em lote para um associado específico
    """
    if request.method == 'POST':
        try:
            associado_id = int(request.POST.get('associado_id'))
            tipo_id = int(request.POST.get('tipo_recebimento'))
            valor = Decimal(request.POST.get('valor'))
            quantidade_parcelas = int(request.POST.get('quantidade_parcelas'))
            data_inicio = request.POST.get('data_inicio')
            dia_vencimento = int(request.POST.get('dia_vencimento'))
            intervalo_meses = int(request.POST.get('intervalo_meses', 1))
            
            # Validar dados
            if not (1 <= quantidade_parcelas <= 60 and valor > 0 and 1 <= dia_vencimento <= 31):
                return JsonResponse({
                    'success': False,
                    'error': 'Dados inválidos fornecidos.'
                })
            
            # Buscar associado
            try:
                associado = Associado.objects.get(id=associado_id, ativo=True)
            except Associado.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Associado não encontrado ou inativo.'
                })
            
            # Buscar tipo de recebimento
            try:
                tipo = TipoMensalidade.objects.get(id=tipo_id, ativo=True)
            except TipoMensalidade.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de recebimento não encontrado.'
                })
            
            # Converter data de início
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Data de início inválida.'
                })
            
            mensalidades_criadas = 0
            mensalidades_duplicadas = 0
            
            # Gerar mensalidades
            for i in range(quantidade_parcelas):
                # Calcular data de vencimento
                ano_atual = data_inicio.year
                mes_atual = data_inicio.month + (i * intervalo_meses)
                
                # Ajustar ano se o mês passar de 12
                while mes_atual > 12:
                    mes_atual -= 12
                    ano_atual += 1
                
                # Tentar criar a data com o dia especificado
                try:
                    data_vencimento = date(ano_atual, mes_atual, dia_vencimento)
                except ValueError:
                    # Se o dia não existe no mês, usar o último dia
                    if mes_atual == 12:
                        data_vencimento = date(ano_atual + 1, 1, 1) - timedelta(days=1)
                    else:
                        data_vencimento = date(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
                
                # Verificar se já existe mensalidade para esta data
                if not Mensalidade.objects.filter(
                    associado=associado,
                    tipo=tipo,
                    data_vencimento=data_vencimento
                ).exists():
                    Mensalidade.objects.create(
                        associado=associado,
                        tipo=tipo,
                        valor=valor,
                        data_vencimento=data_vencimento,
                        status='pendente'
                    )
                    mensalidades_criadas += 1
                else:
                    mensalidades_duplicadas += 1
            
            return JsonResponse({
                'success': True,
                'mensalidades_criadas': mensalidades_criadas,
                'mensalidades_duplicadas': mensalidades_duplicadas,
                'message': f'{mensalidades_criadas} mensalidades foram geradas com sucesso!'
            })
            
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Dados inválidos: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido.'
    })


@login_required
def excluir_mensalidades_associado_lote(request):
    """
    Exclui mensalidades em lote de um associado específico
    """
    if request.method == 'POST':
        try:
            # Debug: imprimir todo o POST
            print(f"DEBUG: request.POST completo: {dict(request.POST)}")
            print(f"DEBUG: request.POST.keys(): {list(request.POST.keys())}")
            
            associado_id = int(request.POST.get('associado_id'))
            print(f"DEBUG: associado_id extraído: {associado_id}")
            
            # Tentar obter mensalidades de diferentes formas
            mensalidade_ids = request.POST.getlist('mensalidades')
            print(f"DEBUG: getlist('mensalidades') retornou: {mensalidade_ids}")
            
            if not mensalidade_ids:
                # Tentar com mensalidades[] (formato do jQuery)
                mensalidade_ids = request.POST.getlist('mensalidades[]')
                print(f"DEBUG: getlist('mensalidades[]') retornou: {mensalidade_ids}")
            
            if not mensalidade_ids:
                # Se não funcionar com getlist, tentar com get e fazer split
                mensalidades_str = request.POST.get('mensalidades', '')
                print(f"DEBUG: get('mensalidades') retornou: {mensalidades_str}")
                
                if not mensalidades_str:
                    # Tentar com mensalidades[]
                    mensalidades_str = request.POST.get('mensalidades[]', '')
                    print(f"DEBUG: get('mensalidades[]') retornou: {mensalidades_str}")
                
                if mensalidades_str:
                    # Remover colchetes e aspas, e dividir por vírgula
                    mensalidades_str = mensalidades_str.strip('[]').replace('"', '').replace("'", '')
                    mensalidade_ids = [id.strip() for id in mensalidades_str.split(',') if id.strip()]
                    print(f"DEBUG: após parsing manual: {mensalidade_ids}")
            
            if not mensalidade_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhuma mensalidade foi selecionada.'
                })
            
            # Debug: imprimir os IDs recebidos
            print(f"DEBUG: mensalidade_ids final: {mensalidade_ids}")
            print(f"DEBUG: tipo de mensalidade_ids: {type(mensalidade_ids)}")
            
            # Buscar associado
            try:
                associado = Associado.objects.get(id=associado_id, ativo=True)
            except Associado.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Associado não encontrado ou inativo.'
                })
            
            # Buscar mensalidades do associado específico
            mensalidades = Mensalidade.objects.filter(
                id__in=mensalidade_ids,
                associado_id=associado_id
            )
            
            count = mensalidades.count()
            
            if count == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhuma mensalidade válida foi encontrada.'
                })
            
            # Excluir mensalidades
            mensalidades.delete()
            
            return JsonResponse({
                'success': True,
                'mensalidades_excluidas': count,
                'message': f'{count} mensalidade(s) foram excluída(s) com sucesso!'
            })
            
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Dados inválidos: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido.'
    })


@login_required
def excluir_mensalidades_lote(request):
    """
    Exclui mensalidades selecionadas em lote
    """
    if request.method == 'POST':
        mensalidade_ids = request.POST.getlist('mensalidades')
        
        if not mensalidade_ids:
            messages.error(request, 'Nenhuma mensalidade foi selecionada.')
            return redirect('financeiro:mensalidade_list')
        
        try:
            # Buscar mensalidades (apenas da categoria 'mensalidade')
            mensalidades = Mensalidade.objects.filter(
                id__in=mensalidade_ids,
                tipo__categoria='mensalidade'
            )
            
            count = mensalidades.count()
            
            if count == 0:
                messages.error(request, 'Nenhuma mensalidade válida foi encontrada.')
                return redirect('financeiro:mensalidade_list')
            
            # Excluir mensalidades
            mensalidades.delete()
            
            messages.success(
                request, 
                f'{count} mensalidade(s) foram excluída(s) com sucesso!'
            )
            
        except Exception as e:
            messages.error(request, f'Erro ao excluir mensalidades: {str(e)}')
    
    return redirect('financeiro:mensalidade_list')


@login_required
def gerar_carne_lote(request):
    """
    Gera carnê em PDF para mensalidades selecionadas
    """
    if request.method == 'POST':
        mensalidade_ids = request.POST.getlist('mensalidades')
        
        if not mensalidade_ids:
            messages.error(request, 'Nenhuma mensalidade foi selecionada.')
            return redirect('financeiro:mensalidade_list')
        
        try:
            # Buscar mensalidades (apenas da categoria 'mensalidade')
            mensalidades = Mensalidade.objects.filter(
                id__in=mensalidade_ids,
                tipo__categoria='mensalidade'
            ).select_related('associado', 'tipo').order_by('associado__nome', 'data_vencimento')
            
            if not mensalidades.exists():
                messages.error(request, 'Nenhuma mensalidade válida foi encontrada.')
                return redirect('financeiro:mensalidade_list')
            
            # Aqui você implementaria a geração do PDF
            # Por enquanto, vamos apenas mostrar uma mensagem de sucesso
            count = mensalidades.count()
            messages.success(
                request, 
                f'Carnê será gerado para {count} mensalidade(s). Funcionalidade em desenvolvimento.'
            )
            
        except Exception as e:
            messages.error(request, f'Erro ao gerar carnê: {str(e)}')
    
    return redirect('financeiro:mensalidade_list')


# Views para Mensalidades de Associados (Recorrentes)
class MensalidadeAssociadosListView(LoginRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_associados_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 25
    ordering = ['-data_vencimento']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('associado', 'tipo')
        # Filtrar apenas mensalidades de associados (recorrentes)
        queryset = queryset.filter(tipo__categoria='mensalidade')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estatísticas para recebíveis de associados
        queryset = self.get_queryset()
        context['total_recebiveis'] = queryset.aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pagos'] = queryset.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pendentes'] = queryset.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_atrasados'] = queryset.filter(
            status='pendente',
            data_vencimento__lt=date.today()
        ).aggregate(total=Sum('valor'))['total'] or 0
        return context


class MensalidadeAssociadoListView(LoginRequiredMixin, ListView):
    """
    View para listar mensalidades de um associado específico
    """
    model = Mensalidade
    template_name = 'financeiro/mensalidade_associado_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 25
    ordering = ['data_vencimento']  # Data mais próxima primeiro (vencimento mais próximo)
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('associado', 'tipo')
        associado_id = self.kwargs.get('associado_id')
        # Filtrar mensalidades do associado específico
        queryset = queryset.filter(associado_id=associado_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        associado_id = self.kwargs.get('associado_id')
        
        # Buscar o associado
        try:
            associado = Associado.objects.get(id=associado_id)
            context['associado'] = associado
        except Associado.DoesNotExist:
            context['associado'] = None
        
        # Estatísticas para o associado específico
        queryset = self.get_queryset()
        context['total_recebiveis'] = queryset.aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pagos'] = queryset.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_pendentes'] = queryset.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0
        context['recebiveis_atrasados'] = queryset.filter(
            status='pendente',
            data_vencimento__lt=date.today()
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Adicionar data atual para comparações no template
        context['today'] = date.today()
        
        # Adicionar tipos de recebimento para o modal de geração em lotes
        tipos_recebimento = TipoMensalidade.objects.filter(ativo=True).order_by('nome')
        context['tipos_recebimento'] = tipos_recebimento
        
        # Adicionar lista ordenada de dias para o modal
        context['dias_vencimento'] = list(range(1, 32))
        
        # Debug: verificar se os tipos estão sendo carregados
        # print(f"DEBUG: Tipos de recebimento encontrados: {tipos_recebimento.count()}")
        # for tipo in tipos_recebimento:
        #     print(f"DEBUG: Tipo - ID: {tipo.id}, Nome: {tipo.nome}, Valor: {tipo.valor}, Ativo: {tipo.ativo}")
        
        # Debug: verificar todos os tipos no banco
        # todos_tipos = TipoMensalidade.objects.all()
        # print(f"DEBUG: Total de tipos no banco: {todos_tipos.count()}")
        # for tipo in todos_tipos:
        #     print(f"DEBUG: Todos os tipos - ID: {tipo.id}, Nome: {tipo.nome}, Valor: {tipo.valor}, Ativo: {tipo.ativo}, Categoria: {tipo.categoria}")
        
        return context


@login_required
def dar_baixa_recebiveis_lote(request):
    """
    Dá baixa em recebíveis em lote de um associado específico
    """
    if request.method == 'POST':
        try:
            associado_id = int(request.POST.get('associado_id'))
            
            # Tentar obter mensalidades de diferentes formas
            mensalidade_ids = request.POST.getlist('mensalidades')
            if not mensalidade_ids:
                # Tentar com mensalidades[] (formato do jQuery)
                mensalidade_ids = request.POST.getlist('mensalidades[]')
            
            if not mensalidade_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum recebível foi selecionado.'
                })
            
            # Buscar associado
            try:
                associado = Associado.objects.get(id=associado_id, ativo=True)
            except Associado.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Associado não encontrado ou inativo.'
                })
            
            # Buscar recebíveis do associado específico (apenas pendentes)
            recebiveis = Mensalidade.objects.filter(
                id__in=mensalidade_ids,
                associado_id=associado_id,
                status='pendente'
            )
            
            count = recebiveis.count()
            
            if count == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum recebível pendente foi encontrado.'
                })
            
            # Dar baixa nos recebíveis (marcar como pagos)
            recebiveis.update(
                status='pago',
                data_pagamento=timezone.now().date()
            )
            
            return JsonResponse({
                'success': True,
                'recebiveis_baixados': count,
                'message': f'{count} recebível(s) foram baixados com sucesso!'
            })
            
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Dados inválidos: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido.'
    })


@login_required
def gerar_carne_associado(request, associado_id):
    """
    Gera carnê em PDF para mensalidades selecionadas de um associado específico
    """
    try:
        # Buscar o associado
        associado = Associado.objects.get(id=associado_id, ativo=True)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado ou inativo.')
        return redirect('financeiro:mensalidade_list')
    
    # Verificar se há mensalidades selecionadas na URL
    mensalidades_ids = request.GET.get('mensalidades', '')
    
    if mensalidades_ids:
        # Filtrar apenas as mensalidades selecionadas
        try:
            ids_lista = [int(id.strip()) for id in mensalidades_ids.split(',') if id.strip()]
            mensalidades = Mensalidade.objects.filter(
                id__in=ids_lista,
                associado=associado,
                status='pendente'
            ).select_related('tipo').order_by('data_vencimento')
        except (ValueError, TypeError):
            messages.error(request, 'IDs de mensalidades inválidos.')
            return redirect('financeiro:mensalidade_associado_list', associado_id=associado_id)
    else:
        # Se não houver seleção, buscar todas as mensalidades pendentes
        mensalidades = Mensalidade.objects.filter(
            associado=associado,
            status='pendente',
            tipo__categoria='mensalidade'
        ).select_related('tipo').order_by('data_vencimento')
    
    if not mensalidades.exists():
        if mensalidades_ids:
            messages.error(request, 'Nenhuma das mensalidades selecionadas foi encontrada ou está pendente.')
        else:
            messages.error(request, 'Nenhuma mensalidade pendente encontrada para este associado.')
        return redirect('financeiro:mensalidade_associado_list', associado_id=associado_id)
    
    try:
        # Importar a função gerar_carne
        from app.utils.carne_generator import gerar_carne
        
        print(f"DEBUG: Gerando carnê para {len(mensalidades)} mensalidades")
        print(f"DEBUG: Primeira mensalidade: {mensalidades.first()}")
        
        # Calcular dados para o carnê
        documento_inicial = mensalidades.first().id
        data_inicio = mensalidades.first().data_vencimento.strftime('%d/%m/%Y')
        meses = len(mensalidades)
        valor = mensalidades.first().valor
        
        print(f"DEBUG: documento_inicial={documento_inicial}, data_inicio={data_inicio}, meses={meses}, valor={valor}")
        
        # Verificar se todas as mensalidades têm o mesmo valor
        valores_diferentes = mensalidades.values_list('valor', flat=True).distinct()
        if len(valores_diferentes) > 1:
            # Se houver valores diferentes, usar o valor da primeira mensalidade
            # mas informar no PDF que há valores diferentes
            pass
        
        print(f"DEBUG: Chamando gerar_carne com nome_associado={associado.nome}")
        
        # Construir endereço completo a partir dos campos do associado
        endereco_completo = f"{associado.rua}, {associado.numero}"
        if associado.complemento:
            endereco_completo += f" - {associado.complemento}"
        endereco_completo += f" - {associado.bairro} - {associado.cidade}/{associado.estado} - CEP: {associado.cep}"
        
        # Gerar PDF usando a função gerar_carne com as mensalidades específicas
        # Obter configuração de cobrança
        config_cobranca = ConfiguracaoCobranca.get_configuracao_unica()
        
        pdf = gerar_carne(
            nome_associado=associado.nome,
            endereco=endereco_completo,
            mensalidades_lista=mensalidades,
            config_cobranca=config_cobranca
        )
        
        print(f"DEBUG: PDF gerado com sucesso! Tamanho: {len(pdf)} bytes")
        
        # Configurar resposta HTTP
        from datetime import datetime
        
        # Nome do arquivo com informações das mensalidades selecionadas
        if mensalidades_ids:
            filename = f"carne_{associado.nome.replace(' ', '_')}_{len(mensalidades)}_mensalidades_{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            filename = f"carne_{associado.nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('financeiro:mensalidade_associado_list', associado_id=associado_id)


# Views para Configuração de Cobrança
@login_required
def configuracao_cobranca_edit(request):
    """Formulário para editar a configuração única de cobrança via AJAX"""
    if request.method == 'POST':
        # Obter ou criar a configuração única
        config = ConfiguracaoCobranca.get_configuracao_unica()
        
        form = ConfiguracaoCobrancaForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    
    # GET request - retornar dados para edição
    config = ConfiguracaoCobranca.get_configuracao_unica()
    return JsonResponse({
        'success': True,
        'data': {
            'nome': config.nome,
            'ativo': config.ativo,
            'chave_pix': config.chave_pix,
            'titular': config.titular,
            'banco': config.banco,
            'mensagem': config.mensagem,
            'telefone_comprovante': config.telefone_comprovante,
            'qr_code_ativo': config.qr_code_ativo,
            'qr_code_tamanho': config.qr_code_tamanho,
        }
    })

@login_required
def configuracao_cobranca_dados(request):
    """Retorna dados da configuração para AJAX"""
    config = ConfiguracaoCobranca.get_configuracao_unica()
    return JsonResponse({
        'success': True,
        'nome': config.nome,
        'ativo': config.ativo,
        'chave_pix': config.chave_pix,
        'titular': config.titular,
        'banco': config.banco,
        'mensagem': config.mensagem,
        'telefone_comprovante': config.telefone_comprovante,
        'qr_code_ativo': config.qr_code_ativo,
        'qr_code_tamanho': config.qr_code_tamanho,
    })


@login_required
def gerar_parcela_unica(request, associado_id):
    """
    Gera uma parcela única para um associado específico
    """
    try:
        # Buscar o associado
        associado = Associado.objects.get(id=associado_id, ativo=True)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado ou inativo.')
        return redirect('financeiro:mensalidade_list')
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            tipo_recebimento_id = request.POST.get('tipo_recebimento')
            valor = request.POST.get('valor')
            data_vencimento = request.POST.get('data_vencimento')
            descricao = request.POST.get('descricao', '')
            
            # Validações básicas
            if not all([tipo_recebimento_id, valor, data_vencimento]):
                return JsonResponse({
                    'success': False,
                    'error': 'Todos os campos obrigatórios devem ser preenchidos.'
                })
            
            # Buscar o tipo de recebimento
            try:
                tipo_recebimento = TipoMensalidade.objects.get(id=tipo_recebimento_id, ativo=True)
            except TipoMensalidade.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de recebimento não encontrado.'
                })
            
            # Converter valor para decimal
            try:
                valor_decimal = Decimal(valor)
                if valor_decimal <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'O valor deve ser maior que zero.'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Valor inválido.'
                })
            
            # Converter data
            try:
                data_vencimento_obj = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Data de vencimento inválida.'
                })
            
            # Criar a mensalidade
            mensalidade = Mensalidade.objects.create(
                associado=associado,
                tipo=tipo_recebimento,
                valor=valor_decimal,
                data_vencimento=data_vencimento_obj,
                descricao=descricao,
                status='pendente'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Parcela única criada com sucesso! ID: {mensalidade.id}',
                'mensalidade_id': mensalidade.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao criar parcela: {str(e)}'
            })
    
    # GET request - retornar dados para o modal
    try:
        # Buscar tipos de recebimento ativos
        tipos_recebimento = TipoMensalidade.objects.filter(ativo=True).order_by('nome')
        
        # Buscar dados do associado
        associado_data = {
            'id': associado.id,
            'nome': associado.nome,
            'cpf': associado.cpf,
            'matricula': associado.matricula_militar
        }
        
        return JsonResponse({
            'success': True,
            'associado': associado_data,
            'tipos_recebimento': list(tipos_recebimento.values('id', 'nome', 'valor'))
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao carregar dados: {str(e)}'
        })