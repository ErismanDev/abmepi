from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db import transaction
import json
from datetime import datetime, timedelta, date

from .models import (
    Quarto, Hospede, Reserva, Hospedagem, 
    ServicoAdicional, ServicoUtilizado
)
from .forms import (
    QuartoForm, HospedeForm, ReservaForm, HospedagemForm,
    ServicoAdicionalForm, ServicoUtilizadoForm, BuscaQuartoForm,
    RelatorioHospedagemForm, ServicoUtilizadoFormSet
)


# Dashboard do Hotel de Trânsito
@login_required
def dashboard_hotel_transito(request):
    """Dashboard principal do módulo de hotel de trânsito"""
    
    # Estatísticas gerais
    total_quartos = Quarto.objects.filter(ativo=True).count()
    quartos_disponiveis = Quarto.objects.filter(status='disponivel', ativo=True).count()
    quartos_ocupados = Quarto.objects.filter(status='ocupado', ativo=True).count()
    quartos_manutencao = Quarto.objects.filter(status='manutencao', ativo=True).count()
    
    # Hospedagens ativas
    hospedagens_ativas = Hospedagem.objects.filter(status='ativa').count()
    
    # Reservas pendentes
    reservas_pendentes = Reserva.objects.filter(status='pendente').count()
    reservas_confirmadas = Reserva.objects.filter(status='confirmada').count()
    
    # Receita do mês atual
    mes_atual = timezone.now().month
    ano_atual = timezone.now().year
    receita_mes = Hospedagem.objects.filter(
        data_entrada_real__month=mes_atual,
        data_entrada_real__year=ano_atual,
        status='finalizada'
    ).aggregate(total=Sum('valor_total_real'))['total'] or 0
    
    # Hóspedes por tipo
    hospedes_associados = Hospede.objects.filter(tipo_hospede='associado', ativo=True).count()
    hospedes_nao_associados = Hospede.objects.filter(tipo_hospede='nao_associado', ativo=True).count()
    
    # Últimas hospedagens
    ultimas_hospedagens = Hospedagem.objects.select_related('hospede', 'quarto').order_by('-data_cadastro')[:5]
    
    # Próximas reservas
    proximas_reservas = Reserva.objects.select_related('hospede', 'quarto').filter(
        data_entrada__gte=timezone.now().date(),
        status__in=['pendente', 'confirmada']
    ).order_by('data_entrada')[:5]
    
    context = {
        'total_quartos': total_quartos,
        'quartos_disponiveis': quartos_disponiveis,
        'quartos_ocupados': quartos_ocupados,
        'quartos_manutencao': quartos_manutencao,
        'hospedagens_ativas': hospedagens_ativas,
        'reservas_pendentes': reservas_pendentes,
        'reservas_confirmadas': reservas_confirmadas,
        'receita_mes': receita_mes,
        'hospedes_associados': hospedes_associados,
        'hospedes_nao_associados': hospedes_nao_associados,
        'ultimas_hospedagens': ultimas_hospedagens,
        'proximas_reservas': proximas_reservas,
    }
    
    return render(request, 'hotel_transito/dashboard.html', context)


