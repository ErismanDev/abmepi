from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from core.models import Usuario, LogAtividade
from .models import Associado, Documento, Dependente
from .forms import (
    AssociadoForm, AssociadoSearchForm, DocumentoForm, 
    DependenteForm, AssociadoBulkActionForm
)
import csv
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from .forms import PreCadastroAssociadoForm
from .models import PreCadastroAssociado
from .pdf_views import gerar_declaracao_associados_pdf, gerar_requerimento_inscricao_pdf
from .ficha_cadastro_associado import gerar_ficha_cadastro_associado_pdf


class AssociadoListView(LoginRequiredMixin, ListView):
    """
    Lista de associados com funcionalidades de busca e filtros
    """
    model = Associado
    template_name = 'associados/associado_list.html'
    context_object_name = 'associados'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Associado.objects.select_related('usuario').all()
        
        # Aplicar filtros de busca
        form = AssociadoSearchForm(self.request.GET)
        if form.is_valid():
            nome = form.cleaned_data.get('nome')
            cpf = form.cleaned_data.get('cpf')
            matricula_militar = form.cleaned_data.get('matricula_militar')
            situacao = form.cleaned_data.get('situacao')
            estado = form.cleaned_data.get('estado')
            tipo_socio = form.cleaned_data.get('tipo_socio')
            tipo_profissional = form.cleaned_data.get('tipo_profissional')
            ativo = form.cleaned_data.get('ativo')
            nome_pai = form.cleaned_data.get('nome_pai')
            nome_mae = form.cleaned_data.get('nome_mae')
            tipo_documento = form.cleaned_data.get('tipo_documento')
            
            if nome:
                queryset = queryset.filter(nome__icontains=nome)
            
            if cpf:
                queryset = queryset.filter(cpf__icontains=cpf)
            
            if matricula_militar:
                queryset = queryset.filter(matricula_militar__icontains=matricula_militar)
            
            if situacao:
                queryset = queryset.filter(situacao=situacao)
            
            if estado:
                queryset = queryset.filter(estado=estado)
            
            if tipo_socio:
                queryset = queryset.filter(tipo_socio=tipo_socio)
            
            if tipo_profissional:
                queryset = queryset.filter(tipo_profissional=tipo_profissional)
            
            if nome_pai:
                queryset = queryset.filter(nome_pai__icontains=nome_pai)
            
            if nome_mae:
                queryset = queryset.filter(nome_mae__icontains=nome_mae)
            
            if tipo_documento:
                queryset = queryset.filter(tipo_documento=tipo_documento)
            
            if ativo:
                if ativo == 'true':
                    queryset = queryset.filter(ativo=True)
                elif ativo == 'false':
                    queryset = queryset.filter(ativo=False)
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AssociadoSearchForm(self.request.GET)
        context['total_associados'] = self.get_queryset().count()
        context['associados_ativos'] = self.get_queryset().filter(ativo=True).count()
        context['associados_inativos'] = self.get_queryset().filter(ativo=False).count()
        
        # Estatísticas por situação
        context['situacoes_stats'] = self.get_queryset().values('situacao').annotate(
            total=Count('id')
        ).order_by('situacao')
        
        # Estatísticas por estado
        context['estados_stats'] = self.get_queryset().values('estado').annotate(
            total=Count('id')
        ).order_by('estado')
        
        # Estatísticas por tipo de sócio
        context['tipos_socio_stats'] = self.get_queryset().values('tipo_socio').annotate(
            total=Count('id')
        ).order_by('tipo_socio')
        
        # Estatísticas por tipo de profissional
        context['tipos_profissional_stats'] = self.get_queryset().values('tipo_profissional').annotate(
            total=Count('id')
        ).order_by('tipo_profissional')
        
        return context


class AssociadoCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de novos associados
    """
    model = Associado
    form_class = AssociadoForm
    template_name = 'associados/associado_form.html'
    success_url = reverse_lazy('associados:associado_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Associado criado',
            modulo='Associados',
            detalhes=f'Associado {form.instance.nome} criado'
        )
        
        messages.success(self.request, 'Associado criado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Associado'
        context['submit_text'] = 'Criar Associado'
        return context


class AssociadoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Atualização de associados existentes
    """
    model = Associado
    form_class = AssociadoForm
    template_name = 'associados/associado_form.html'
    success_url = reverse_lazy('associados:associado_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Associado atualizado',
            modulo='Associados',
            detalhes=f'Associado {form.instance.nome} atualizado'
        )
        
        messages.success(self.request, 'Associado atualizado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Associado'
        context['submit_text'] = 'Atualizar Associado'
        return context


class AssociadoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão de associados
    """
    model = Associado
    template_name = 'associados/associado_confirm_delete.html'
    success_url = reverse_lazy('associados:associado_list')
    
    def delete(self, request, *args, **kwargs):
        associado = self.get_object()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Associado excluído',
            modulo='Associados',
            detalhes=f'Associado {associado.nome} excluído'
        )
        
        messages.success(request, 'Associado excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class DependenteDetailView(LoginRequiredMixin, DetailView):
    """
    Visualização detalhada de dependentes
    """
    model = Dependente
    template_name = 'associados/dependente_detail.html'
    context_object_name = 'dependente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associado'] = self.object.associado
        return context


class AssociadoDetailView(LoginRequiredMixin, DetailView):
    """
    Visualização detalhada de associados
    """
    model = Associado
    template_name = 'associados/associado_detail.html'
    context_object_name = 'associado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documentos'] = self.object.documentos.filter(ativo=True)
        context['dependentes'] = self.object.dependentes.filter(ativo=True)
        
        # Dados financeiros do associado
        from financeiro.models import Mensalidade
        mensalidades = Mensalidade.objects.filter(
            associado=self.object,
            tipo__categoria='mensalidade'
        )
        
        context['total_mensalidades'] = mensalidades.count()
        context['mensalidades_pagas'] = mensalidades.filter(status='pago').count()
        context['mensalidades_pendentes'] = mensalidades.filter(status='pendente').count()
        
        # Calcular valor total das mensalidades
        valor_total = mensalidades.aggregate(
            total=Sum('valor')
        )['total'] or 0
        context['valor_total'] = f"{valor_total:.2f}".replace('.', ',')
        
        return context





@login_required
def associado_bulk_action(request):
    """
    Ações em lote para associados
    """
    if request.method == 'POST':
        form = AssociadoBulkActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            associados_ids = form.cleaned_data['associados'].split(',')
            
            if action == 'ativar':
                Associado.objects.filter(id__in=associados_ids).update(ativo=True)
                messages.success(request, f'{len(associados_ids)} associado(s) ativado(s) com sucesso!')
            
            elif action == 'desativar':
                Associado.objects.filter(id__in=associados_ids).update(ativo=False)
                messages.success(request, f'{len(associados_ids)} associado(s) desativado(s) com sucesso!')
            
            elif action == 'exportar':
                return exportar_associados(request, associados_ids)
    
    return redirect('associados:associado_list')


@login_required
def associado_financeiro(request):
    """
    View para associados visualizarem suas informações financeiras (mensalidades e recebíveis)
    """
    # Verificar se o usuário é associado
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Esta funcionalidade é exclusiva para associados.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o associado vinculado ao usuário
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado. Entre em contato com a administração.')
        return redirect('core:usuario_dashboard')
    
    # Importar modelos financeiros
    from financeiro.models import Mensalidade, Pagamento
    
    # Buscar mensalidades do associado
    mensalidades = Mensalidade.objects.filter(
        associado=associado
    ).select_related('tipo').order_by('-data_vencimento')
    
    # Estatísticas financeiras
    total_mensalidades = mensalidades.count()
    mensalidades_pagas = mensalidades.filter(status='pago').count()
    mensalidades_pendentes = mensalidades.filter(status='pendente').count()
    mensalidades_atrasadas = mensalidades.filter(status='atrasado').count()
    
    # Valores financeiros
    from django.db.models import Sum
    valor_total_mensalidades = mensalidades.aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    valor_pago = mensalidades.filter(status='pago').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    valor_pendente = mensalidades.filter(status='pendente').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    valor_atrasado = mensalidades.filter(status='atrasado').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    # Buscar pagamentos recentes
    pagamentos_recentes = Pagamento.objects.filter(
        mensalidade__associado=associado
    ).select_related('mensalidade__tipo').order_by('-data_pagamento')[:10]
    
    # Mensalidades do ano atual
    from datetime import date
    ano_atual = date.today().year
    mensalidades_ano = mensalidades.filter(
        data_vencimento__year=ano_atual
    )
    
    # Calcular saldo (valor pago - valor total)
    saldo = valor_pago - valor_total_mensalidades
    
    context = {
        'associado': associado,
        'mensalidades': mensalidades[:20],  # Últimas 20 mensalidades
        'pagamentos_recentes': pagamentos_recentes,
        'mensalidades_ano': mensalidades_ano,
        'estatisticas': {
            'total_mensalidades': total_mensalidades,
            'mensalidades_pagas': mensalidades_pagas,
            'mensalidades_pendentes': mensalidades_pendentes,
            'mensalidades_atrasadas': mensalidades_atrasadas,
            'valor_total_mensalidades': valor_total_mensalidades,
            'valor_pago': valor_pago,
            'valor_pendente': valor_pendente,
            'valor_atrasado': valor_atrasado,
            'saldo': saldo,
        }
    }
    
    return render(request, 'associados/associado_financeiro.html', context)


@login_required
def exportar_associados(request, associados_ids=None):
    """
    Exporta associados para CSV
    """
    if associados_ids:
        queryset = Associado.objects.filter(id__in=associados_ids)
    else:
        queryset = Associado.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="associados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Nome', 'CPF', 'RG', 'Data Nascimento', 'Sexo', 'Estado Civil',
        'Email', 'Telefone', 'Celular', 'CEP', 'Rua', 'Número', 'Complemento',
        'Bairro', 'Cidade', 'Estado', 'Tipo de Sócio', 'Tipo de Profissional', 'Matrícula Militar', 'Posto/Graduação',
        'Nome Civil', 'Unidade Lotação', 'Data Ingresso', 'Situação', 'Ativo', 'Data Cadastro'
    ])
    
    for associado in queryset:
        writer.writerow([
            associado.nome, associado.cpf, associado.rg, associado.data_nascimento,
            associado.get_sexo_display(), associado.get_estado_civil_display(),
            associado.email, associado.telefone, associado.celular, associado.cep,
            associado.rua, associado.numero, associado.complemento, associado.bairro,
            associado.cidade, associado.estado, associado.get_tipo_socio_display(),
            associado.get_tipo_profissional_display(), associado.matricula_militar,
            associado.get_posto_graduacao_display(), associado.nome_civil, associado.unidade_lotacao, associado.data_ingresso,
            associado.get_situacao_display(), 'Sim' if associado.ativo else 'Não',
            associado.data_cadastro.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response


# Views para Documentos
@login_required
def documento_create(request, associado_id):
    """
    Criação de documentos para associados
    """
    associado = get_object_or_404(Associado, id=associado_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.associado = associado
            documento.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Documento criado',
                modulo='Associados',
                detalhes=f'Documento {documento.get_tipo_display()} criado para {associado.nome}'
            )
            
            messages.success(request, 'Documento criado com sucesso!')
            return redirect('associados:associado_detail', pk=associado_id)
    else:
        form = DocumentoForm()
    
    context = {
        'form': form,
        'associado': associado,
        'title': 'Novo Documento'
    }
    
    return render(request, 'associados/documento_form.html', context)


@login_required
def documento_delete(request, documento_id):
    """
    Exclusão de documentos
    """
    documento = get_object_or_404(Documento, id=documento_id)
    associado_id = documento.associado.id
    
    if request.method == 'POST':
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Documento excluído',
            modulo='Associados',
            detalhes=f'Documento {documento.get_tipo_display()} excluído de {documento.associado.nome}'
        )
        
        documento.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('associados:associado_detail', pk=associado_id)
    
    context = {
        'documento': documento,
        'associado': documento.associado
    }
    
    return render(request, 'associados/documento_confirm_delete.html', context)


# Views para Dependentes
@login_required
def dependente_create(request, associado_id):
    """
    Criação de dependentes para associados
    """
    associado = get_object_or_404(Associado, id=associado_id)
    
    if request.method == 'POST':
        form = DependenteForm(request.POST, request.FILES)
        if form.is_valid():
            dependente = form.save(commit=False)
            dependente.associado = associado
            dependente.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Dependente criado',
                modulo='Associados',
                detalhes=f'Dependente {dependente.nome} criado para {associado.nome}'
            )
            
            messages.success(request, 'Dependente criado com sucesso!')
            return redirect('associados:associado_detail', pk=associado_id)
    else:
        form = DependenteForm()
    
    context = {
        'form': form,
        'associado': associado,
        'title': 'Novo Dependente'
    }
    
    return render(request, 'associados/dependente_form.html', context)


@login_required
def dependente_update(request, pk):
    """
    Atualização de dependentes
    """
    dependente = get_object_or_404(Dependente, id=pk)
    
    if request.method == 'POST':
        form = DependenteForm(request.POST, request.FILES, instance=dependente)
        if form.is_valid():
            form.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Dependente atualizado',
                modulo='Associados',
                detalhes=f'Dependente {dependente.nome} atualizado'
            )
            
            messages.success(request, 'Dependente atualizado com sucesso!')
            return redirect('associados:associado_detail', pk=dependente.associado.id)
    else:
        form = DependenteForm(instance=dependente)
    
    context = {
        'form': form,
        'dependente': dependente,
        'associado': dependente.associado,
        'title': 'Editar Dependente'
    }
    
    return render(request, 'associados/dependente_form.html', context)


@login_required
def dependente_delete(request, pk):
    """
    Exclusão de dependentes
    """
    dependente = get_object_or_404(Dependente, id=pk)
    associado_id = dependente.associado.id
    
    if request.method == 'POST':
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Dependente excluído',
            modulo='Associados',
            detalhes=f'Dependente {dependente.nome} excluído de {dependente.associado.nome}'
        )
        
        dependente.delete()
        messages.success(request, 'Dependente excluído com sucesso!')
        return redirect('associados:associado_detail', pk=associado_id)
    
    context = {
        'dependente': dependente,
        'associado': dependente.associado
    }
    
    return render(request, 'associados/dependente_confirm_delete.html', context)


# API Views para AJAX
@login_required
def associado_stats_api(request):
    """
    API para estatísticas de associados (AJAX)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_associados = Associado.objects.count()
        associados_ativos = Associado.objects.filter(ativo=True).count()
        
        # Estatísticas por situação
        situacoes_stats = list(Associado.objects.values('situacao').annotate(
            total=Count('id')
        ).order_by('situacao'))
        
        # Estatísticas por estado
        estados_stats = list(Associado.objects.values('estado').annotate(
            total=Count('id')
        ).order_by('estado'))
        
        stats = {
            'total_associados': total_associados,
            'associados_ativos': associados_ativos,
            'situacoes_stats': situacoes_stats,
            'estados_stats': estados_stats,
        }
        
        return JsonResponse(stats)
    
    return JsonResponse({'error': 'Requisição inválida'}, status=400)


@login_required
def associado_api(request, pk):
    """
    API para buscar dados de um associado específico (AJAX)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            associado = get_object_or_404(Associado, pk=pk)
            
            # Formatar data de nascimento para o formato esperado pelo input date
            data_nascimento = associado.data_nascimento.strftime('%Y-%m-%d') if associado.data_nascimento else None
            
            data = {
                'id': associado.id,
                'nome_completo': associado.nome,
                'data_nascimento': data_nascimento,
                'telefone': associado.telefone or associado.celular,
                'email': associado.email,
                'cep': associado.cep,
                'endereco': associado.rua,
                'numero': associado.numero,
                'complemento': associado.complemento,
                'bairro': associado.bairro,
                'cidade': associado.cidade,
                'estado': associado.estado,
            }
            
            return JsonResponse(data)
            
        except Associado.DoesNotExist:
            return JsonResponse({'error': 'Associado não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Requisição inválida'}, status=400)


class PreCadastroAssociadoView(CreateView):
    """
    View para pré-cadastro de associados
    """
    model = PreCadastroAssociado
    form_class = PreCadastroAssociadoForm
    template_name = 'associados/pre_cadastro_form.html'
    success_url = reverse_lazy('associados:pre_cadastro_sucesso')
    
    def form_valid(self, form):
        print("DEBUG: Formulário válido, salvando pré-cadastro...")
        # Salvar o pré-cadastro
        response = super().form_valid(form)
        print(f"DEBUG: Pré-cadastro salvo com ID: {form.instance.id}")
        
        # Processar dependentes
        try:
            self.processar_dependentes(form.instance)
            print("DEBUG: Dependentes processados com sucesso")
        except Exception as e:
            print(f"DEBUG: Erro ao processar dependentes: {e}")
        
        # Enviar email de confirmação
        try:
            self.enviar_email_confirmacao(form.instance)
            print("DEBUG: Email de confirmação enviado")
        except Exception as e:
            # Log do erro, mas não falha o cadastro
            print(f"Erro ao enviar email: {e}")
        
        # Enviar mensagem de sucesso
        messages.success(
            self.request,
            'Pré-cadastro realizado com sucesso! Aguarde a aprovação da diretoria.'
        )
        
        return response
    
    def form_invalid(self, form):
        print("DEBUG: Formulário inválido")
        print(f"DEBUG: Erros do formulário: {form.errors}")
        return super().form_invalid(form)
    
    def processar_dependentes(self, pre_cadastro):
        """Processa os dependentes enviados no formulário"""
        from .models import DependentePreCadastro
        
        print("DEBUG: Iniciando processamento de dependentes...")
        print(f"DEBUG: POST data keys: {list(self.request.POST.keys())}")
        
        # Contar quantos dependentes foram enviados
        dependente_count = 0
        for key in self.request.POST.keys():
            if key.startswith('dependente_nome_'):
                dependente_count += 1
        
        print(f"DEBUG: Encontrados {dependente_count} dependentes")
        
        # Processar cada dependente
        for i in range(1, dependente_count + 1):
            nome = self.request.POST.get(f'dependente_nome_{i}')
            parentesco = self.request.POST.get(f'dependente_parentesco_{i}')
            data_nascimento = self.request.POST.get(f'dependente_data_nascimento_{i}')
            cpf = self.request.POST.get(f'dependente_cpf_{i}')
            email = self.request.POST.get(f'dependente_email_{i}')
            observacoes = self.request.POST.get(f'dependente_observacoes_{i}')
            
            print(f"DEBUG: Dependente {i} - Nome: {nome}, Parentesco: {parentesco}, Data: {data_nascimento}")
            
            # Validar campos obrigatórios
            if nome and parentesco and data_nascimento:
                # Limpar CPF se fornecido
                if cpf:
                    cpf = cpf.replace('.', '').replace('-', '')
                    if len(cpf) == 11 and cpf.isdigit():
                        cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
                    else:
                        cpf = None
                
                # Criar dependente
                try:
                    DependentePreCadastro.objects.create(
                        pre_cadastro=pre_cadastro,
                        nome=nome,
                        parentesco=parentesco,
                        data_nascimento=data_nascimento,
                        cpf=cpf,
                        email=email,
                        observacoes=observacoes
                    )
                    print(f"DEBUG: Dependente {i} criado com sucesso")
                except Exception as e:
                    print(f"DEBUG: Erro ao criar dependente {i}: {e}")
            else:
                print(f"DEBUG: Dependente {i} ignorado - campos obrigatórios vazios")
    
    def enviar_email_confirmacao(self, pre_cadastro):
        """Envia email de confirmação para o candidato"""
        subject = 'Pré-cadastro ABMEPI - Confirmação Recebida'
        message = f"""
        Olá {pre_cadastro.nome},

        Recebemos seu pré-cadastro para associação na ABMEPI.

        Dados do cadastro:
        - Nome: {pre_cadastro.nome}
        - CPF: {pre_cadastro.cpf}
        - Email: {pre_cadastro.email}
        - Profissão: {pre_cadastro.get_tipo_profissao_display()}

        Status: Pendente de Aprovação

        Sua solicitação será analisada pela diretoria da associação. 
        Você receberá uma notificação por email assim que for aprovado ou rejeitado.

        Em caso de dúvidas, entre em contato conosco.

        Atenciosamente,
        Equipe ABMEPI
        """
        
        # Enviar para o candidato
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pre_cadastro.email],
            fail_silently=False,
        )
        
        # Enviar notificação para administradores
        admin_subject = 'Novo Pré-cadastro ABMEPI - Requer Aprovação'
        admin_message = f"""
        Novo pré-cadastro recebido:

        Nome: {pre_cadastro.nome}
        CPF: {pre_cadastro.cpf}
        Email: {pre_cadastro.email}
        Profissão: {pre_cadastro.get_tipo_profissao_display()}
        Data: {pre_cadastro.data_solicitacao.strftime('%d/%m/%Y %H:%M')}

        Acesse o painel administrativo para analisar e aprovar/rejeitar.
        """
        
        # Enviar para administradores (configurar no settings)
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
        if admin_emails:
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )


def pre_cadastro_sucesso(request):
    """
    Página de sucesso após pré-cadastro
    """
    return render(request, 'associados/pre_cadastro_sucesso.html')


def consultar_pre_cadastro(request):
    """
    Página para consultar o andamento do pré-cadastro
    """
    pre_cadastro = None
    erro = None
    
    if request.method == 'POST':
        cpf = request.POST.get('cpf', '').strip()
        email = request.POST.get('email', '').strip()
        
        if cpf and email:
            try:
                # Buscar pré-cadastro por CPF e email
                pre_cadastro = PreCadastroAssociado.objects.get(cpf=cpf, email=email)
            except PreCadastroAssociado.DoesNotExist:
                erro = "Nenhum pré-cadastro encontrado com os dados informados."
            except PreCadastroAssociado.MultipleObjectsReturned:
                # Se houver múltiplos, pegar o mais recente
                pre_cadastro = PreCadastroAssociado.objects.filter(cpf=cpf, email=email).order_by('-data_solicitacao').first()
        else:
            erro = "Por favor, preencha todos os campos."
    
    context = {
        'pre_cadastro': pre_cadastro,
        'erro': erro,
        'title': 'Consultar Andamento do Pré-Cadastro'
    }
    
    return render(request, 'associados/consultar_pre_cadastro.html', context)


# ============================================================================
# VIEWS PARA MODAIS
# ============================================================================

@login_required
def associado_modal_create(request):
    """
    View para criar associado via modal
    """
    print(f"DEBUG: Método da requisição: {request.method}")
    print(f"DEBUG: Host: {request.get_host()}")
    print(f"DEBUG: User: {request.user}")
    
    if request.method == 'POST':
        print(f"DEBUG: Dados POST recebidos: {request.POST}")
        form = AssociadoForm(request.POST, request.FILES)
        if form.is_valid():
            associado = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Associado criado com sucesso!',
                'reload': True,
                'associado_id': associado.id
            })
        else:
            print(f"DEBUG: Erros de validação: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    print("DEBUG: Renderizando formulário GET")
    form = AssociadoForm()
    form_html = render(request, 'associados/forms/associado_form_modal.html', {
        'form': form,
        'title': 'Novo Associado'
    }).content.decode('utf-8')
    
    print(f"DEBUG: Form HTML gerado com {len(form_html)} caracteres")
    return JsonResponse({'form_html': form_html})


@login_required
def associado_modal_update(request, pk):
    """
    View para editar associado via modal
    """
    associado = get_object_or_404(Associado, pk=pk)
    
    if request.method == 'POST':
        # Log para debug
        print(f"DEBUG: Dados recebidos - ativo: {request.POST.get('ativo')}")
        print(f"DEBUG: Status atual do associado: {associado.ativo}")
        
        form = AssociadoForm(request.POST, request.FILES, instance=associado)
        if form.is_valid():
            # Log para debug antes de salvar
            print(f"DEBUG: Form válido - ativo antes de salvar: {form.cleaned_data.get('ativo')}")
            
            associado = form.save()
            
            # Log para debug após salvar
            print(f"DEBUG: Associado salvo - ativo após salvar: {associado.ativo}")
            
            return JsonResponse({
                'success': True,
                'message': 'Associado atualizado com sucesso!',
                'reload': True,
                'associado_id': associado.id
            })
        else:
            print(f"DEBUG: Erros de validação: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AssociadoForm(instance=associado)
    form_html = render(request, 'associados/forms/associado_form_modal.html', {
        'form': form,
        'title': 'Editar Associado'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def dependente_modal_create(request):
    """
    View para criar dependente via modal
    """
    associado_id = request.GET.get('associado')
    associado = None
    if associado_id:
        associado = get_object_or_404(Associado, pk=associado_id)
    
    if request.method == 'POST':
        form = DependenteForm(request.POST, request.FILES)
        if form.is_valid():
            dependente = form.save(commit=False)
            if associado:
                dependente.associado = associado
            dependente.save()
            return JsonResponse({
                'success': True,
                'message': 'Dependente criado com sucesso!',
                'reload': True,
                'dependente_id': dependente.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DependenteForm()
    form_html = render(request, 'associados/forms/dependente_form_modal.html', {
        'form': form,
        'associado': associado,
        'title': 'Novo Dependente'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def dependente_modal_update(request, pk):
    """
    View para editar dependente via modal
    """
    dependente = get_object_or_404(Dependente, pk=pk)
    
    if request.method == 'POST':
        form = DependenteForm(request.POST, request.FILES, instance=dependente)
        if form.is_valid():
            dependente = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Dependente atualizado com sucesso!',
                'reload': True,
                'dependente_id': dependente.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DependenteForm(instance=dependente)
    form_html = render(request, 'associados/forms/dependente_form_modal.html', {
        'form': form,
        'title': 'Editar Dependente'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def documento_modal_create(request):
    """
    View para criar documento via modal
    """
    associado_id = request.GET.get('associado')
    dependente_id = request.GET.get('dependente')
    
    associado = None
    dependente = None
    
    if associado_id:
        associado = get_object_or_404(Associado, pk=associado_id)
    if dependente_id:
        dependente = get_object_or_404(Dependente, pk=dependente_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, associado_id=associado_id, dependente_id=dependente_id)
        if form.is_valid():
            documento = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Documento criado com sucesso!',
                'reload': True,
                'documento_id': documento.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DocumentoForm(associado_id=associado_id, dependente_id=dependente_id)
    form_html = render(request, 'associados/forms/documento_form_modal.html', {
        'form': form,
        'associado': associado,
        'dependente': dependente,
        'title': 'Novo Documento'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def documento_modal_update(request, pk):
    """
    View para editar documento via modal
    """
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Documento atualizado com sucesso!',
                'reload': True,
                'documento_id': documento.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = DocumentoForm(instance=documento)
    form_html = render(request, 'associados/forms/documento_form_modal.html', {
        'form': form,
        'title': 'Editar Documento'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def pre_cadastro_modal(request):
    """
    View para pré-cadastro via modal
    """
    if request.method == 'POST':
        form = PreCadastroAssociadoForm(request.POST)
        if form.is_valid():
            pre_cadastro = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Pré-cadastro realizado com sucesso! Aguarde a aprovação.',
                'reload': False
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = PreCadastroAssociadoForm()
    form_html = render(request, 'associados/forms/pre_cadastro_form_modal.html', {
        'form': form,
        'title': 'Pré-Cadastro de Associado'
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def minha_ficha(request):
    """
    View para associados visualizarem suas próprias informações
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    context = {
        'associado': associado,
        'title': 'Minha Ficha',
        'subtitle': 'Informações Pessoais'
    }
    
    return render(request, 'associados/minha_ficha.html', context)


@login_required
def meus_atendimentos_juridicos(request):
    """
    View para associados visualizarem seus próprios atendimentos jurídicos - VERSÃO DEFINITIVA
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar atendimentos jurídicos do associado
    from assejus.models import AtendimentoJuridico
    
    # Query específica com relacionamentos otimizados
    atendimentos = AtendimentoJuridico.objects.select_related(
        'associado', 'advogado_responsavel', 'usuario_responsavel'
    ).filter(
        associado=associado
    ).order_by('-data_abertura')  # CAMPO CORRETO: data_abertura
    
    # Estatísticas dos atendimentos
    total_atendimentos = atendimentos.count()
    atendimentos_abertos = atendimentos.filter(status__in=['aberto', 'em_analise', 'em_andamento']).count()
    atendimentos_concluidos = atendimentos.filter(status='concluido').count()
    
    context = {
        'associado': associado,
        'atendimentos': atendimentos,
        'total_atendimentos': total_atendimentos,
        'atendimentos_abertos': atendimentos_abertos,
        'atendimentos_concluidos': atendimentos_concluidos,
        'title': 'Meus Atendimentos Jurídicos',
        'subtitle': 'Histórico de Atendimentos'
    }
    
    return render(request, 'associados/meus_atendimentos_juridicos.html', context)

# NOVA VIEW PARA EVITAR CONFLITOS DE CACHE
@login_required
def meus_atendimentos_juridicos_nova(request):
    """
    NOVA VIEW para associados visualizarem seus próprios atendimentos jurídicos
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar atendimentos jurídicos do associado
    from assejus.models import AtendimentoJuridico
    
    # Query específica com relacionamentos otimizados
    atendimentos = AtendimentoJuridico.objects.select_related(
        'associado', 'advogado_responsavel', 'usuario_responsavel'
    ).filter(
        associado=associado
    ).order_by('-data_abertura')  # CAMPO CORRETO: data_abertura
    
    # Estatísticas dos atendimentos
    total_atendimentos = atendimentos.count()
    atendimentos_abertos = atendimentos.filter(status__in=['aberto', 'em_analise', 'em_andamento']).count()
    atendimentos_concluidos = atendimentos.filter(status='concluido').count()
    
    context = {
        'associado': associado,
        'atendimentos': atendimentos,
        'total_atendimentos': total_atendimentos,
        'atendimentos_abertos': atendimentos_abertos,
        'atendimentos_concluidos': atendimentos_concluidos,
        'title': 'Meus Atendimentos Jurídicos',
        'subtitle': 'Histórico de Atendimentos'
    }
    
    return render(request, 'associados/meus_atendimentos_juridicos.html', context)


@login_required
def detalhes_atendimento_juridico(request, atendimento_id):
    """
    View para associados visualizarem detalhes completos de um atendimento jurídico
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar o atendimento específico
    from assejus.models import AtendimentoJuridico
    
    try:
        atendimento = AtendimentoJuridico.objects.select_related(
            'associado', 'advogado_responsavel', 'usuario_responsavel'
        ).get(
            id=atendimento_id,
            associado=associado  # Garantir que o atendimento pertence ao associado
        )
    except AtendimentoJuridico.DoesNotExist:
        messages.error(request, 'Atendimento não encontrado ou você não tem permissão para visualizá-lo.')
        return redirect('associados:meus_atendimentos_juridicos')
    
    # Criar histórico simulado baseado no status e datas
    historico = []
    
    # Adicionar entrada de abertura
    historico.append({
        'data': atendimento.data_abertura,
        'status': 'aberto',
        'descricao': 'Atendimento criado e aberto',
        'responsavel': 'Sistema'
    })
    
    # Adicionar entrada se foi atribuído a um advogado
    if atendimento.advogado_responsavel:
        historico.append({
            'data': atendimento.data_abertura,  # Usar data de abertura como referência
            'status': 'em_analise',
            'descricao': f'Atendimento atribuído ao advogado {atendimento.advogado_responsavel.nome}',
            'responsavel': atendimento.advogado_responsavel.nome
        })
    
    # Adicionar entrada baseada no status atual
    if atendimento.status != 'aberto':
        status_descriptions = {
            'em_analise': 'Atendimento em análise pelo advogado responsável',
            'em_andamento': 'Atendimento em andamento - ações sendo executadas',
            'aguardando_documentos': 'Aguardando envio de documentos pelo associado',
            'aguardando_decisao': 'Aguardando decisão judicial ou administrativa',
            'suspenso': 'Atendimento temporariamente suspenso',
            'concluido': 'Atendimento concluído com sucesso',
            'arquivado': 'Atendimento arquivado',
            'cancelado': 'Atendimento cancelado'
        }
        
        historico.append({
            'data': atendimento.data_conclusao if atendimento.data_conclusao else atendimento.data_abertura,
            'status': atendimento.status,
            'descricao': status_descriptions.get(atendimento.status, f'Status alterado para {atendimento.get_status_display()}'),
            'responsavel': atendimento.advogado_responsavel.nome if atendimento.advogado_responsavel else 'Sistema'
        })
    
    # Ordenar histórico por data (mais recente primeiro)
    historico.sort(key=lambda x: x['data'], reverse=True)
    
    context = {
        'atendimento': atendimento,
        'associado': associado,
        'historico': historico,
        'title': f'Detalhes do Atendimento - {atendimento.titulo}',
        'subtitle': 'Acompanhamento do Andamento'
    }
    
    return render(request, 'associados/detalhes_atendimento_juridico.html', context)


@login_required
def meus_atendimentos_psicologicos(request):
    """
    View para associados visualizarem seus próprios atendimentos psicológicos - REESCRITA
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar sessões psicológicas do associado
    from psicologia.models import Sessao, Paciente
    
    try:
        paciente = Paciente.objects.select_related('associado').get(associado=associado)
        
        # Query otimizada com relacionamentos
        atendimentos = Sessao.objects.select_related(
            'paciente', 'psicologo'
        ).filter(
            paciente=paciente
        ).order_by('-data_criacao')
        
        # Estatísticas das sessões
        total_sessoes = atendimentos.count()
        sessoes_realizadas = atendimentos.filter(status='realizada').count()
        sessoes_agendadas = atendimentos.filter(status__in=['agendada', 'confirmada']).count()
        
    except Paciente.DoesNotExist:
        atendimentos = Sessao.objects.none()
        total_sessoes = 0
        sessoes_realizadas = 0
        sessoes_agendadas = 0
    
    context = {
        'associado': associado,
        'atendimentos': atendimentos,
        'total_sessoes': total_sessoes,
        'sessoes_realizadas': sessoes_realizadas,
        'sessoes_agendadas': sessoes_agendadas,
        'title': 'Meus Atendimentos Psicológicos',
        'subtitle': 'Histórico de Atendimentos'
    }
    
    return render(request, 'associados/meus_atendimentos_psicologicos.html', context)


@login_required
def minhas_reservas_hotel(request):
    """
    View para associados visualizarem suas próprias reservas no hotel - VERSÃO CORRIGIDA
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar reservas do associado através da relação hospede->associado
    from hotel_transito.models import Reserva
    
    # Query otimizada com relacionamentos corretos
    reservas = Reserva.objects.select_related(
        'hospede', 'quarto'
    ).filter(
        hospede__associado=associado  # Relação correta: hospede -> associado
    ).order_by('-data_entrada')
    
    # Estatísticas das reservas
    total_reservas = reservas.count()
    reservas_ativas = reservas.filter(status__in=['confirmada', 'pendente']).count()
    reservas_concluidas = reservas.filter(status='finalizada').count()
    
    context = {
        'associado': associado,
        'reservas': reservas,
        'total_reservas': total_reservas,
        'reservas_ativas': reservas_ativas,
        'reservas_concluidas': reservas_concluidas,
        'title': 'Minhas Reservas',
        'subtitle': 'Histórico de Reservas no Hotel'
    }
    
    return render(request, 'associados/minhas_reservas_hotel.html', context)

# NOVA VIEW PARA EVITAR CONFLITOS DE CACHE
@login_required
def minhas_reservas_hotel_nova(request):
    """
    NOVA VIEW para associados visualizarem suas próprias reservas no hotel
    """
    if request.user.tipo_usuario != 'associado':
        messages.error(request, 'Acesso negado. Apenas associados podem acessar esta página.')
        return redirect('core:usuario_dashboard')
    
    try:
        associado = Associado.objects.get(usuario=request.user)
    except Associado.DoesNotExist:
        messages.error(request, 'Associado não encontrado.')
        return redirect('core:usuario_dashboard')
    
    # Buscar reservas do associado através da relação hospede->associado
    from hotel_transito.models import Reserva
    
    # Query otimizada com relacionamentos corretos
    reservas = Reserva.objects.select_related(
        'hospede', 'quarto'
    ).filter(
        hospede__associado=associado  # Relação correta: hospede -> associado
    ).order_by('-data_entrada')
    
    # Estatísticas das reservas
    total_reservas = reservas.count()
    reservas_ativas = reservas.filter(status__in=['confirmada', 'pendente']).count()
    reservas_concluidas = reservas.filter(status='finalizada').count()
    
    context = {
        'associado': associado,
        'reservas': reservas,
        'total_reservas': total_reservas,
        'reservas_ativas': reservas_ativas,
        'reservas_concluidas': reservas_concluidas,
        'title': 'Minhas Reservas',
        'subtitle': 'Histórico de Reservas no Hotel'
    }
    
    return render(request, 'associados/minhas_reservas_hotel.html', context)