# Views para Quartos
class QuartoListView(LoginRequiredMixin, ListView):
    model = Quarto
    template_name = 'hotel_transito/quarto_list.html'
    context_object_name = 'quartos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Quarto.objects.all()
        
        # Filtros
        status = self.request.GET.get('status')
        tipo = self.request.GET.get('tipo')
        ativo = self.request.GET.get('ativo')
        
        if status:
            queryset = queryset.filter(status=status)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        return queryset.order_by('numero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Quarto.STATUS_CHOICES
        context['tipo_choices'] = Quarto.TIPO_QUARTO_CHOICES
        return context


class QuartoDetailView(LoginRequiredMixin, DetailView):
    model = Quarto
    template_name = 'hotel_transito/quarto_detail.html'
    context_object_name = 'quarto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar reservas e hospedagens do quarto
        context['reservas'] = self.object.reserva_set.all().order_by('-data_reserva')[:10]
        context['hospedagens'] = self.object.hospedagem_set.all().order_by('-data_cadastro')[:10]
        return context


class QuartoCreateView(LoginRequiredMixin, CreateView):
    model = Quarto
    form_class = QuartoForm
    template_name = 'hotel_transito/quarto_form.html'
    success_url = reverse_lazy('hotel_transito:quarto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Quarto criado com sucesso!')
        return super().form_valid(form)


class QuartoUpdateView(LoginRequiredMixin, UpdateView):
    model = Quarto
    form_class = QuartoForm
    template_name = 'hotel_transito/quarto_form.html'
    success_url = reverse_lazy('hotel_transito:quarto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Quarto atualizado com sucesso!')
        return super().form_valid(form)


class QuartoDeleteView(LoginRequiredMixin, DeleteView):
    model = Quarto
    template_name = 'hotel_transito/quarto_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:quarto_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quarto excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Hóspedes
class HospedeListView(LoginRequiredMixin, ListView):
    model = Hospede
    template_name = 'hotel_transito/hospede_list.html'
    context_object_name = 'hospedes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Hospede.objects.all()
        
        # Filtros
        tipo_hospede = self.request.GET.get('tipo_hospede')
        ativo = self.request.GET.get('ativo')
        search = self.request.GET.get('search')
        
        if tipo_hospede:
            queryset = queryset.filter(tipo_hospede=tipo_hospede)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        if search:
            queryset = queryset.filter(nome_completo__icontains=search)
        
        return queryset.order_by('nome_completo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas para os cards
        total_hospedes = Hospede.objects.count()
        hospedes_ativos = Hospede.objects.filter(ativo=True).count()
        hospedes_associados = Hospede.objects.filter(tipo_hospede='associado').count()
        hospedes_visitantes = Hospede.objects.filter(tipo_hospede='visitante').count()
        
        context.update({
            'total_hospedes': total_hospedes,
            'hospedes_ativos': hospedes_ativos,
            'hospedes_associados': hospedes_associados,
            'hospedes_visitantes': hospedes_visitantes,
            'tipo_hospede_choices': Hospede.TIPO_HOSPEDE_CHOICES,
        })
        
        return context


class HospedeDetailView(LoginRequiredMixin, DetailView):
    model = Hospede
    template_name = 'hotel_transito/hospede_detail.html'
    context_object_name = 'hospede'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar reservas e hospedagens do hóspede
        context['reservas'] = self.object.reserva_set.all().order_by('-data_reserva')
        context['hospedagens'] = self.object.hospedagem_set.all().order_by('-data_cadastro')
        return context


class HospedeCreateView(LoginRequiredMixin, CreateView):
    model = Hospede
    form_class = HospedeForm
    template_name = 'hotel_transito/hospede_form.html'
    success_url = reverse_lazy('hotel_transito:hospede_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Hóspede criado com sucesso!')
        return super().form_valid(form)


class HospedeUpdateView(LoginRequiredMixin, UpdateView):
    model = Hospede
    form_class = HospedeForm
    template_name = 'hotel_transito/hospede_form.html'
    success_url = reverse_lazy('hotel_transito:hospede_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Hóspede atualizado com sucesso!')
        return super().form_valid(form)


class HospedeDeleteView(LoginRequiredMixin, DeleteView):
    model = Hospede
    template_name = 'hotel_transito/hospede_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:hospede_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Hóspede excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Reservas
class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'hotel_transito/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Reserva.objects.select_related('hospede', 'quarto')
        
        # Filtros
        status = self.request.GET.get('status')
        data_entrada = self.request.GET.get('data_entrada')
        data_saida = self.request.GET.get('data_saida')
        
        if status:
            queryset = queryset.filter(status=status)
        if data_entrada:
            queryset = queryset.filter(data_entrada__gte=data_entrada)
        if data_saida:
            queryset = queryset.filter(data_saida__lte=data_saida)
        
        return queryset.order_by('-data_reserva')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Reserva.STATUS_CHOICES
        return context


class ReservaDetailView(LoginRequiredMixin, DetailView):
    model = Reserva
    template_name = 'hotel_transito/reserva_detail.html'
    context_object_name = 'reserva'


class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'hotel_transito/reserva_form.html'
    success_url = reverse_lazy('hotel_transito:reserva_list')
    
    def form_valid(self, form):
        # Gerar código único para a reserva
        import uuid
        form.instance.codigo_reserva = f"RES{uuid.uuid4().hex[:8].upper()}"
        
        messages.success(self.request, 'Reserva criada com sucesso!')
        return super().form_valid(form)


class ReservaUpdateView(LoginRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'hotel_transito/reserva_form.html'
    success_url = reverse_lazy('hotel_transito:reserva_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Reserva atualizada com sucesso!')
        return super().form_valid(form)


class ReservaDeleteView(LoginRequiredMixin, DeleteView):
    model = Reserva
    template_name = 'hotel_transito/reserva_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:reserva_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Reserva excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def confirmar_reserva(request, pk):
    """Confirmar uma reserva pendente"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if reserva.status == 'pendente':
        reserva.status = 'confirmada'
        reserva.data_confirmacao = timezone.now()
        reserva.save()
        
        # Não alterar o status do quarto - ele pode ter múltiplas reservas
        # O status do quarto será determinado dinamicamente baseado nas reservas ativas
        
        # Marcar notificações relacionadas como resolvidas
        from core.models import Notificacao
        Notificacao.objects.filter(
            objeto_tipo='Reserva',
            objeto_id=reserva.id,
            tipo='reserva_hotel',
            status='pendente'
        ).update(status='resolvida', data_resolucao=timezone.now())
        
        messages.success(request, 'Reserva confirmada com sucesso!')
    else:
        messages.error(request, 'Apenas reservas pendentes podem ser confirmadas.')
    
    return redirect('hotel_transito:reserva_detail', pk=pk)


@login_required
def cancelar_reserva(request, pk):
    """Cancelar uma reserva"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if reserva.status in ['pendente', 'confirmada']:
        reserva.status = 'cancelada'
        reserva.data_cancelamento = timezone.now()
        reserva.save()
        
        # Não alterar o status do quarto - ele pode ter outras reservas ativas
        # O status do quarto será determinado dinamicamente baseado nas reservas ativas
        
        # Marcar notificações relacionadas como canceladas
        from core.models import Notificacao
        Notificacao.objects.filter(
            objeto_tipo='Reserva',
            objeto_id=reserva.id,
            tipo='reserva_hotel',
            status='pendente'
        ).update(status='cancelada', data_resolucao=timezone.now())
        
        messages.success(request, 'Reserva cancelada com sucesso!')
    else:
        messages.error(request, 'Esta reserva não pode ser cancelada.')
    
    return redirect('hotel_transito:reserva_detail', pk=pk)


# Views para Hospedagens
class HospedagemListView(LoginRequiredMixin, ListView):
    model = Hospedagem
    template_name = 'hotel_transito/hospedagem_list.html'
    context_object_name = 'hospedagens'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Hospedagem.objects.select_related('hospede', 'quarto')
        
        # Filtros
        status = self.request.GET.get('status')
        data_entrada = self.request.GET.get('data_entrada')
        
        if status:
            queryset = queryset.filter(status=status)
        if data_entrada:
            queryset = queryset.filter(data_entrada_real__date=data_entrada)
        
        return queryset.order_by('-data_cadastro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Hospedagem.STATUS_CHOICES
        return context


class HospedagemDetailView(LoginRequiredMixin, DetailView):
    model = Hospedagem
    template_name = 'hotel_transito/hospedagem_detail.html'
    context_object_name = 'hospedagem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar serviços utilizados
        context['servicos_utilizados'] = self.object.servicoutilizado_set.all().order_by('-data_utilizacao')
        return context


class HospedagemCreateView(LoginRequiredMixin, CreateView):
    model = Hospedagem
    form_class = HospedagemForm
    template_name = 'hotel_transito/hospedagem_form.html'
    success_url = reverse_lazy('hotel_transito:hospedagem_list')
    
    def form_valid(self, form):
        # Atualizar status do quarto para ocupado
        quarto = form.instance.quarto
        quarto.status = 'ocupado'
        quarto.save()
        
        messages.success(self.request, 'Hospedagem criada com sucesso!')
        return super().form_valid(form)


class HospedagemUpdateView(LoginRequiredMixin, UpdateView):
    model = Hospedagem
    form_class = HospedagemForm
    template_name = 'hotel_transito/hospedagem_form.html'
    success_url = reverse_lazy('hotel_transito:hospedagem_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Hospedagem atualizada com sucesso!')
        return super().form_valid(form)


class HospedagemDeleteView(LoginRequiredMixin, DeleteView):
    model = Hospedagem
    template_name = 'hotel_transito/hospedagem_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:hospedagem_list')
    
    def delete(self, request, *args, **kwargs):
        # Liberar quarto
        hospedagem = self.get_object()
        quarto = hospedagem.quarto
        quarto.status = 'disponivel'
        quarto.save()
        
        messages.success(request, 'Hospedagem excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def finalizar_hospedagem(request, pk):
    """Finalizar uma hospedagem ativa"""
    hospedagem = get_object_or_404(Hospedagem, pk=pk)
    
    if hospedagem.status == 'ativa':
        hospedagem.status = 'finalizada'
        hospedagem.data_saida_real = timezone.now()
        hospedagem.save()
        
        # Liberar quarto
        quarto = hospedagem.quarto
        quarto.status = 'disponivel'
        quarto.save()
        
        # Se havia reserva, finalizá-la também
        if hospedagem.reserva and hospedagem.reserva.status == 'confirmada':
            hospedagem.reserva.status = 'finalizada'
            hospedagem.reserva.save()
        
        messages.success(request, 'Hospedagem finalizada com sucesso!')
    else:
        messages.error(request, 'Apenas hospedagens ativas podem ser finalizadas.')
    
    return redirect('hotel_transito:hospedagem_detail', pk=pk)


# Views para Serviços Adicionais
class ServicoAdicionalListView(LoginRequiredMixin, ListView):
    model = ServicoAdicional
    template_name = 'hotel_transito/servico_adicional_list.html'
    context_object_name = 'servicos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ServicoAdicional.objects.all()
        
        # Filtros
        tipo = self.request.GET.get('tipo')
        ativo = self.request.GET.get('ativo')
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if ativo:
            if ativo == 'true':
                queryset = queryset.filter(ativo=True)
            elif ativo == 'false':
                queryset = queryset.filter(ativo=False)
        
        return queryset


class ServicoAdicionalCreateView(LoginRequiredMixin, CreateView):
    model = ServicoAdicional
    form_class = ServicoAdicionalForm
    template_name = 'hotel_transito/servico_adicional_form.html'
    success_url = reverse_lazy('hotel_transito:servico_adicional_list')


class ServicoAdicionalUpdateView(LoginRequiredMixin, UpdateView):
    model = ServicoAdicional
    form_class = ServicoAdicionalForm
    template_name = 'hotel_transito/servico_adicional_form.html'
    success_url = reverse_lazy('hotel_transito:servico_adicional_list')


class ServicoAdicionalDeleteView(LoginRequiredMixin, DeleteView):
    model = ServicoAdicional
    template_name = 'hotel_transito/servico_adicional_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:servico_adicional_list')


# Views para Serviços Utilizados
class ServicoUtilizadoListView(LoginRequiredMixin, ListView):
    model = ServicoUtilizado
    template_name = 'hotel_transito/servico_utilizado_list.html'
    context_object_name = 'servicos_utilizados'
    paginate_by = 20


class ServicoUtilizadoCreateView(LoginRequiredMixin, CreateView):
    model = ServicoUtilizado
    form_class = ServicoUtilizadoForm
    template_name = 'hotel_transito/servico_utilizado_form.html'
    success_url = reverse_lazy('hotel_transito:servico_utilizado_list')


class ServicoUtilizadoUpdateView(LoginRequiredMixin, UpdateView):
    model = ServicoUtilizado
    form_class = ServicoUtilizadoForm
    template_name = 'hotel_transito/servico_utilizado_form.html'
    success_url = reverse_lazy('hotel_transito:servico_utilizado_list')


class ServicoUtilizadoDeleteView(LoginRequiredMixin, DeleteView):
    model = ServicoUtilizado
    template_name = 'hotel_transito/servico_utilizado_confirm_delete.html'
    success_url = reverse_lazy('hotel_transito:servico_utilizado_list')


# Views para Busca e Relatórios
@login_required
def buscar_quartos_disponiveis(request):
    """Buscar quartos disponíveis para um período"""
    if request.method == 'POST':
        form = BuscaQuartoForm(request.POST)
        if form.is_valid():
            data_entrada = form.cleaned_data['data_entrada']
            data_saida = form.cleaned_data['data_saida']
            tipo_quarto = form.cleaned_data['tipo_quarto']
            capacidade_minima = form.cleaned_data['capacidade_minima']
            
            # Buscar quartos disponíveis
            quartos_disponiveis = Quarto.objects.filter(
                status='disponivel',
                ativo=True
            )
            
            if tipo_quarto:
                quartos_disponiveis = quartos_disponiveis.filter(tipo=tipo_quarto)
            
            if capacidade_minima:
                quartos_disponiveis = quartos_disponiveis.filter(capacidade__gte=capacidade_minima)
            
            # Verificar conflitos de reserva
            quartos_finais = []
            for quarto in quartos_disponiveis:
                conflitos = Reserva.objects.filter(
                    quarto=quarto,
                    status__in=['pendente', 'confirmada'],
                    data_entrada__lt=data_saida,
                    data_saida__gt=data_entrada
                )
                
                if not conflitos.exists():
                    quartos_finais.append(quarto)
            
            context = {
                'form': form,
                'quartos_disponiveis': quartos_finais,
                'data_entrada': data_entrada,
                'data_saida': data_saida,
            }
            
            return render(request, 'hotel_transito/buscar_quartos_disponiveis.html', context)
    else:
        form = BuscaQuartoForm()
    
    return render(request, 'hotel_transito/buscar_quartos_disponiveis.html', {'form': form})


@login_required
def relatorio_hospedagem(request):
    """Gerar relatório de hospedagens"""
    if request.method == 'POST':
        form = RelatorioHospedagemForm(request.POST)
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            tipo_hospede = form.cleaned_data['tipo_hospede']
            status = form.cleaned_data['status']
            
            # Definir período baseado na seleção
            hoje = timezone.now().date()
            
            if periodo == 'hoje':
                data_inicio = hoje
                data_fim = hoje
            elif periodo == 'semana':
                data_inicio = hoje - timedelta(days=hoje.weekday())
                data_fim = data_inicio + timedelta(days=6)
            elif periodo == 'mes':
                data_inicio = hoje.replace(day=1)
                if hoje.month == 12:
                    data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    data_fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
            elif periodo == 'trimestre':
                trimestre = (hoje.month - 1) // 3
                mes_inicio = trimestre * 3 + 1
                data_inicio = hoje.replace(month=mes_inicio, day=1)
                if mes_inicio + 2 > 12:
                    data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    data_fim = hoje.replace(month=mes_inicio + 2, day=1) - timedelta(days=1)
            elif periodo == 'ano':
                data_inicio = hoje.replace(month=1, day=1)
                data_fim = hoje.replace(month=12, day=31)
            
            # Filtrar hospedagens
            hospedagens = Hospedagem.objects.filter(
                data_entrada_real__date__gte=data_inicio,
                data_entrada_real__date__lte=data_fim
            )
            
            if tipo_hospede:
                hospedagens = hospedagens.filter(hospede__tipo_hospede=tipo_hospede)
            
            if status:
                hospedagens = hospedagens.filter(status=status)
            
            # Estatísticas
            total_hospedagens = hospedagens.count()
            receita_total = hospedagens.aggregate(total=Sum('valor_total_real'))['total'] or 0
            hospedes_associados = hospedagens.filter(hospede__tipo_hospede='associado').count()
            hospedes_nao_associados = hospedagens.filter(hospede__tipo_hospede='nao_associado').count()
            
            context = {
                'form': form,
                'hospedagens': hospedagens,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'total_hospedagens': total_hospedagens,
                'receita_total': receita_total,
                'hospedes_associados': hospedes_associados,
                'hospedes_nao_associados': hospedes_nao_associados,
            }
            
            return render(request, 'hotel_transito/relatorio_hospedagem.html', context)
    else:
        form = RelatorioHospedagemForm()
    
    return render(request, 'hotel_transito/relatorio_hospedagem.html', {'form': form})


# Views AJAX
@login_required
def get_quarto_info(request, pk):
    """Retornar informações do quarto via AJAX"""
    try:
        quarto = Quarto.objects.get(pk=pk)
        data = {
            'success': True,
            'quarto': {
                'numero': quarto.numero,
                'tipo': quarto.get_tipo_display(),
                'capacidade': quarto.capacidade,
                'valor_diaria': float(quarto.valor_diaria),
                'status': quarto.status,
                'caracteristicas': {
                    'ar_condicionado': quarto.ar_condicionado,
                    'tv': quarto.tv,
                    'wifi': quarto.wifi,
                    'banheiro_privativo': quarto.banheiro_privativo,
                    'frigobar': quarto.frigobar,
                }
            }
        }
        return JsonResponse(data)
    except Quarto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Quarto não encontrado'})


@login_required
def get_reserva_info(request, pk):
    """Retornar informações da reserva via AJAX"""
    try:
        reserva = Reserva.objects.get(pk=pk)
        data = {
            'success': True,
            'reserva': {
                'id': reserva.id,
                'codigo_reserva': reserva.codigo_reserva,
                'quarto': reserva.quarto.id,
                'hospede': reserva.hospede.id,
                'data_entrada': reserva.data_entrada.strftime('%Y-%m-%d'),
                'data_saida': reserva.data_saida.strftime('%Y-%m-%d'),
                'hora_entrada': reserva.hora_entrada.strftime('%H:%M'),
                'hora_saida': reserva.hora_saida.strftime('%H:%M'),
                'valor_diaria': float(reserva.valor_diaria),
                'quantidade_diarias': reserva.quantidade_diarias,
                'valor_total': float(reserva.valor_total),
                'status': reserva.status,
                'observacoes': reserva.observacoes
            }
        }
        return JsonResponse(data)
    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reserva não encontrada'})


@login_required
def get_hospede_info(request, pk):
    """Retornar informações do hóspede via AJAX"""
    try:
        hospede = Hospede.objects.get(pk=pk)
        data = {
            'nome_completo': hospede.nome_completo,
            'tipo_hospede': hospede.get_tipo_hospede_display(),
            'telefone': hospede.telefone,
            'email': hospede.email,
            'cidade': hospede.cidade,
            'estado': hospede.estado,
        }
        return JsonResponse({'success': True, 'data': data})
    except Hospede.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Hóspede não encontrado'})


@login_required
def checkin_rapido(request):
    """Check-in rápido de hóspedes"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospede_id = data.get('hospede_id')
            quarto_id = data.get('quarto_id')
            
            hospede = Hospede.objects.get(pk=hospede_id)
            quarto = Quarto.objects.get(pk=quarto_id)
            
            # Criar hospedagem
            hospedagem = Hospedagem.objects.create(
                hospede=hospede,
                quarto=quarto,
                data_entrada_real=timezone.now(),
                valor_diaria_real=quarto.valor_diaria,
                status='ativa'
            )
            
            # Atualizar status do quarto
            quarto.status = 'ocupado'
            quarto.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Check-in realizado com sucesso!',
                'hospedagem_id': hospedagem.id
            })
            
        except (Hospede.DoesNotExist, Quarto.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Hóspede ou quarto não encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def checkout_rapido(request):
    """Check-out rápido de hóspedes"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospedagem_id = data.get('hospedagem_id')
            
            hospedagem = Hospedagem.objects.get(pk=hospedagem_id, status='ativa')
            
            # Finalizar hospedagem
            hospedagem.status = 'finalizada'
            hospedagem.data_saida_real = timezone.now()
            hospedagem.save()
            
            # Liberar quarto
            quarto = hospedagem.quarto
            quarto.status = 'disponivel'
            quarto.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Check-out realizado com sucesso!'
            })
            
        except Hospedagem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Hospedagem não encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


def hospede_detail_modal(request, pk):
    """View para retornar detalhes do hóspede em formato JSON para modal"""
    try:
        hospede = Hospede.objects.get(pk=pk)
        
        # Renderizar o HTML do modal
        html = render_to_string('hotel_transito/hospede_detail_modal.html', {
            'hospede': hospede
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'hospede': {
                'id': hospede.pk,
                'nome_completo': hospede.nome_completo,
                'tipo_hospede': hospede.get_tipo_hospede_display(),
                'ativo': hospede.ativo
            },
            'html': html
        })
    except Hospede.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Hóspede não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Views específicas para Associados
@login_required
def associado_quartos_disponiveis(request):
    """
    View para associados visualizarem e reservarem quartos disponíveis
    """
    # Verificar se o usuário é associado
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Esta funcionalidade é exclusiva para associados.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o associado vinculado ao usuário
    try:
        from associados.models import Associado
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado. Entre em contato com a administração.')
        return redirect('core:usuario_dashboard')
    
    # Buscar todos os quartos ativos (para mostrar calendário completo)
    quartos_disponiveis = Quarto.objects.filter(
        ativo=True
    ).order_by('numero')
    
    # Aplicar filtros se fornecidos
    tipo_quarto = request.GET.get('tipo_quarto')
    capacidade_minima = request.GET.get('capacidade_minima')
    
    if tipo_quarto:
        quartos_disponiveis = quartos_disponiveis.filter(tipo=tipo_quarto)
    
    if capacidade_minima:
        quartos_disponiveis = quartos_disponiveis.filter(capacidade__gte=capacidade_minima)
    
    # Buscar todas as reservas do associado
    reservas = Reserva.objects.filter(
        hospede__associado=associado
    ).select_related('quarto').order_by('-data_reserva')
    
    # Aplicar filtro de status se fornecido
    status_filter = request.GET.get('status')
    if status_filter:
        reservas = reservas.filter(status=status_filter)
    
    # Buscar todas as reservas para o calendário (todas as reservas ativas)
    from datetime import datetime, timedelta, date
    import calendar
    
    # Obter mês e ano atual ou do parâmetro
    hoje = datetime.now()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))
    
    # Buscar reservas do mês
    inicio_mes = date(ano, mes, 1)
    if mes == 12:
        fim_mes = date(ano + 1, 1, 1) - timedelta(days=1)
    else:
        fim_mes = date(ano, mes + 1, 1) - timedelta(days=1)
    
    # Buscar reservas do mês (pendentes e confirmadas)
    reservas_mes = Reserva.objects.filter(
        data_entrada__lte=fim_mes,
        data_saida__gte=inicio_mes,
        status__in=['pendente', 'confirmada']
    ).select_related('quarto')
    
    # Buscar hospedagens ativas do mês (ocupadas)
    hospedagens_mes = Hospedagem.objects.filter(
        data_entrada_real__date__lte=fim_mes,
        data_entrada_real__date__gte=inicio_mes,
        status='ativa'
    ).select_related('quarto')
    
    # Criar dicionários de dias por quarto
    dias_reservados = {}  # Amarelo - reservas
    dias_ocupados = {}    # Vermelho - hospedagens ativas
    
    # Processar reservas (amarelo)
    for reserva in reservas_mes:
        quarto_num = reserva.quarto.numero
        if quarto_num not in dias_reservados:
            dias_reservados[quarto_num] = set()
        
        # Adicionar todos os dias da reserva
        data_atual = max(reserva.data_entrada, inicio_mes)
        data_fim = min(reserva.data_saida, fim_mes)
        
        while data_atual <= data_fim:
            dias_reservados[quarto_num].add(data_atual.day)
            data_atual += timedelta(days=1)
    
    # Processar hospedagens ativas (vermelho)
    for hospedagem in hospedagens_mes:
        quarto_num = hospedagem.quarto.numero
        if quarto_num not in dias_ocupados:
            dias_ocupados[quarto_num] = set()
        
        # Adicionar todos os dias da hospedagem
        data_entrada = hospedagem.data_entrada_real.date()
        data_saida = hospedagem.data_saida_real.date() if hospedagem.data_saida_real else fim_mes
        
        data_atual = max(data_entrada, inicio_mes)
        data_fim = min(data_saida, fim_mes)
        
        while data_atual <= data_fim:
            dias_ocupados[quarto_num].add(data_atual.day)
            data_atual += timedelta(days=1)
    
    # Adicionar informações aos quartos
    for quarto in quartos_disponiveis:
        quarto.dias_reservados = dias_reservados.get(quarto.numero, set())
        quarto.dias_ocupados = dias_ocupados.get(quarto.numero, set())
    
    # Dados do calendário
    cal = calendar.monthcalendar(ano, mes)
    nome_mes = calendar.month_name[mes]
    
    context = {
        'associado': associado,
        'quartos_disponiveis': quartos_disponiveis,
        'reservas': reservas,
        'tipo_quarto_choices': Quarto.TIPO_QUARTO_CHOICES,
        'status_choices': Reserva.STATUS_CHOICES,
        'calendario': {
            'mes': mes,
            'ano': ano,
            'nome_mes': nome_mes,
            'cal': cal,
            'dias_ocupados': dias_ocupados,
            'mes_anterior': mes - 1 if mes > 1 else 12,
            'ano_anterior': ano if mes > 1 else ano - 1,
            'mes_proximo': mes + 1 if mes < 12 else 1,
            'ano_proximo': ano if mes < 12 else ano + 1,
        }
    }
    
    return render(request, 'hotel_transito/associado_quartos_disponiveis.html', context)





@login_required
def associado_reservar_quarto(request, quarto_id):
    """
    View para associados reservarem um quarto específico
    """
    # Verificar se o usuário é associado
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Esta funcionalidade é exclusiva para associados.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o associado vinculado ao usuário
    try:
        from associados.models import Associado
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado. Entre em contato com a administração.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o quarto (permitir quartos disponíveis e reservados)
    quarto = get_object_or_404(Quarto, pk=quarto_id, status__in=['disponivel', 'reservado'], ativo=True)
    
    if request.method == 'POST':
        # Processar formulário de reserva
        data_entrada = request.POST.get('data_entrada')
        data_saida = request.POST.get('data_saida')
        observacoes = request.POST.get('observacoes', '')
        
        if not data_entrada or not data_saida:
            messages.error(request, 'Data de entrada e saída são obrigatórias.')
            return redirect('hotel_transito:associado_reservar_quarto', quarto_id=quarto_id)
        
        try:
            data_entrada = datetime.strptime(data_entrada, '%Y-%m-%d').date()
            data_saida = datetime.strptime(data_saida, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data inválido.')
            return redirect('hotel_transito:associado_reservar_quarto', quarto_id=quarto_id)
        
        # Validar datas
        if data_entrada >= data_saida:
            messages.error(request, 'A data de saída deve ser posterior à data de entrada.')
            return redirect('hotel_transito:associado_reservar_quarto', quarto_id=quarto_id)
        
        if data_entrada < timezone.now().date():
            messages.error(request, 'A data de entrada não pode ser anterior à data atual.')
            return redirect('hotel_transito:associado_reservar_quarto', quarto_id=quarto_id)
        
        # Verificar se o quarto ainda está disponível no período
        conflitos = Reserva.objects.filter(
            quarto=quarto,
            status__in=['pendente', 'confirmada'],
            data_entrada__lt=data_saida,
            data_saida__gt=data_entrada
        )
        
        if conflitos.exists():
            messages.error(request, 'Este quarto já possui reserva para o período selecionado.')
            return redirect('hotel_transito:associado_reservar_quarto', quarto_id=quarto_id)
        
        # Buscar ou criar hóspede associado
        hospede, created = Hospede.objects.get_or_create(
            associado=associado,
            defaults={
                'nome_completo': associado.nome,
                'tipo_hospede': 'associado',
                'tipo_documento': 'cpf',
                'numero_documento': associado.cpf,
                'telefone': associado.telefone,
                'email': associado.email,
                'cidade': associado.cidade,
                'estado': associado.estado,
                'ativo': True
            }
        )
        
        # Calcular valores
        quantidade_diarias = (data_saida - data_entrada).days
        valor_total = quarto.valor_diaria * quantidade_diarias
        
        # Criar reserva
        import uuid
        reserva = Reserva.objects.create(
            codigo_reserva=f"RES{uuid.uuid4().hex[:8].upper()}",
            quarto=quarto,
            hospede=hospede,
            data_entrada=data_entrada,
            data_saida=data_saida,
            hora_entrada=timezone.now().time(),
            hora_saida=timezone.now().time(),
            valor_diaria=quarto.valor_diaria,
            quantidade_diarias=quantidade_diarias,
            valor_total=valor_total,
            status='pendente',
            observacoes=observacoes
        )
        
        # Criar notificações para administradores
        from core.models import Notificacao, Usuario
        administradores = Usuario.objects.filter(
            tipo_usuario__in=['administrador_sistema', 'atendente_geral']
        )
        
        for admin in administradores:
            Notificacao.criar_notificacao_reserva_hotel(reserva, admin)
        
        messages.success(
            request, 
            f'Reserva criada com sucesso! Código: {reserva.codigo_reserva}. '
            f'Aguarde a confirmação da administração.'
        )
        
        return redirect('hotel_transito:associado_quartos_disponiveis')
    
    context = {
        'associado': associado,
        'quarto': quarto,
        'today': timezone.now().date(),
    }
    
    return render(request, 'hotel_transito/associado_reservar_quarto.html', context)


@login_required
def associado_minhas_reservas(request):
    """
    View para associados visualizarem suas reservas
    """
    # Verificar se o usuário é associado
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Esta funcionalidade é exclusiva para associados.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o associado vinculado ao usuário
    try:
        from associados.models import Associado
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado. Entre em contato com a administração.')
        return redirect('core:usuario_dashboard')
    
    # Buscar reservas do associado
    reservas = Reserva.objects.filter(
        hospede__associado=associado
    ).select_related('quarto', 'hospede').order_by('-data_reserva')
    
    # Aplicar filtros se fornecidos
    status = request.GET.get('status')
    if status:
        reservas = reservas.filter(status=status)
    
    context = {
        'associado': associado,
        'reservas': reservas,
        'status_choices': Reserva.STATUS_CHOICES,
    }
    
    return render(request, 'hotel_transito/associado_minhas_reservas.html', context)