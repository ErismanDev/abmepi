from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Case, When, IntegerField, Value
from django.utils import timezone
from django.urls import reverse
from datetime import date, timedelta, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
import os


def get_logo_path(filename):
    """
    Retorna o caminho correto para a logo, tentando primeiro em static (desenvolvimento)
    e depois em staticfiles (produção)
    """
    from django.conf import settings
    
    # Tentar primeiro no diretório static (desenvolvimento)
    logo_path = os.path.join(settings.BASE_DIR, 'static', filename)
    if os.path.exists(logo_path):
        return logo_path
    
    # Se não existir, tentar no staticfiles (produção)
    logo_path = os.path.join(settings.STATIC_ROOT, filename)
    if os.path.exists(logo_path):
        return logo_path
    
    return None
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os
from django.conf import settings
from .models import (
    Advogado, AtendimentoJuridico, DocumentoJuridico, 
    Andamento, ConsultaJuridica, RelatorioJuridico, ProcessoJuridico,
    ProcuracaoAdJudicia
)
from .forms import (
    AdvogadoForm, AtendimentoJuridicoForm,
    AndamentoForm, ConsultaJuridicaForm, RelatorioJuridicoForm, ProcessoJuridicoForm,
    ProcuracaoAdJudiciaForm
)

User = get_user_model()
from core.permissions import (
    AssejusAccessMixin, AssejusFullAccessMixin,
    require_user_type, require_permission
)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def index(request):
    """Página principal do app ASEJUS"""
    # Estatísticas básicas para a página principal
    total_advogados = Advogado.objects.filter(ativo=True).count()
    total_atendimentos = AtendimentoJuridico.objects.count()
    total_consultas = ConsultaJuridica.objects.count()
    total_documentos = DocumentoJuridico.objects.count()
    total_andamentos = Andamento.objects.count()
    total_relatorios = RelatorioJuridico.objects.count()
    
    context = {
        'total_advogados': total_advogados,
        'total_atendimentos': total_atendimentos,
        'total_consultas': total_consultas,
        'total_documentos': total_documentos,
        'total_andamentos': total_andamentos,
        'total_relatorios': total_relatorios,
    }
    
    return render(request, 'assejus/index.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def dashboard(request):
    """Dashboard principal do app ASEJUS"""
    # Estatísticas básicas
    total_advogados = Advogado.objects.filter(ativo=True).count()
    total_atendimentos = AtendimentoJuridico.objects.count()
    atendimentos_em_andamento = AtendimentoJuridico.objects.filter(status='em_andamento').count()
    consultas_pendentes = ConsultaJuridica.objects.filter(resolvida=False).count()
    
    # Atendimentos recentes
    atendimentos_recentes = AtendimentoJuridico.objects.select_related('advogado_responsavel').order_by('-data_abertura')[:5]
    
    # Consultas recentes
    consultas_recentes = ConsultaJuridica.objects.order_by('-data_consulta')[:5]
    
    # Gráfico de atendimentos por tipo
    atendimentos_por_tipo = AtendimentoJuridico.objects.values('tipo_demanda').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Estatísticas adicionais
    total_documentos = DocumentoJuridico.objects.count()
    total_andamentos = Andamento.objects.count()
    total_relatorios = RelatorioJuridico.objects.count()
    
    # Atendimentos por prioridade
    atendimentos_urgentes = AtendimentoJuridico.objects.filter(prioridade='alta').count()
    atendimentos_medias = AtendimentoJuridico.objects.filter(prioridade='media').count()
    atendimentos_baixas = AtendimentoJuridico.objects.filter(prioridade='baixa').count()
    
    # Consultas por status
    consultas_pendentes = ConsultaJuridica.objects.exclude(status='respondida').count()
    
    context = {
        'total_advogados': total_advogados,
        'total_atendimentos': total_atendimentos,
        'atendimentos_em_andamento': atendimentos_em_andamento,
        'consultas_pendentes': consultas_pendentes,
        'atendimentos_recentes': atendimentos_recentes,
        'consultas_recentes': consultas_recentes,
        'atendimentos_por_tipo': atendimentos_por_tipo,
        'total_documentos': total_documentos,
        'total_andamentos': total_andamentos,
        'total_relatorios': total_relatorios,
        'atendimentos_urgentes': atendimentos_urgentes,
        'atendimentos_medias': atendimentos_medias,
        'atendimentos_baixas': atendimentos_baixas,
    }
    
    return render(request, 'assejus/dashboard.html', context)


# Views para Advogados
@require_user_type(['administrador_sistema', 'advogado'])
def advogado_list(request):
    """Lista de advogados com filtros avançados"""
    from .forms import AdvogadoSearchForm
    
    # Inicializar formulário de pesquisa
    search_form = AdvogadoSearchForm(request.GET)
    
    # Verificar se é admin/superuser ou advogado específico
    is_admin_or_superuser = (request.user.tipo_usuario == 'administrador_sistema' or 
                            request.user.is_superuser)
    
    
    # Se é advogado comum (não admin/superuser), redirecionar para seu perfil
    if request.user.tipo_usuario == 'advogado' and not is_admin_or_superuser:
        try:
            # Buscar o advogado associado ao usuário
            advogado = Advogado.objects.get(user=request.user)
            
            # Redirecionar para o perfil do advogado
            return redirect('assejus:advogado_detail', pk=advogado.pk)
            
        except Advogado.DoesNotExist:
            messages.error(request, 'Usuário advogado não encontrado. Contate o administrador.')
            return redirect('assejus:dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao carregar perfil: {str(e)}')
            return redirect('assejus:dashboard')
    else:
        # Admin/Superuser - mostrar lista completa
        advogados = Advogado.objects.all()
    
    # Aplicar filtros se o formulário for válido (apenas para administradores)
    if search_form.is_valid() and is_admin_or_superuser:
        nome = search_form.cleaned_data.get('nome')
        cpf = search_form.cleaned_data.get('cpf')
        oab = search_form.cleaned_data.get('oab')
        uf_oab = search_form.cleaned_data.get('uf_oab')
        situacao = search_form.cleaned_data.get('situacao')
        estado = search_form.cleaned_data.get('estado')
        ativo = search_form.cleaned_data.get('ativo')
        
        if nome:
            advogados = advogados.filter(nome__icontains=nome)
        
        if cpf:
            advogados = advogados.filter(cpf__icontains=cpf)
        
        if oab:
            advogados = advogados.filter(oab__icontains=oab)
        
        if uf_oab:
            advogados = advogados.filter(uf_oab=uf_oab)
        
        if situacao:
            advogados = advogados.filter(situacao=situacao)
        
        if estado:
            advogados = advogados.filter(estado=estado)
        
        if ativo:
            if ativo == 'true':
                advogados = advogados.filter(ativo=True)
            elif ativo == 'false':
                advogados = advogados.filter(ativo=False)
    
    # Ordenar por nome
    advogados = advogados.order_by('nome')
    
    # Estatísticas
    total_advogados = Advogado.objects.count()
    advogados_ativos = Advogado.objects.filter(ativo=True).count()
    
    # Paginação
    paginator = Paginator(advogados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'advogados': page_obj.object_list,  # Lista de advogados para o template
        'page_obj': page_obj,               # Objeto de paginação
        'search_form': search_form,         # Formulário de pesquisa
        'total_advogados': total_advogados, # Total de advogados
        'advogados_ativos': advogados_ativos, # Total de advogados ativos
        'is_paginated': page_obj.has_other_pages(), # Se há paginação
        'has_advogados': advogados.exists(), # Se há advogados para exibir
        'is_admin_view': is_admin_or_superuser, # Flag para identificar se é visualização de admin
    }
    
    return render(request, 'assejus/advogado_list.html', context)


@require_user_type(['administrador_sistema', 'advogado'])
def advogado_create(request):
    """Criar novo advogado"""
    # RESTRIÇÃO: Usuário advogado não pode criar novos advogados
    if request.user.tipo_usuario == 'advogado':
        messages.error(request, 'Você não tem permissão para criar novos advogados.')
        return redirect('assejus:advogado_list')
    
    if request.method == 'POST':
        form = AdvogadoForm(request.POST, request.FILES)
        if form.is_valid():
            advogado = form.save()
            messages.success(request, 'Advogado criado com sucesso!')
            return redirect('assejus:advogado_detail', pk=advogado.pk)
    else:
        form = AdvogadoForm()
    
    context = {
        'form': form,
        'title': 'Novo Advogado',
        'action': 'Criar',
    }
    
    return render(request, 'assejus/advogado_form.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def advogado_detail(request, pk):
    """View para exibir detalhes completos do advogado"""
    try:
        advogado = get_object_or_404(Advogado, pk=pk)
        
        # Calcular estatísticas do advogado
        total_casos = AtendimentoJuridico.objects.filter(advogado_responsavel=advogado).count()
        casos_em_andamento = AtendimentoJuridico.objects.filter(
            advogado_responsavel=advogado,
            status__in=['em_andamento', 'em_analise', 'aguardando_documentos', 'aguardando_decisao']
        ).count()
        casos_concluidos = AtendimentoJuridico.objects.filter(
            advogado_responsavel=advogado,
            status='concluido'
        ).count()
        
        # Buscar atendimentos do advogado
        atendimentos = AtendimentoJuridico.objects.filter(
            advogado_responsavel=advogado
        ).select_related('associado').order_by('-data_abertura')
        
        context = {
            'advogado': advogado,
            'total_casos': total_casos,
            'casos_em_andamento': casos_em_andamento,
            'casos_concluidos': casos_concluidos,
            'atendimentos': atendimentos,
        }
        
        return render(request, 'assejus/advogado_detail.html', context)
        
    except Exception as e:
        import traceback
        
        # Redirecionar para lista com mensagem de erro
        messages.error(request, f'Erro ao carregar detalhes do advogado: {str(e)}')
        return redirect('assejus:advogado_list')


@require_user_type(['administrador_sistema', 'advogado'])
def advogado_update(request, pk):
    """Editar advogado"""
    advogado = get_object_or_404(Advogado, pk=pk)
    
    # RESTRIÇÃO: Usuário advogado só pode editar seu próprio cadastro
    if request.user.tipo_usuario == 'advogado':
        try:
            # Buscar o advogado associado ao usuário
            advogado_usuario = Advogado.objects.get(user=request.user)
            
            # Verificar se o advogado a ser editado é o próprio usuário
            if advogado.pk != advogado_usuario.pk:
                messages.error(request, 'Você não tem permissão para editar este cadastro.')
                return redirect('assejus:advogado_list')
                
        except Advogado.DoesNotExist:
            messages.error(request, 'Erro de configuração: Usuário advogado não encontrado.')
            return redirect('assejus:advogado_list')
        except Exception as e:
            messages.error(request, 'Erro ao verificar permissões.')
            return redirect('assejus:advogado_list')
    
    if request.method == 'POST':
        form = AdvogadoForm(request.POST, request.FILES, instance=advogado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advogado atualizado com sucesso!')
            return redirect('assejus:advogado_detail', pk=advogado.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # Garante que todos os dados sejam carregados corretamente
        form = AdvogadoForm(instance=advogado)
        
        # Debug para verificar os dados carregados
        
        # Verifica se o formulário foi inicializado corretamente
    
    context = {
        'form': form,
        'advogado': advogado,
        'title': 'Editar Advogado',
        'action': 'Atualizar',
    }
    
    return render(request, 'assejus/advogado_form.html', context)


@require_user_type(['administrador_sistema', 'advogado'])
def advogado_debug(request, pk):
    """Debug do formulário de advogado"""
    advogado = get_object_or_404(Advogado, pk=pk)
    form = AdvogadoForm(instance=advogado)
    
    context = {
        'form': form,
        'advogado': advogado,
        'title': 'Debug - Editar Advogado',
        'action': 'Debug',
    }
    
    return render(request, 'assejus/advogado_form_debug.html', context)


@require_user_type(['administrador_sistema'])
def advogado_delete(request, pk):
    """Excluir advogado"""
    advogado = get_object_or_404(Advogado, pk=pk)
    
    if request.method == 'POST':
        advogado.delete()
        messages.success(request, 'Advogado excluído com sucesso!')
        return redirect('assejus:advogado_list')
    
    context = {
        'advogado': advogado,
    }
    
    return render(request, 'assejus/advogado_confirm_delete.html', context)


# Views para Atendimentos Jurídicos
@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def atendimento_list(request):
    """Lista de atendimentos jurídicos"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    tipo_demanda = request.GET.get('tipo_demanda', '')
    
    # Base inicial de atendimentos
    atendimentos = AtendimentoJuridico.objects.all()
    
    # RESTRIÇÃO: Usuário advogado só vê atendimentos onde ele é responsável
    if request.user.tipo_usuario == 'advogado':
        try:
            # Buscar o advogado associado ao usuário
            advogado = Advogado.objects.get(user=request.user)
            
            # Filtrar apenas atendimentos onde o advogado é responsável
            atendimentos = atendimentos.filter(advogado_responsavel=advogado)
            
        except Advogado.DoesNotExist:
            # Se não encontrar o advogado, não mostrar nenhum atendimento
            atendimentos = AtendimentoJuridico.objects.none()
        except Exception as e:
            atendimentos = AtendimentoJuridico.objects.none()
    
    # Aplicar filtros de busca
    if search:
        atendimentos = atendimentos.filter(
            Q(titulo__icontains=search) |
            Q(associado__nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    if status:
        atendimentos = atendimentos.filter(status=status)
    
    if tipo_demanda:
        atendimentos = atendimentos.filter(tipo_demanda=tipo_demanda)
    
    # Ordenação: primeiro por status (concluídos por último), depois por data de abertura
    atendimentos = atendimentos.order_by(
        Case(
            When(status='concluido', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
        '-data_abertura'
    )
    
    # Estatísticas para o contexto
    total_atendimentos = atendimentos.count()
    atendimentos_ativos = atendimentos.exclude(status='concluido').count()
    atendimentos_concluidos = atendimentos.filter(status='concluido').count()
    
    # Verifica se há transição entre ativos e concluídos
    tem_transicao = atendimentos_ativos > 0 and atendimentos_concluidos > 0
    
    # Paginação
    paginator = Paginator(atendimentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'atendimentos': page_obj,
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'tipo_demanda': tipo_demanda,
        'total_atendimentos': total_atendimentos,
        'atendimentos_ativos': atendimentos_ativos,
        'atendimentos_concluidos': atendimentos_concluidos,
        'tem_transicao': tem_transicao,
        'is_advogado_restricted': request.user.tipo_usuario == 'advogado',
    }
    
    return render(request, 'assejus/atendimento_list.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def atendimento_create(request):
    """Criar novo atendimento jurídico"""
    if request.method == 'POST':
        form = AtendimentoJuridicoForm(request.POST)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario_responsavel = request.user
            atendimento.save()
            form.save_m2m()
            messages.success(request, 'Atendimento criado com sucesso!')
            return redirect('assejus:atendimento_detail', pk=atendimento.pk)
    else:
        form = AtendimentoJuridicoForm()
    
    context = {
        'form': form,
        'title': 'Novo Atendimento Jurídico',
        'action': 'Criar',
    }
    
    return render(request, 'assejus/atendimento_form.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def atendimento_detail(request, pk):
    """Detalhes do atendimento jurídico - redireciona para processo se existir"""
    atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
    
    # Se o atendimento tem número de processo, redirecionar para a página do processo
    if atendimento.numero_processo:
        try:
            # Buscar processo pelo número
            processo = ProcessoJuridico.objects.get(numero_processo=atendimento.numero_processo)
            # Redirecionar para a página do processo
            return redirect('assejus:processo_detail', pk=processo.pk)
        except ProcessoJuridico.DoesNotExist:
            # Processo não existe ainda, mostrar página de atendimento com aviso
            pass
    
    # Se não tem processo ou processo não existe, mostrar página de atendimento
    context = {
        'atendimento': atendimento,
    }
    
    return render(request, 'assejus/atendimento_detail.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def atendimento_update(request, pk):
    """Editar atendimento jurídico"""
    atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
    
    # RESTRIÇÃO: Usuário advogado só pode editar atendimentos onde ele é responsável
    if request.user.tipo_usuario == 'advogado':
        try:
            # Buscar o advogado associado ao usuário
            advogado = Advogado.objects.get(user=request.user)
            
            # Verificar se o atendimento pertence ao advogado
            if atendimento.advogado_responsavel != advogado:
                messages.error(request, 'Você não tem permissão para editar este atendimento.')
                return redirect('assejus:atendimento_list')
                
        except Advogado.DoesNotExist:
            messages.error(request, 'Erro de configuração: Usuário advogado não encontrado.')
            return redirect('assejus:atendimento_list')
        except Exception as e:
            messages.error(request, 'Erro ao verificar permissões.')
            return redirect('assejus:atendimento_list')
    
    if request.method == 'POST':
        form = AtendimentoJuridicoForm(request.POST, instance=atendimento)
        if form.is_valid():
            # RESTRIÇÃO: Para usuário advogado, garantir que o advogado responsável não seja alterado
            if request.user.tipo_usuario == 'advogado':
                try:
                    advogado = Advogado.objects.get(user=request.user)
                    form.instance.advogado_responsavel = advogado
                except Exception as e:
                    pass
            
            form.save()
            messages.success(request, 'Atendimento atualizado com sucesso!')
            return redirect('assejus:atendimento_detail', pk=atendimento.pk)
    else:
        form = AtendimentoJuridicoForm(instance=atendimento)
        
        # RESTRIÇÃO: Para usuário advogado, restringir campo advogado_responsavel
        if request.user.tipo_usuario == 'advogado':
            try:
                advogado = Advogado.objects.get(user=request.user)
                form.fields['advogado_responsavel'].queryset = Advogado.objects.filter(pk=advogado.pk)
                form.fields['advogado_responsavel'].widget.attrs['readonly'] = True
            except Exception as e:
                pass
    
    context = {
        'form': form,
        'atendimento': atendimento,
        'title': 'Editar Atendimento Jurídico',
        'action': 'Atualizar',
    }
    
    return render(request, 'assejus/atendimento_form.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def atendimento_finalizar(request, pk):
    """Finalizar atendimento jurídico"""
    atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
    
    # RESTRIÇÃO: Usuário advogado só pode finalizar atendimentos onde ele é responsável
    if request.user.tipo_usuario == 'advogado':
        try:
            # Buscar o advogado associado ao usuário
            advogado = Advogado.objects.get(user=request.user)
            
            # Verificar se o atendimento pertence ao advogado
            if atendimento.advogado_responsavel != advogado:
                messages.error(request, 'Você não tem permissão para finalizar este atendimento.')
                return redirect('assejus:atendimento_list')
                
        except Advogado.DoesNotExist:
            messages.error(request, 'Erro de configuração: Usuário advogado não encontrado.')
            return redirect('assejus:atendimento_list')
        except Exception as e:
            messages.error(request, 'Erro ao verificar permissões.')
            return redirect('assejus:atendimento_list')
    
    if request.method == 'POST':
        # Verifica se o atendimento já não está finalizado
        if atendimento.status == 'concluido':
            messages.warning(request, 'Este atendimento já está finalizado.')
        else:
            # Atualiza o status para concluído
            atendimento.status = 'concluido'
            atendimento.data_conclusao = timezone.now()
            atendimento.save()
            
            messages.success(request, 'Atendimento finalizado com sucesso!')
        
        return redirect('assejus:atendimento_detail', pk=atendimento.pk)
    
    context = {
        'atendimento': atendimento,
        'title': 'Finalizar Atendimento',
    }
    
    return render(request, 'assejus/atendimento_confirm_finalizar.html', context)


@login_required
def atendimento_delete(request, pk):
    """Excluir atendimento jurídico"""
    atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
    
    # RESTRIÇÃO: Usuário advogado só pode excluir atendimentos onde ele é responsável
    if request.user.tipo_usuario == 'advogado':
        try:
            # Buscar o advogado associado ao usuário
            advogado = Advogado.objects.get(user=request.user)
            
            # Verificar se o atendimento pertence ao advogado
            if atendimento.advogado_responsavel != advogado:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Você não tem permissão para excluir este atendimento.'
                    })
                else:
                    messages.error(request, 'Você não tem permissão para excluir este atendimento.')
                    return redirect('assejus:atendimento_list')
                
        except Advogado.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erro de configuração: Usuário advogado não encontrado.'
                })
            else:
                messages.error(request, 'Erro de configuração: Usuário advogado não encontrado.')
                return redirect('assejus:atendimento_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erro ao verificar permissões.'
                })
            else:
                messages.error(request, 'Erro ao verificar permissões.')
                return redirect('assejus:atendimento_list')
    
    if request.method == 'POST':
        try:
            atendimento.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Atendimento excluído com sucesso!'
                })
            else:
                messages.success(request, 'Atendimento excluído com sucesso!')
                return redirect('assejus:atendimento_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao excluir atendimento: {str(e)}'
                })
            else:
                messages.error(request, f'Erro ao excluir atendimento: {str(e)}')
                return redirect('assejus:atendimento_list')
    
    # Se não for POST, mostrar confirmação
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    else:
        context = {
            'atendimento': atendimento,
        }
        return render(request, 'assejus/atendimento_confirm_delete.html', context)


@login_required
def atendimento_delete_ajax(request, pk):
    """Excluir atendimento jurídico via AJAX"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
        atendimento.delete()
        return JsonResponse({
            'success': True,
            'message': 'Atendimento excluído com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao excluir atendimento: {str(e)}'
        })


# =============================================================================
# VIEWS PARA SISTEMA DE DOCUMENTOS DE PROCESSOS JURÍDICOS
# =============================================================================

@login_required
def documento_list(request):
    """
    Lista de documentos jurídicos com filtros avançados
    Sistema completo de busca e paginação
    """
    from core.forms import DocumentoProcessoSearchForm
    
    # Inicializar formulário de busca
    search_form = DocumentoProcessoSearchForm(request.GET)
    
    # Query base
    documentos = DocumentoJuridico.objects.select_related(
        'processo', 'usuario_upload', 'processo__parte_cliente'
    ).all()
    
    # Aplicar filtros se formulário for válido
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search', '').strip()
        tipo_documento = search_form.cleaned_data.get('tipo_documento')
        processo = search_form.cleaned_data.get('processo')
        data_inicio = search_form.cleaned_data.get('data_inicio')
        data_fim = search_form.cleaned_data.get('data_fim')
        usuario_upload = search_form.cleaned_data.get('usuario_upload')
        
        # Filtro de busca textual
        if search:
            documentos = documentos.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(processo__numero_processo__icontains=search) |
                Q(processo__parte_cliente__nome__icontains=search)
            )
        
        # Filtros específicos
        if tipo_documento:
            documentos = documentos.filter(tipo_documento=tipo_documento)
        
        if processo:
            documentos = documentos.filter(processo=processo)
        
        if data_inicio:
            documentos = documentos.filter(data_upload__date__gte=data_inicio)
        
        if data_fim:
            documentos = documentos.filter(data_upload__date__lte=data_fim)
        
        if usuario_upload:
            documentos = documentos.filter(usuario_upload=usuario_upload)
    
    # Ordenação
    documentos = documentos.order_by('-data_upload')
    
    # Paginação
    paginator = Paginator(documentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_documentos = DocumentoJuridico.objects.count()
    documentos_hoje = DocumentoJuridico.objects.filter(
        data_upload__date=timezone.now().date()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_documentos': total_documentos,
        'documentos_hoje': documentos_hoje,
        'title': 'Documentos Jurídicos',
    }
    
    return render(request, 'assejus/documento_list.html', context)


@login_required
def documento_create(request):
    """
    Criar novo documento jurídico
    Upload único
    """
    from core.forms import DocumentoProcessoForm
    
    processo_id = request.GET.get('processo')
    
    if request.method == 'POST':
        form = DocumentoProcessoForm(
            request.POST, 
            request.FILES, 
            processo_id=processo_id,
            usuario=request.user
        )
        
        if form.is_valid():
            try:
                documento = form.save()
                messages.success(request, 'Documento criado com sucesso!')
                
                # Redirecionar baseado no contexto
                if processo_id:
                    return redirect('assejus:processo_detail', pk=processo_id)
                else:
                    return redirect('assejus:documento_list')
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar documento: {str(e)}')
                import traceback
                traceback.print_exc()
    else:
        form = DocumentoProcessoForm(
            processo_id=processo_id,
            usuario=request.user
        )
    
    # Buscar informações do processo se fornecido
    processo_info = None
    if processo_id:
        try:
            processo_info = ProcessoJuridico.objects.get(pk=processo_id)
        except ProcessoJuridico.DoesNotExist:
            messages.error(request, 'Processo não encontrado.')
            return redirect('assejus:documento_list')
    
    context = {
        'form': form,
        'title': 'Novo Documento Jurídico',
        'action': 'Criar',
        'processo_id': processo_id,
        'processo_info': processo_info,
    }
    
    return render(request, 'assejus/documento_form.html', context)


@login_required
def documento_detail(request, pk):
    """
    Detalhes do documento jurídico
    Inclui informações de metadados e histórico
    """
    documento = get_object_or_404(
        DocumentoJuridico.objects.select_related(
            'processo', 'usuario_upload', 'processo__parte_cliente'
        ), 
        pk=pk
    )
    
    # Verificar permissões (opcional - implementar conforme necessário)
    # if not request.user.has_perm('assejus.view_documentojuridico'):
    #     messages.error(request, 'Você não tem permissão para visualizar este documento.')
    #     return redirect('assejus:documento_list')
    
    context = {
        'documento': documento,
        'title': f'Documento: {documento.titulo}',
    }
    
    return render(request, 'assejus/documento_detail.html', context)


@login_required
def documento_update(request, pk):
    """
    Editar documento jurídico
    Permite editar metadados e substituir arquivo
    """
    from core.forms import DocumentoProcessoEditForm, DocumentoProcessoReplaceForm
    
    documento = get_object_or_404(DocumentoJuridico, pk=pk)
    acao = request.GET.get('acao', 'editar')  # 'editar' ou 'substituir'
    
    if request.method == 'POST':
        if acao == 'substituir':
            form = DocumentoProcessoReplaceForm(request.POST, request.FILES, instance=documento)
        else:
            form = DocumentoProcessoEditForm(request.POST, instance=documento)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Documento atualizado com sucesso!')
                return redirect('assejus:documento_detail', pk=documento.pk)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar documento: {str(e)}')
    else:
        if acao == 'substituir':
            form = DocumentoProcessoReplaceForm(instance=documento)
        else:
            form = DocumentoProcessoEditForm(instance=documento)
    
    context = {
        'form': form,
        'documento': documento,
        'title': f'Editar Documento: {documento.titulo}',
        'action': 'Atualizar',
        'acao': acao,
    }
    
    return render(request, 'assejus/documento_form.html', context)


@login_required
def documento_delete(request, pk):
    """
    Excluir documento jurídico
    Confirmação obrigatória
    """
    documento = get_object_or_404(DocumentoJuridico, pk=pk)
    
    if request.method == 'POST':
        try:
            # Armazenar informações para mensagem
            titulo = documento.titulo
            processo_numero = documento.processo.numero_processo
            
            # Excluir arquivo físico se existir
            if documento.arquivo and documento.arquivo.name:
                try:
                    documento.arquivo.delete(save=False)
                except Exception as e:
                    pass
            
            # Excluir registro do banco
            documento.delete()
            
            messages.success(
                request, 
                f'Documento "{titulo}" do processo {processo_numero} foi excluído com sucesso!'
            )
            
            # Redirecionar baseado no contexto
            processo_id = request.POST.get('processo_id')
            if processo_id:
                return redirect('assejus:processo_detail', pk=processo_id)
            else:
                return redirect('assejus:documento_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao excluir documento: {str(e)}')
    
    context = {
        'documento': documento,
        'title': f'Excluir Documento: {documento.titulo}',
    }
    
    return render(request, 'assejus/documento_confirm_delete.html', context)


@login_required
def documento_download(request, pk):
    """
    Download de documento jurídico
    Com controle de acesso e logging
    """
    documento = get_object_or_404(DocumentoJuridico, pk=pk)
    
    # Verificar se arquivo existe
    if not documento.arquivo or not documento.arquivo.name:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('assejus:documento_detail', pk=pk)
    
    try:
        # Log do download (opcional)
        
        # Preparar resposta de download
        response = HttpResponse(
            documento.arquivo.read(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{documento.arquivo.name}"'
        response['Content-Length'] = documento.arquivo.size
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao fazer download: {str(e)}')
        return redirect('assejus:documento_detail', pk=pk)


@login_required
def documento_view(request, pk):
    """
    Visualizar documento no navegador
    Para PDFs e imagens
    """
    documento = get_object_or_404(DocumentoJuridico, pk=pk)
    
    if not documento.arquivo or not documento.arquivo.name:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('assejus:documento_detail', pk=pk)
    
    # Verificar se é um tipo que pode ser visualizado no navegador
    nome_arquivo = documento.arquivo.name.lower()
    tipos_visualizaveis = ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
    
    if not any(nome_arquivo.endswith(ext) for ext in tipos_visualizaveis):
        messages.info(request, 'Este tipo de arquivo não pode ser visualizado no navegador.')
        return redirect('assejus:documento_download', pk=pk)
    
    try:
        # Preparar resposta para visualização
        response = HttpResponse(
            documento.arquivo.read(),
            content_type='application/pdf' if nome_arquivo.endswith('.pdf') else 'image/jpeg'
        )
        response['Content-Disposition'] = f'inline; filename="{documento.arquivo.name}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao visualizar arquivo: {str(e)}')
        return redirect('assejus:documento_detail', pk=pk)


# =============================================================================
# VIEWS AJAX PARA DOCUMENTOS
# =============================================================================

@login_required
def documento_upload_ajax(request):
    """
    Upload de documento via AJAX
    Retorna JSON com resultado
    """
    from core.forms import DocumentoProcessoForm
    from django.http import JsonResponse
    
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        processo_id = request.POST.get('processo_id')
        
        form = DocumentoProcessoForm(
            request.POST,
            request.FILES,
            processo_id=processo_id,
            usuario=request.user
        )
        
        if not form.is_valid():
            pass
        
        if form.is_valid():
            documento = form.save()
            
            try:
                url_download = reverse('assejus:documento_download', args=[documento.id])
                url_view = reverse('assejus:documento_view', args=[documento.id])
            except Exception as e:
                url_download = f"/assejus/documentos/{documento.id}/download/"
                url_view = f"/assejus/documentos/{documento.id}/visualizar/"
            
            response_data = {
                'success': True,
                'message': 'Documento criado com sucesso!',
                'reload': True,  # Flag para recarregar a página
                'documento': {
                    'id': documento.id,
                    'titulo': documento.titulo,
                    'tipo': documento.get_tipo_documento_display(),
                    'data_upload': documento.data_upload.strftime('%d/%m/%Y %H:%M'),
                    'tamanho': documento.tamanho_arquivo,
                    'url_download': url_download,
                    'url_view': url_view,
                }
            }
            return JsonResponse(response_data)
        else:
            # Retornar erros de validação
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Erro de validação',
                'errors': errors
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def documento_upload_multiplo_ajax(request):
    """
    Upload múltiplo de documentos via AJAX
    Retorna JSON com resultado
    """
    from core.forms import DocumentoProcessoMultiploForm
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        processo_id = request.POST.get('processo_id')
        arquivos = request.FILES.getlist('arquivo_multiplo')
        
        if not arquivos:
            return JsonResponse({
                'success': False,
                'message': 'Nenhum arquivo foi selecionado.'
            })
        
        form = DocumentoProcessoMultiploForm(
            request.POST,
            processo_id=processo_id,
            usuario=request.user
        )
        
        if form.is_valid():
            documentos_criados = []
            tipo_documento = form.cleaned_data['tipo_documento']
            descricao = form.cleaned_data.get('descricao', '')
            
            for arquivo in arquivos:
                # Criar documento para cada arquivo
                from assejus.models import DocumentoJuridico
                
                # Gerar título baseado no nome do arquivo
                nome_base = arquivo.name.rsplit('.', 1)[0]
                titulo = nome_base.replace('_', ' ').replace('-', ' ').title()
                
                documento = DocumentoJuridico.objects.create(
                    titulo=titulo,
                    tipo_documento=tipo_documento,
                    descricao=descricao,
                    arquivo=arquivo,
                    processo_id=processo_id,
                    usuario_upload=request.user
                )
                
                documentos_criados.append(documento)
            
            return JsonResponse({
                'success': True,
                'message': f'{len(documentos_criados)} documentos criados com sucesso!',
                'documentos': [
                    {
                        'id': doc.id,
                        'titulo': doc.titulo,
                        'tipo': doc.get_tipo_documento_display(),
                        'data_upload': doc.data_upload.strftime('%d/%m/%Y %H:%M'),
                        'tamanho': doc.tamanho_arquivo,
                        'url_download': reverse('assejus:documento_download', args=[doc.id]),
                        'url_view': reverse('assejus:documento_view', args=[doc.id]),
                    }
                    for doc in documentos_criados
                ]
            })
        else:
            # Retornar erros de validação
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Erro de validação',
                'errors': errors
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def documento_list_ajax(request):
    """
    Lista de documentos via AJAX
    Para carregamento dinâmico
    """
    from core.forms import DocumentoProcessoSearchForm
    from django.http import JsonResponse
    
    try:
        # Inicializar formulário de busca
        search_form = DocumentoProcessoSearchForm(request.GET)
        
        # Query base
        documentos = DocumentoJuridico.objects.select_related(
            'processo', 'usuario_upload', 'processo__parte_cliente'
        ).all()
        
        # Aplicar filtros se formulário for válido
        if search_form.is_valid():
            search = search_form.cleaned_data.get('search', '').strip()
            tipo_documento = search_form.cleaned_data.get('tipo_documento')
            processo = search_form.cleaned_data.get('processo')
            data_inicio = search_form.cleaned_data.get('data_inicio')
            data_fim = search_form.cleaned_data.get('data_fim')
            usuario_upload = search_form.cleaned_data.get('usuario_upload')
            
            # Aplicar filtros (mesmo código da view normal)
            if search:
                documentos = documentos.filter(
                    Q(titulo__icontains=search) |
                    Q(descricao__icontains=search) |
                    Q(processo__numero_processo__icontains=search) |
                    Q(processo__parte_cliente__nome__icontains=search)
                )
            
            if tipo_documento:
                documentos = documentos.filter(tipo_documento=tipo_documento)
            
            if processo:
                documentos = documentos.filter(processo=processo)
            
            if data_inicio:
                documentos = documentos.filter(data_upload__date__gte=data_inicio)
            
            if data_fim:
                documentos = documentos.filter(data_upload__date__lte=data_fim)
            
            if usuario_upload:
                documentos = documentos.filter(usuario_upload=usuario_upload)
        
        # Ordenação e paginação
        documentos = documentos.order_by('-data_upload')
        
        # Paginação
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        paginator = Paginator(documentos, per_page)
        page_obj = paginator.get_page(page)
        
        # Preparar dados para JSON
        documentos_data = []
        for documento in page_obj:
            documentos_data.append({
                'id': documento.id,
                'titulo': documento.titulo,
                'tipo': documento.get_tipo_documento_display(),
                'descricao': documento.descricao or '',
                'processo_numero': documento.processo.numero_processo,
                'processo_cliente': documento.processo.parte_cliente.nome,
                'data_upload': documento.data_upload.strftime('%d/%m/%Y %H:%M'),
                'usuario_upload': documento.usuario_upload.get_full_name() if documento.usuario_upload else 'Sistema',
                'tamanho': documento.tamanho_arquivo,
                'url_detail': reverse('assejus:documento_detail', args=[documento.id]),
                'url_download': reverse('assejus:documento_download', args=[documento.id]),
                'url_view': reverse('assejus:documento_view', args=[documento.id]),
                'url_edit': reverse('assejus:documento_update', args=[documento.id]),
                'url_delete': reverse('assejus:documento_delete', args=[documento.id]),
            })
        
        return JsonResponse({
            'success': True,
            'documentos': documentos_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def documento_delete_ajax(request, pk):
    """
    Excluir documento via AJAX
    """
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        documento = get_object_or_404(DocumentoJuridico, pk=pk)
        
        # Armazenar informações para resposta
        titulo = documento.titulo
        processo_numero = documento.processo.numero_processo
        
        # Excluir arquivo físico se existir
        if documento.arquivo and documento.arquivo.name:
            try:
                documento.arquivo.delete(save=False)
            except Exception as e:
                pass
        
        # Excluir registro do banco
        documento.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Documento "{titulo}" do processo {processo_numero} foi excluído com sucesso!'
        })
        
    except DocumentoJuridico.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Documento não encontrado'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def documento_update_ajax(request, pk):
    """
    Atualizar documento via AJAX
    """
    from core.forms import DocumentoProcessoEditForm, DocumentoProcessoReplaceForm
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        documento = get_object_or_404(DocumentoJuridico, pk=pk)
        acao = request.POST.get('acao', 'editar')
        
        if acao == 'substituir':
            form = DocumentoProcessoReplaceForm(request.POST, request.FILES, instance=documento)
        else:
            form = DocumentoProcessoEditForm(request.POST, instance=documento)
        
        if form.is_valid():
            form.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Documento atualizado com sucesso!',
                'documento': {
                    'id': documento.id,
                    'titulo': documento.titulo,
                    'tipo': documento.get_tipo_documento_display(),
                    'descricao': documento.descricao or '',
                    'data_upload': documento.data_upload.strftime('%d/%m/%Y %H:%M'),
                    'tamanho': documento.tamanho_arquivo,
                    'url_download': reverse('assejus:documento_download', args=[documento.id]),
                    'url_view': reverse('assejus:documento_view', args=[documento.id]),
                }
            })
        else:
            # Retornar erros de validação
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Erro de validação',
                'errors': errors
            })
            
    except DocumentoJuridico.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Documento não encontrado'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def documento_delete(request, pk):
    """Excluir documento jurídico"""
    documento = get_object_or_404(DocumentoJuridico, pk=pk)
    
    if request.method == 'POST':
        processo_id = documento.processo.id
        documento.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('assejus:processo_detail', pk=processo_id)
    
    context = {
        'documento': documento,
    }
    
    return render(request, 'assejus/documento_confirm_delete.html', context)


# Views para Andamentos
@login_required
def andamento_list(request):
    """Lista de andamentos"""
    search = request.GET.get('search', '')
    
    andamentos = Andamento.objects.all()
    
    if search:
        andamentos = andamentos.filter(
            Q(descricao_detalhada__icontains=search) |
            Q(processo__numero_processo__icontains=search) |
            Q(processo__parte_cliente__nome__icontains=search) |
            Q(tipo_andamento__icontains=search)
        )
    
    andamentos = andamentos.order_by('-data_andamento')
    
    # Paginação
    paginator = Paginator(andamentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'assejus/andamento_list.html', context)


@login_required
def andamento_create(request):
    """Criar novo andamento"""
    
    if request.method == 'POST':
        form = AndamentoForm(request.POST)
        if form.is_valid():
            andamento = form.save(commit=False)
            andamento.usuario_registro = request.user
            andamento.save()
            form.save_m2m()
            messages.success(request, 'Andamento criado com sucesso!')
            # Redirecionar para a página do processo ao invés da página do andamento
            return redirect('assejus:processo_detail', pk=andamento.processo.pk)
        else:
            pass
    else:
        # Verificar se há um processo específico na URL
        processo_id = request.GET.get('processo')
        atendimento_id = request.GET.get('atendimento')
        initial_data = {}
        
        
        if processo_id:
            try:
                processo = ProcessoJuridico.objects.get(pk=processo_id)
                initial_data['processo'] = processo
            except ProcessoJuridico.DoesNotExist:
                pass
        elif atendimento_id:
            try:
                atendimento = AtendimentoJuridico.objects.get(pk=atendimento_id)
                
                # Se o atendimento tem número de processo, buscar ou criar o processo correspondente
                if atendimento.numero_processo:
                    try:
                        # Tentar encontrar um processo existente com o mesmo número
                        processo = ProcessoJuridico.objects.get(numero_processo=atendimento.numero_processo)
                    except ProcessoJuridico.DoesNotExist:
                        # Criar um novo processo baseado no atendimento
                        processo = ProcessoJuridico.objects.create(
                            numero_processo=atendimento.numero_processo,
                            vara_tribunal=atendimento.vara or 'Não informado',
                            tipo_acao='outro',  # Tipo padrão
                            parte_cliente=atendimento.associado,
                            parte_contraria='Não informado',
                            advogado_responsavel=atendimento.usuario_responsavel,
                            situacao_atual='andamento',
                            observacoes_gerais=f'Processo criado automaticamente a partir do atendimento: {atendimento.titulo}'
                        )
                    
                    initial_data['processo'] = processo
                else:
                    messages.warning(request, 'Este atendimento não possui número de processo. É necessário criar um processo judicial primeiro.')
                    
            except AtendimentoJuridico.DoesNotExist:
                messages.error(request, 'Atendimento não encontrado.')
                pass
        
        form = AndamentoForm(initial=initial_data)
    
    # Buscar processos para o contexto
    processos = ProcessoJuridico.objects.filter(
        situacao_atual__in=['andamento', 'suspenso']
    ).order_by('-data_cadastro')
    
    
    context = {
        'form': form,
        'processos': processos,
        'title': 'Novo Andamento',
        'action': 'Criar',
    }
    
    return render(request, 'assejus/andamento_form.html', context)


@login_required
def andamento_detail(request, pk):
    """Detalhes do andamento"""
    andamento = get_object_or_404(Andamento, pk=pk)
    
    # Verificar se o advogado tem permissão para ver este andamento
    if request.user.tipo_usuario == 'advogado' and andamento.processo.advogado_responsavel != request.user:
        from django.http import Http404
        raise Http404("Andamento não encontrado ou você não tem permissão para visualizá-lo.")
    
    context = {
        'andamento': andamento,
    }
    
    return render(request, 'assejus/andamento_detail.html', context)


@login_required
def andamento_update(request, pk):
    """Editar andamento"""
    andamento = get_object_or_404(Andamento, pk=pk)
    
    # Verificar se o advogado tem permissão para editar este andamento
    if request.user.tipo_usuario == 'advogado' and andamento.processo.advogado_responsavel != request.user:
        from django.http import Http404
        raise Http404("Andamento não encontrado ou você não tem permissão para editá-lo.")
    
    if request.method == 'POST':
        form = AndamentoForm(request.POST, instance=andamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Andamento atualizado com sucesso!')
            return redirect('assejus:andamento_detail', pk=andamento.pk)
    else:
        form = AndamentoForm(instance=andamento)
    
    context = {
        'form': form,
        'andamento': andamento,
        'title': 'Editar Andamento',
        'action': 'Atualizar',
    }
    
    return render(request, 'assejus/andamento_form.html', context)


@login_required
def andamento_delete(request, pk):
    """Excluir andamento"""
    andamento = get_object_or_404(Andamento, pk=pk)
    
    # Verificar se o advogado tem permissão para excluir este andamento
    if request.user.tipo_usuario == 'advogado' and andamento.processo.advogado_responsavel != request.user:
        from django.http import Http404
        raise Http404("Andamento não encontrado ou você não tem permissão para excluí-lo.")
    
    if request.method == 'POST':
        andamento.delete()
        messages.success(request, 'Andamento excluído com sucesso!')
        return redirect('assejus:andamento_list')
    
    context = {
        'andamento': andamento,
    }
    
    return render(request, 'assejus/andamento_confirm_delete.html', context)


@login_required
def andamento_delete_ajax(request, pk):
    """
    Excluir andamento via AJAX
    """
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    try:
        andamento = get_object_or_404(Andamento, pk=pk)
        
        # Verificar se o advogado tem permissão para excluir este andamento
        if request.user.tipo_usuario == 'advogado' and andamento.processo.advogado_responsavel != request.user:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para excluir este andamento.'
            })
        
        # Armazenar informações para resposta
        tipo_andamento = andamento.get_tipo_andamento_display()
        processo_numero = andamento.processo.numero_processo
        data_andamento = andamento.data_andamento.strftime('%d/%m/%Y %H:%M')
        
        # Excluir andamento
        andamento.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Andamento "{tipo_andamento}" do processo {processo_numero} foi excluído com sucesso!',
            'andamento_info': {
                'tipo': tipo_andamento,
                'processo': processo_numero,
                'data': data_andamento
            }
        })
        
    except Andamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Andamento não encontrado'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@login_required
def andamento_pdf(request, pk):
    """
    Gerar PDF do andamento
    """
    andamento = get_object_or_404(Andamento, pk=pk)
    
    # Verificar se o usuário tem permissão para visualizar este andamento
    if request.user.tipo_usuario == 'advogado' and andamento.processo.advogado_responsavel != request.user:
        from django.http import Http404
        raise Http404("Andamento não encontrado ou você não tem permissão para visualizá-lo.")
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    filename = f"andamento_{andamento.processo.numero_processo}_{andamento.id}_{andamento.data_andamento.strftime('%Y%m%d')}.pdf"
    
    # Verificar se é para download ou visualização
    if request.GET.get('download') == '1':
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Criar documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    normal_style = styles['Normal']
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Título
    story.append(Paragraph(f"Andamento - {andamento.get_tipo_andamento_display()}", title_style))
    story.append(Spacer(1, 20))
    
    # Informações do processo
    story.append(Paragraph("Informações do Processo", heading_style))
    story.append(Paragraph(f"<b>Número do Processo:</b> {andamento.processo.numero_processo}", normal_style))
    story.append(Paragraph(f"<b>Vara/Tribunal:</b> {andamento.processo.vara_tribunal}", normal_style))
    story.append(Paragraph(f"<b>Tipo de Ação:</b> {andamento.processo.get_tipo_acao_display()}", normal_style))
    story.append(Paragraph(f"<b>Parte Cliente:</b> {andamento.processo.parte_cliente.nome}", normal_style))
    story.append(Paragraph(f"<b>Parte Contrária:</b> {andamento.processo.parte_contraria}", normal_style))
    story.append(Spacer(1, 20))
    
    # Informações do andamento
    story.append(Paragraph("Detalhes do Andamento", heading_style))
    story.append(Paragraph(f"<b>Tipo:</b> {andamento.get_tipo_andamento_display()}", normal_style))
    story.append(Paragraph(f"<b>Data:</b> {andamento.data_andamento.strftime('%d/%m/%Y às %H:%M')}", normal_style))
    story.append(Paragraph(f"<b>Registrado por:</b> {andamento.usuario_registro.get_full_name() or andamento.usuario_registro.username}", normal_style))
    story.append(Spacer(1, 20))
    
    # Descrição detalhada
    if andamento.descricao_detalhada:
        story.append(Paragraph("Descrição Detalhada", heading_style))
        # Quebrar texto longo em parágrafos
        descricao_paragrafos = andamento.descricao_detalhada.split('\n')
        for paragrafo in descricao_paragrafos:
            if paragrafo.strip():
                story.append(Paragraph(paragrafo.strip(), normal_style))
        story.append(Spacer(1, 20))
    
    # Observações para o cliente
    if andamento.observacoes_cliente:
        story.append(Paragraph("Observações para o Cliente", heading_style))
        story.append(Paragraph(andamento.observacoes_cliente, normal_style))
        story.append(Spacer(1, 20))
    
    # Informações adicionais
    story.append(Paragraph("Informações Adicionais", heading_style))
    story.append(Paragraph(f"<b>Data de Criação:</b> {andamento.data_andamento.strftime('%d/%m/%Y às %H:%M')}", normal_style))
    story.append(Paragraph(f"<b>Última Atualização:</b> {andamento.data_andamento.strftime('%d/%m/%Y às %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Rodapé
    story.append(Paragraph(f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
    
    # Construir PDF
    doc.build(story)
    
    return response


@login_required
def processo_andamentos_pdf(request, pk):
    """
    Gerar PDF com todos os andamentos do processo
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    
    processo = get_object_or_404(ProcessoJuridico, pk=pk)
    
    # Verificar se o usuário tem permissão para visualizar este processo
    if request.user.tipo_usuario == 'advogado' and processo.advogado_responsavel != request.user:
        from django.http import Http404
        raise Http404("Processo não encontrado ou você não tem permissão para visualizá-lo.")
    
    # Buscar todos os andamentos do processo ordenados por data
    andamentos = processo.andamentos.all().order_by('data_andamento')
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    filename = f"andamentos_processo_{processo.numero_processo}_{timezone.now().strftime('%Y%m%d')}.pdf"
    
    # Verificar se é para download ou visualização
    if request.GET.get('download') == '1':
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Criar documento PDF com margens mínimas no topo para logo
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=18, bottomMargin=100)  # Aumentar margem inferior para rodapé
    story = []
    
    # Definir cores institucionais
    cor_vermelho_sangue = colors.Color(0.8, 0.1, 0.1)  # Vermelho sangue
    cor_cinza_escuro = colors.Color(0.2, 0.2, 0.2)     # Cinza escuro
    cor_cinza_claro = colors.Color(0.9, 0.9, 0.9)      # Cinza claro
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo do cabeçalho institucional
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=cor_vermelho_sangue,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo do subtítulo do cabeçalho
    header_subtitle_style = ParagraphStyle(
        'HeaderSubtitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=cor_cinza_escuro,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Estilo do título do documento
    title_style = ParagraphStyle(
        'DocumentTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=cor_cinza_escuro,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo dos cabeçalhos de seção
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=cor_vermelho_sangue,
        spaceAfter=15,
        spaceBefore=20,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=cor_vermelho_sangue,
        borderPadding=5
    )
    
    # Estilo dos subtítulos
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=cor_cinza_escuro,
        spaceAfter=10,
        spaceBefore=15,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Estilo do texto normal
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=cor_cinza_escuro,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Estilo do rodapé
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # IMAGEM LOGO2 ASEJUR
    try:
        from reportlab.platypus import Image
        import os
        from django.conf import settings
        
        # Usar a função auxiliar para encontrar a logo
        logo_path = get_logo_path('logo2assejur.png')
        
        if logo_path:
            # Converter cm para inch (1 inch = 2.54 cm)
            width_cm = 8.61
            height_cm = 2.41
            width_inch = width_cm / 2.54
            height_inch = height_cm / 2.54
            logo = Image(logo_path, width=width_inch*inch, height=height_inch*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 20))
        else:
            # Se a logo não for encontrada, pula o cabeçalho
            story.append(Spacer(1, 30))
    except Exception as e:
        # Em caso de erro, pula o cabeçalho
        story.append(Spacer(1, 30))
    
    # Título discreto dos dados do processo
    story.append(Paragraph("Dados do Processo", ParagraphStyle(
        'ProcessTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=15,
        spaceBefore=0,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )))
    
    # Dados do processo em uma única tabela
    processo_data = [
        ['Número do Processo:', processo.numero_processo],
        ['Vara/Tribunal:', processo.vara_tribunal],
        ['Tipo de Ação:', processo.get_tipo_acao_display()],
        ['Situação Atual:', processo.get_situacao_atual_display()],
        ['Parte Cliente:', processo.parte_cliente.nome],
        ['Parte Contrária:', processo.parte_contraria],
        ['Advogado Responsável:', processo.advogado_responsavel.get_full_name() if processo.advogado_responsavel else 'Não informado'],
        ['Total de Andamentos:', str(andamentos.count())],
        ['Primeiro Andamento:', andamentos.first().data_andamento.strftime('%d/%m/%Y') if andamentos.exists() else 'N/A'],
        ['Último Andamento:', andamentos.last().data_andamento.strftime('%d/%m/%Y') if andamentos.exists() else 'N/A'],
    ]
    
    # Criar tabela única com dados do processo
    processo_table = Table(processo_data, colWidths=[2*inch, 4*inch])
    processo_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), cor_cinza_escuro),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(processo_table)
    story.append(Spacer(1, 25))
    
    # Tabela de andamentos
    if andamentos.exists():
        # Cabeçalho da tabela de andamentos
        andamentos_header = ['#', 'Data', 'Tipo', 'Descrição', 'Observações']
        
        # Dados dos andamentos
        andamentos_data = [andamentos_header]
        
        for i, andamento in enumerate(andamentos, 1):
            # Criar Paragraphs para permitir quebra de linha automática
            descricao_para = Paragraph(andamento.descricao_detalhada or "", normal_style) if andamento.descricao_detalhada else Paragraph("", normal_style)
            observacoes_para = Paragraph(andamento.observacoes_cliente or "", normal_style) if andamento.observacoes_cliente else Paragraph("", normal_style)
            
            andamentos_data.append([
                str(i),
                andamento.data_andamento.strftime('%d/%m/%Y'),
                andamento.get_tipo_andamento_display(),
                descricao_para,
                observacoes_para
            ])
        
        # Criar tabela de andamentos com larguras ajustadas para textos longos
        andamentos_table = Table(andamentos_data, colWidths=[0.3*inch, 0.7*inch, 0.8*inch, 2.5*inch, 2.7*inch])
        andamentos_table.setStyle(TableStyle([
            # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), cor_cinza_escuro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Dados
            ('TEXTCOLOR', (0, 1), (-1, -1), cor_cinza_escuro),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Coluna #
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Coluna Data
            ('ALIGN', (2, 1), (-1, -1), 'LEFT'),   # Demais colunas
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),   # Alinhamento vertical no topo
            
            # Bordas e espaçamento
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(andamentos_table)
    else:
        story.append(Paragraph("Nenhum andamento registrado para este processo.", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Função para criar rodapé
    def create_footer(canvas, doc):
        canvas.saveState()
        
        # Texto do rodapé
        footer_text = """
        Reconhecimento de Utilidade Pública Estadual Lei nº 5.614 28/11/06 |
        Reconhecimento de Utilidade Pública Municipal Lei nº 3.634 14/05/07 |
        Fone: 86 3085-1722 | E-mail: abmepi@gmail.com |
        Endereço: Rua Coelho Rodrigues, 2242, Centro Sul, CEP: 64.000-080, Teresina – PI
        """
        
        # Posicionar rodapé na parte inferior da página
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)  # Texto preto
        
        # Desenhar linha separadora por toda a página
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(0, 70, 612, 70)  # Linha horizontal por toda a página (A4 width = 612pt)
        
        # Adicionar logo da ABMEPI do lado esquerdo
        try:
            logo_path = get_logo_path('Logo_abmepi.png')
            if logo_path:
                canvas.drawImage(logo_path, 20, 20, width=40, height=40, preserveAspectRatio=True)
                
                # Adicionar dados de geração do documento abaixo da logo
                canvas.setFont('Helvetica', 6)
                canvas.setFillColor(colors.lightgrey)  # Cor cinza claro
                canvas.drawString(20, 10, f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}")
                canvas.drawString(20, 4, "ASEJUR - ABMEPI")
        except:
            pass  # Se não conseguir carregar a logo, continua sem ela
        
        # Dividir o texto em linhas
        lines = footer_text.strip().split('|')
        y_position = 50  # Subiu de 30 para 50
        
        # Garantir que o texto das informações institucionais seja preto
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)  # Texto preto
        
        for line in lines:
            line = line.strip()
            if line:
                # Todas as linhas alinhadas à direita
                canvas.drawRightString(580, y_position, line)
                y_position -= 10
        
        canvas.restoreState()
    
    # Construir PDF com rodapé em todas as páginas
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response


# Views para Consultas
@login_required
def consulta_list(request):
    """Lista de consultas jurídicas"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    tipo = request.GET.get('tipo', '')
    
    consultas = ConsultaJuridica.objects.all()
    
    if search:
        consultas = consultas.filter(
            Q(pergunta__icontains=search) |
            Q(associado__nome__icontains=search) |
            Q(resposta__icontains=search)
        )
    
    if status:
        consultas = consultas.filter(status=status)
    
    if tipo:
        consultas = consultas.filter(tipo=tipo)
    
    # Ordenação: primeiro por status (respondidas por último), depois por data de consulta
    consultas = consultas.order_by(
        Case(
            When(status='respondida', then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
        '-data_consulta'
    )
    
    # Estatísticas para o contexto
    total_consultas = consultas.count()
    consultas_pendentes = consultas.exclude(status='respondida').count()
    consultas_respondidas = consultas.filter(status='respondida').count()
    
    # Verifica se há transição entre pendentes e respondidas
    tem_transicao = consultas_pendentes > 0 and consultas_respondidas > 0
    
    # Paginação
    paginator = Paginator(consultas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'tipo': tipo,
        'total_consultas': total_consultas,
        'consultas_pendentes': consultas_pendentes,
        'consultas_respondidas': consultas_respondidas,
        'tem_transicao': tem_transicao,
    }
    
    return render(request, 'assejus/consulta_list.html', context)


@login_required
def consulta_create(request):
    """Criar nova consulta jurídica"""
    if request.method == 'POST':
        form = ConsultaJuridicaForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            messages.success(request, 'Consulta criada com sucesso!')
            return redirect('assejus:consulta_detail', pk=consulta.pk)
    else:
        form = ConsultaJuridicaForm()
    
    context = {
        'form': form,
        'title': 'Nova Consulta Jurídica',
        'action': 'Criar',
    }
    
    return render(request, 'assejus/consulta_form.html', context)


@login_required
def consulta_enviar_advogado(request, pk):
    """Enviar consulta para advogado"""
    consulta = get_object_or_404(ConsultaJuridica, pk=pk)
    
    if request.method == 'POST':
        advogado_id = request.POST.get('advogado_responsavel')
        if advogado_id:
            try:
                advogado = Advogado.objects.get(pk=advogado_id, ativo=True)
                consulta.advogado_responsavel = advogado
                consulta.status = 'em_analise'
                consulta.save()
                messages.success(request, f'Consulta enviada para o advogado {advogado.nome} com sucesso!')
            except Advogado.DoesNotExist:
                messages.error(request, 'Advogado não encontrado ou inativo.')
        else:
            messages.error(request, 'Por favor, selecione um advogado.')
        
        return redirect('assejus:consulta_detail', pk=consulta.pk)
    
    # Busca advogados ativos
    advogados = Advogado.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'consulta': consulta,
        'advogados': advogados,
        'title': 'Enviar Consulta para Advogado',
    }
    
    return render(request, 'assejus/consulta_enviar_advogado.html', context)


@login_required
def consulta_detail(request, pk):
    """Detalhes da consulta jurídica"""
    consulta = get_object_or_404(ConsultaJuridica, pk=pk)
    
    context = {
        'consulta': consulta,
    }
    
    return render(request, 'assejus/consulta_detail.html', context)


@login_required
def consulta_update(request, pk):
    """Editar consulta jurídica"""
    consulta = get_object_or_404(ConsultaJuridica, pk=pk)
    
    if request.method == 'POST':
        form = ConsultaJuridicaForm(request.POST, instance=consulta)
        if form.is_valid():
            consulta = form.save(commit=False)
            if form.cleaned_data.get('resposta'):
                consulta.status = 'respondida'
                consulta.resolvida = True
                consulta.data_resposta = timezone.now()
                consulta.usuario_resposta = request.user
            consulta.save()
            messages.success(request, 'Consulta atualizada com sucesso!')
            return redirect('assejus:consulta_detail', pk=consulta.pk)
    else:
        form = ConsultaJuridicaForm(instance=consulta)
    
    context = {
        'form': form,
        'consulta': consulta,
        'title': 'Editar Consulta Jurídica',
        'action': 'Atualizar',
    }
    
    return render(request, 'assejus/consulta_form.html', context)


@login_required
def consulta_delete(request, pk):
    """Excluir consulta jurídica"""
    consulta = get_object_or_404(ConsultaJuridica, pk=pk)
    
    if request.method == 'POST':
        consulta.delete()
        messages.success(request, 'Consulta excluída com sucesso!')
        return redirect('assejus:consulta_list')
    
    context = {
        'consulta': consulta,
    }
    
    return render(request, 'assejus/consulta_confirm_delete.html', context)


# Views para Relatórios
@login_required
def relatorio_list(request):
    """Lista de relatórios jurídicos"""
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    escopo = request.GET.get('escopo', '')
    
    relatorios = RelatorioJuridico.objects.all()
    
    if search:
        relatorios = relatorios.filter(
            Q(tipo__icontains=search) |
            Q(advogado__nome__icontains=search)
        )
    
    if tipo:
        relatorios = relatorios.filter(tipo=tipo)
    
    if escopo:
        relatorios = relatorios.filter(escopo=escopo)
    
    relatorios = relatorios.order_by('-data_geracao')
    
    # Paginação
    paginator = Paginator(relatorios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'tipo': tipo,
        'escopo': escopo,
    }
    
    return render(request, 'assejus/relatorio_list.html', context)


@login_required
def relatorio_create(request):
    """Criar novo relatório jurídico"""
    if request.method == 'POST':
        form = RelatorioJuridicoForm(request.POST)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.usuario_geracao = request.user
            
            # Validação adicional para o escopo
            if relatorio.escopo == 'por_advogado' and not relatorio.advogado:
                form.add_error('advogado', 'É obrigatório selecionar um advogado quando o escopo for "Por Advogado Específico".')
                context = {
                    'form': form,
                    'title': 'Novo Relatório Jurídico',
                    'action': 'Criar',
                }
                return render(request, 'assejus/relatorio_form.html', context)
            
            relatorio.save()
            messages.success(request, 'Relatório criado com sucesso!')
            return redirect('assejus:relatorio_detail', pk=relatorio.pk)
    else:
        form = RelatorioJuridicoForm()
    
    context = {
        'form': form,
        'title': 'Novo Relatório Jurídico',
        'action': 'Criar',
    }
    
    return render(request, 'assejus/relatorio_form.html', context)


@login_required
def relatorio_detail(request, pk):
    """Detalhes do relatório jurídico"""
    relatorio = get_object_or_404(RelatorioJuridico, pk=pk)
    
    # Estatísticas baseadas no escopo do relatório
    from django.db.models import Count, Q
    
    # Filtros por período, distintos para cada modelo
    periodo_filter_atend = Q(
        data_abertura__gte=relatorio.periodo_inicio,
        data_abertura__lte=relatorio.periodo_fim
    )
    periodo_filter_cons = Q(
        data_consulta__gte=relatorio.periodo_inicio,
        data_consulta__lte=relatorio.periodo_fim
    )
    
    if relatorio.escopo == 'por_advogado' and relatorio.advogado:
        # Relatório por advogado específico
        atendimentos = AtendimentoJuridico.objects.filter(
            periodo_filter_atend,
            advogado_responsavel=relatorio.advogado
        )
        consultas = ConsultaJuridica.objects.filter(
            periodo_filter_cons,
            advogado_responsavel=relatorio.advogado
        )
        escopo_info = f"Relatório específico para o advogado {relatorio.advogado.nome}"
    else:
        # Relatório total geral
        atendimentos = AtendimentoJuridico.objects.filter(periodo_filter_atend)
        consultas = ConsultaJuridica.objects.filter(periodo_filter_cons)
        escopo_info = "Relatório geral de todos os advogados"
    
    # Estatísticas
    total_atendimentos = atendimentos.count()
    atendimentos_por_status = atendimentos.values('status').annotate(total=Count('id'))
    atendimentos_por_tipo = atendimentos.values('tipo_demanda').annotate(total=Count('id'))
    
    total_consultas = consultas.count()
    consultas_por_status = consultas.values('status').annotate(total=Count('id'))
    
    context = {
        'relatorio': relatorio,
        'escopo_info': escopo_info,
        'total_atendimentos': total_atendimentos,
        'atendimentos_por_status': atendimentos_por_status,
        'atendimentos_por_tipo': atendimentos_por_tipo,
        'total_consultas': total_consultas,
        'consultas_por_status': consultas_por_status,
        'periodo_inicio': relatorio.periodo_inicio,
        'periodo_fim': relatorio.periodo_fim,
    }
    
    return render(request, 'assejus/relatorio_detail.html', context)


@login_required
def relatorio_update(request, pk):
    """Editar relatório jurídico"""
    relatorio = get_object_or_404(RelatorioJuridico, pk=pk)
    
    if request.method == 'POST':
        form = RelatorioJuridicoForm(request.POST, instance=relatorio)
        if form.is_valid():
            relatorio_temp = form.save(commit=False)
            
            # Validação adicional para o escopo
            if relatorio_temp.escopo == 'por_advogado' and not relatorio_temp.advogado:
                form.add_error('advogado', 'É obrigatório selecionar um advogado quando o escopo for "Por Advogado Específico".')
                context = {
                    'form': form,
                    'relatorio': relatorio,
                    'title': 'Editar Relatório Jurídico',
                    'action': 'Atualizar',
                }
                return render(request, 'assejus/relatorio_form.html', context)
            
            form.save()
            messages.success(request, 'Relatório atualizado com sucesso!')
            return redirect('assejus:relatorio_detail', pk=relatorio.pk)
    else:
        form = RelatorioJuridicoForm(instance=relatorio)
    
    context = {
        'form': form,
        'relatorio': relatorio,
        'title': 'Editar Relatório Jurídico',
        'action': 'Atualizar',
    }
    
    return render(request, 'assejus/relatorio_form.html', context)


@login_required
def relatorio_delete(request, pk):
    """Excluir relatório jurídico"""
    relatorio = get_object_or_404(RelatorioJuridico, pk=pk)
    
    if request.method == 'POST':
        relatorio.delete()
        messages.success(request, 'Relatório excluído com sucesso!')
        return redirect('assejus:relatorio_list')
    
    context = {
        'relatorio': relatorio,
    }
    
    return render(request, 'assejus/relatorio_confirm_delete.html', context)


@login_required
def relatorio_pdf(request, pk):
    """Gerar relatório em PDF"""
    relatorio = get_object_or_404(RelatorioJuridico, pk=pk)
    
    # Estatísticas baseadas no escopo do relatório
    from django.db.models import Count, Q
    
    # Filtros por período, distintos para cada modelo
    periodo_filter_atend = Q(
        data_abertura__gte=relatorio.periodo_inicio,
        data_abertura__lte=relatorio.periodo_fim
    )
    periodo_filter_cons = Q(
        data_consulta__gte=relatorio.periodo_inicio,
        data_consulta__lte=relatorio.periodo_fim
    )
    
    if relatorio.escopo == 'por_advogado' and relatorio.advogado:
        # Relatório por advogado específico
        atendimentos = AtendimentoJuridico.objects.filter(
            periodo_filter_atend,
            advogado_responsavel=relatorio.advogado
        )
        consultas = ConsultaJuridica.objects.filter(
            periodo_filter_cons,
            advogado_responsavel=relatorio.advogado
        )
        escopo_info = f"Relatório específico para o advogado {relatorio.advogado.nome}"
    else:
        # Relatório total geral
        atendimentos = AtendimentoJuridico.objects.filter(periodo_filter_atend)
        consultas = ConsultaJuridica.objects.filter(periodo_filter_cons)
        escopo_info = "Relatório geral de todos os advogados"
    
    # Estatísticas
    total_atendimentos = atendimentos.count()
    atendimentos_por_status = atendimentos.values('status').annotate(total=Count('id'))
    atendimentos_por_tipo = atendimentos.values('tipo_demanda').annotate(total=Count('id'))
    
    total_consultas = consultas.count()
    consultas_por_status = consultas.values('status').annotate(total=Count('id'))
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo baseado no escopo
    if relatorio.escopo == 'por_advogado' and relatorio.advogado:
        filename = f"relatorio_{relatorio.tipo}_{relatorio.advogado.nome}_{relatorio.periodo_inicio}_{relatorio.periodo_fim}.pdf"
    else:
        filename = f"relatorio_{relatorio.tipo}_{relatorio.periodo_inicio}_{relatorio.periodo_fim}.pdf"
    
    # Verificar se é para download ou visualização
    if request.GET.get('download') == '1':
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Criar documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    normal_style = styles['Normal']
    
    # Título
    if relatorio.escopo == 'por_advogado' and relatorio.advogado:
        story.append(Paragraph(f"Relatório {relatorio.get_tipo_display()} - {relatorio.advogado.nome}", title_style))
    else:
        story.append(Paragraph(f"Relatório {relatorio.get_tipo_display()}", title_style))
    story.append(Spacer(1, 20))
    
    # Informações do relatório
    story.append(Paragraph("Informações do Relatório", heading_style))
    story.append(Paragraph(f"<b>Escopo:</b> {escopo_info}", normal_style))
    story.append(Paragraph(f"<b>Período:</b> {relatorio.periodo_inicio.strftime('%d/%m/%Y')} a {relatorio.periodo_fim.strftime('%d/%m/%Y')}", normal_style))
    story.append(Paragraph(f"<b>Data de Geração:</b> {relatorio.data_geracao.strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Paragraph(f"<b>Usuário:</b> {relatorio.usuario_geracao.username if relatorio.usuario_geracao else 'Não informado'}", normal_style))
    story.append(Spacer(1, 20))
    
    # Estatísticas de Atendimentos
    story.append(Paragraph("Estatísticas de Atendimentos", heading_style))
    story.append(Paragraph(f"<b>Total de Atendimentos:</b> {total_atendimentos}", normal_style))
    
    if atendimentos_por_status:
        story.append(Paragraph("Atendimentos por Status:", normal_style))
        status_data = [['Status', 'Quantidade']]
        for item in atendimentos_por_status:
            status_data.append([item['status'], str(item['total'])])
        
        status_table = Table(status_data)
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(status_table)
    
    story.append(Spacer(1, 20))
    
    # Estatísticas de Consultas
    story.append(Paragraph("Estatísticas de Consultas", heading_style))
    story.append(Paragraph(f"<b>Total de Consultas:</b> {total_consultas}", normal_style))
    
    if consultas_por_status:
        story.append(Paragraph("Consultas por Status:", normal_style))
        consulta_data = [['Status', 'Quantidade']]
        for item in consultas_por_status:
            consulta_data.append([item['status'], str(item['total'])])
        
        consulta_table = Table(consulta_data)
        consulta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(consulta_table)
    
    # Gerar PDF
    doc.build(story)
    return response


@login_required
def stats(request):
    """API para retornar estatísticas em formato JSON"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Estatísticas básicas
        total_advogados = Advogado.objects.filter(ativo=True).count()
        total_atendimentos = AtendimentoJuridico.objects.count()
        atendimentos_em_andamento = AtendimentoJuridico.objects.filter(status='em_andamento').count()
        consultas_pendentes = ConsultaJuridica.objects.exclude(status='respondida').count()
        
        data = {
            'total_advogados': total_advogados,
            'total_atendimentos': total_atendimentos,
            'atendimentos_em_andamento': atendimentos_em_andamento,
            'consultas_pendentes': consultas_pendentes,
        }
        
        return JsonResponse(data)
    
    # Se não for uma requisição AJAX, retornar erro 400
    return JsonResponse({'error': 'Requisição inválida'}, status=400)


# ============================================================================
# VIEWS PARA MODAIS
# ============================================================================

from django.template.loader import render_to_string

# Views de teste removidas - não são mais necessárias
# def advogado_modal_test(request): ...
# def advogado_modal_create_simple(request): ...
# def advogado_modal_create_minimal(request): ...

def advogado_modal_create(request):
    """View para criar advogado via modal"""
    
    # Verificação manual de autenticação
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Usuário não autenticado',
            'redirect': '/login/'
        }, status=401)
    
    if request.method == 'POST':
        form = AdvogadoForm(request.POST, request.FILES)
        if form.is_valid():
            advogado = form.save()
            
            # Verificar se o usuário foi criado automaticamente
            if advogado.user:
                # Retornar informações de login
                return JsonResponse({
                    'success': True,
                    'message': f'Advogado {advogado.nome} criado com sucesso!',
                    'reload': True,
                    'id': advogado.id,
                    'login_info': {
                        'username': advogado.user.username,
                        'senha_padrao': '12345678',
                        'tipo_usuario': advogado.user.tipo_usuario
                    }
                })
            else:
                # Usuário não foi criado automaticamente
                return JsonResponse({
                    'success': True,
                    'message': f'Advogado {advogado.nome} criado com sucesso! (Usuário não criado automaticamente)',
                    'reload': True,
                    'id': advogado.id
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AdvogadoForm()
    
    # Usar render_to_string para obter o HTML como string
    form_html = render_to_string('assejus/forms/advogado_form_modal.html', {
        'form': form,
        'title': 'Novo Advogado'
    }, request=request)
    
    return JsonResponse({
        'success': True,
        'form_html': form_html
    })


@login_required
def advogado_modal_update(request, pk):
    """View para editar advogado via modal"""
    advogado = get_object_or_404(Advogado, pk=pk)
    
    if request.method == 'POST':
        form = AdvogadoForm(request.POST, request.FILES, instance=advogado)
        if form.is_valid():
            advogado = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Advogado {advogado.nome} atualizado com sucesso!',
                'reload': True,
                'id': advogado.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AdvogadoForm(instance=advogado)
    
    # Usar render_to_string para obter o HTML como string
    form_html = render_to_string('assejus/forms/advogado_form_modal.html', {
        'form': form,
        'title': 'Editar Advogado'
    }, request=request)
    
    return JsonResponse({
        'success': True,
        'form_html': form_html
    })


@login_required
def atendimento_modal_create(request):
    """View para criar atendimento via modal"""
    if request.method == 'POST':
        form = AtendimentoJuridicoForm(request.POST)
        if form.is_valid():
            atendimento = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Atendimento {atendimento.titulo} criado com sucesso!',
                'reload': True,
                'id': atendimento.id,
                'titulo': atendimento.titulo
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AtendimentoJuridicoForm()
    
    # Usar render_to_string para obter o HTML como string
    form_html = render_to_string('assejus/forms/atendimento_form_modal.html', {
        'form': form,
        'title': 'Novo Atendimento'
    }, request=request)
    return JsonResponse({'form_html': form_html})


@login_required
def atendimento_modal_update(request, pk):
    """View para editar atendimento via modal"""
    atendimento = get_object_or_404(AtendimentoJuridico, pk=pk)
    
    if request.method == 'POST':
        form = AtendimentoJuridicoForm(request.POST, instance=atendimento)
        if form.is_valid():
            atendimento = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Atendimento {atendimento.titulo} atualizado com sucesso!',
                'reload': True,
                'id': atendimento.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = AtendimentoJuridicoForm(instance=atendimento)
    
    # Usar render_to_string para obter o HTML como string
    form_html = render_to_string('assejus/forms/atendimento_form_modal.html', {
        'form': form,
        'title': 'Editar Atendimento'
    }, request=request)
    return JsonResponse({'form_html': form_html})








# ===== VIEWS PARA GESTÃO DE PROCESSOS JURÍDICOS =====

@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def processos_list(request):
    """Lista todos os processos jurídicos"""
    # Filtro baseado no tipo de usuário
    if request.user.tipo_usuario == 'advogado':
        # Advogados só veem processos onde são responsáveis
        processos = ProcessoJuridico.objects.filter(advogado_responsavel=request.user).order_by('-data_atualizacao')
    else:
        # Administradores e atendentes veem todos os processos
        processos = ProcessoJuridico.objects.all().order_by('-data_atualizacao')
    
    # Filtros
    search = request.GET.get('search')
    situacao = request.GET.get('situacao')
    tipo_acao = request.GET.get('tipo_acao')
    advogado = request.GET.get('advogado')
    
    if search:
        processos = processos.filter(
            Q(numero_processo__icontains=search) |
            Q(parte_cliente__nome__icontains=search) |
            Q(parte_contraria__icontains=search) |
            Q(vara_tribunal__icontains=search)
        )
    if situacao:
        processos = processos.filter(situacao_atual=situacao)
    if tipo_acao:
        processos = processos.filter(tipo_acao=tipo_acao)
    if advogado:
        processos = processos.filter(advogado_responsavel_id=advogado)
    
    # Estatísticas para o dashboard (também filtradas por permissão)
    if request.user.tipo_usuario == 'advogado':
        base_queryset = ProcessoJuridico.objects.filter(advogado_responsavel=request.user)
    else:
        base_queryset = ProcessoJuridico.objects.all()
    
    stats = {
        'total_processos': base_queryset.count(),
        'processos_andamento': base_queryset.filter(situacao_atual='andamento').count(),
        'processos_suspensos': base_queryset.filter(situacao_atual='suspenso').count(),
        'processos_arquivados': base_queryset.filter(situacao_atual='arquivado').count(),
        'processos_concluidos': base_queryset.filter(situacao_atual='concluido').count(),
    }
    
    context = {
        'processos': processos,
        'stats': stats,
        'situacao_choices': ProcessoJuridico.SITUACAO_CHOICES,
        'tipo_acao_choices': ProcessoJuridico.TIPO_ACAO_CHOICES,
        'advogados': User.objects.filter(tipo_usuario='advogado').order_by('first_name'),
    }
    
    return render(request, 'assejus/processos_list.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def processo_detail(request, pk):
    """Detalhes de um processo específico com timeline de andamentos"""
    processo = get_object_or_404(ProcessoJuridico, pk=pk)
    
    # Verificar se o advogado tem permissão para ver este processo
    if request.user.tipo_usuario == 'advogado':
        # Verificar se o processo tem advogado responsável
        if not processo.advogado_responsavel:
            from django.http import Http404
            raise Http404("Processo não tem advogado responsável definido. Contate um administrador.")
        
        # Verificar se o usuário é o advogado responsável
        if processo.advogado_responsavel != request.user:
            from django.http import Http404
            raise Http404("Processo não encontrado ou você não tem permissão para visualizá-lo.")
    andamentos = processo.andamentos.all().order_by('-data_andamento')
    documentos = processo.documentos.all().order_by('-data_upload')
    
    # Filtros para andamentos
    tipo_andamento = request.GET.get('tipo_andamento')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if tipo_andamento:
        andamentos = andamentos.filter(tipo_andamento=tipo_andamento)
    if data_inicio:
        andamentos = andamentos.filter(data_andamento__date__gte=data_inicio)
    if data_fim:
        andamentos = andamentos.filter(data_andamento__date__lte=data_fim)
    
    context = {
        'processo': processo,
        'andamentos': andamentos,
        'documentos': documentos,
        'tipo_andamento_choices': Andamento.TIPO_ANDAMENTO_CHOICES,
    }
    
    return render(request, 'assejus/processo_detail.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def processo_create(request):
    """Criar novo processo jurídico"""
    if request.method == 'POST':
        form = ProcessoJuridicoForm(request.POST)
        if form.is_valid():
            processo = form.save()
            messages.success(request, f'Processo {processo.numero_processo} criado com sucesso!')
            return redirect('assejus:processo_detail', pk=processo.pk)
    else:
        form = ProcessoJuridicoForm()
    
    return render(request, 'assejus/processo_form.html', {'form': form, 'title': 'Novo Processo'})


# Views para Procuração Ad Judicia
@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_list(request):
    """Lista todas as procurações"""
    procuracaoes = ProcuracaoAdJudicia.objects.all().order_by('-data_criacao')
    
    context = {
        'procuracaoes': procuracaoes,
        'title': 'Procurações Ad Judicia'
    }
    
    return render(request, 'assejus/procuracao_list.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_create(request):
    """Criar nova procuração"""
    if request.method == 'POST':
        form = ProcuracaoAdJudiciaForm(request.POST)
        if form.is_valid():
            procuracao = form.save(commit=False)
            procuracao.usuario_criacao = request.user
            procuracao.save()
            form.save_m2m()  # Salvar relacionamentos many-to-many
            messages.success(request, 'Procuração criada com sucesso!')
            return redirect('assejus:procuracao_detail', pk=procuracao.pk)
    else:
        form = ProcuracaoAdJudiciaForm()
    
    context = {
        'form': form,
        'title': 'Nova Procuração Ad Judicia'
    }
    
    return render(request, 'assejus/procuracao_form.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_detail(request, pk):
    """Detalhes da procuração"""
    procuracao = get_object_or_404(ProcuracaoAdJudicia, pk=pk)
    
    context = {
        'procuracao': procuracao,
        'title': f'Procuração - {procuracao.outorgante.nome}'
    }
    
    return render(request, 'assejus/procuracao_detail.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_edit(request, pk):
    """Editar procuração"""
    procuracao = get_object_or_404(ProcuracaoAdJudicia, pk=pk)
    
    if request.method == 'POST':
        form = ProcuracaoAdJudiciaForm(request.POST, instance=procuracao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Procuração atualizada com sucesso!')
            return redirect('assejus:procuracao_detail', pk=procuracao.pk)
    else:
        form = ProcuracaoAdJudiciaForm(instance=procuracao)
    
    context = {
        'form': form,
        'procuracao': procuracao,
        'title': f'Editar Procuração - {procuracao.outorgante.nome}'
    }
    
    return render(request, 'assejus/procuracao_form.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_delete(request, pk):
    """Excluir procuração"""
    procuracao = get_object_or_404(ProcuracaoAdJudicia, pk=pk)
    
    if request.method == 'POST':
        outorgante_nome = procuracao.outorgante.nome
        procuracao.delete()
        messages.success(request, f'Procuração de {outorgante_nome} excluída com sucesso!')
        return redirect('assejus:procuracao_list')
    
    context = {
        'procuracao': procuracao,
        'title': f'Excluir Procuração - {procuracao.outorgante.nome}'
    }
    
    return render(request, 'assejus/procuracao_confirm_delete.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_print(request, pk):
    """Imprimir procuração"""
    from datetime import datetime
    
    procuracao = get_object_or_404(ProcuracaoAdJudicia, pk=pk)
    
    # Data em português (igual ao PDF)
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    data_atual = datetime.now()
    data_pt = f"{data_atual.day} de {meses_pt[data_atual.month]} de {data_atual.year}"
    
    context = {
        'procuracao': procuracao,
        'texto_procuracao': procuracao.get_texto_procuracao(),
        'data_pt': data_pt,
        'title': f'Procuração - {procuracao.outorgante.nome}'
    }
    
    return render(request, 'assejus/procuracao_print.html', context)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def get_associado_data(request, associado_id):
    """Buscar dados do associado via AJAX"""
    try:
        from associados.models import Associado
        associado = Associado.objects.get(pk=associado_id)
        
        # Montar endereço completo
        endereco_completo = f"{associado.rua}, {associado.numero}"
        if associado.complemento:
            endereco_completo += f", {associado.complemento}"
        endereco_completo += f", {associado.bairro}, {associado.cidade} - {associado.estado}, CEP: {associado.cep}"
        
        # Mapear dados militares baseados nos campos disponíveis no modelo Associado
        cargo_militar = associado.get_posto_graduacao_display() if associado.posto_graduacao else ''
        matricula_funcional = associado.matricula_militar or ''
        rgpmpi = associado.tipo_documento.upper() + ': ' + (associado.rg or '') if associado.tipo_documento and associado.rg else ''
        
        data = {
            'nome': associado.nome,
            'cpf': associado.cpf,
            'cargo_militar': cargo_militar,
            'matricula_funcional': matricula_funcional,
            'rgpmpi': rgpmpi,
            'endereco_completo': endereco_completo,
            'telefone': associado.telefone or associado.celular or '',
            'email': associado.email or '',
            'naturalidade': associado.naturalidade or '',
            'nacionalidade': associado.nacionalidade or '',
            'tipo_profissional': associado.get_tipo_profissional_display() or '',
            'unidade_lotacao': getattr(associado, 'unidade_lotacao', '') or '',
        }
        
        return JsonResponse(data)
    except Associado.DoesNotExist:
        return JsonResponse({'error': 'Associado não encontrado'}, status=404)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def get_advogado_data(request, advogado_id):
    """Buscar dados do advogado via AJAX"""
    try:
        advogado = Advogado.objects.get(pk=advogado_id)
        
        # Montar endereço completo
        endereco_completo = f"{advogado.endereco}, {advogado.cidade} - {advogado.estado}, CEP: {advogado.cep}"
        
        data = {
            'nome': advogado.nome,
            'cpf': advogado.cpf,
            'oab': advogado.oab,
            'uf_oab': advogado.uf_oab,
            'oab_completa': f"{advogado.oab}/{advogado.uf_oab}",
            'endereco_completo': endereco_completo,
            'telefone': advogado.telefone,
            'celular': advogado.celular or '',
            'email': advogado.email,
            'especialidades': advogado.especialidades or '',
            'situacao': advogado.get_situacao_display(),
        }
        
        return JsonResponse(data)
    except Advogado.DoesNotExist:
        return JsonResponse({'error': 'Advogado não encontrado'}, status=404)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def procuracao_pdf(request, pk):
    """Gerar PDF da procuração com cabeçalho institucional e rodapé"""
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    from django.utils import timezone
    import os
    
    procuracao = get_object_or_404(ProcuracaoAdJudicia, pk=pk)
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="procuracao_{procuracao.outorgante.nome.replace(" ", "_")}_{procuracao.pk}.pdf"'
    
    # Criar documento com margem superior de 1cm (28.35 pontos)
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=28.35, bottomMargin=72)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Função para obter logo
    def get_logo_path(filename):
        from django.conf import settings
        logo_path = os.path.join(settings.BASE_DIR, 'static', filename)
        if os.path.exists(logo_path):
            return logo_path
        logo_path = os.path.join(settings.STATIC_ROOT, filename)
        if os.path.exists(logo_path):
            return logo_path
        return None
    
    # Função para criar rodapé
    def create_footer(canvas, doc):
        canvas.saveState()
        
        # Texto do rodapé
        footer_text = """
        Reconhecimento de Utilidade Pública Estadual Lei nº 5.614 28/11/06 |
        Reconhecimento de Utilidade Pública Municipal Lei nº 3.634 14/05/07 |
        Fone: 86 3085-1722 | E-mail: abmepi@gmail.com |
        Endereço: Rua Coelho Rodrigues, 2242, Centro Sul, CEP: 64.000-080, Teresina – PI
        """
        
        # Posicionar rodapé na parte inferior da página
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)
        
        # Desenhar linha separadora
        canvas.setLineWidth(0.5)
        canvas.line(0, 70, 612, 70)
        
        # Adicionar logo da ABMEPI
        try:
            logo_path = get_logo_path('Logo_abmepi.png')
            if logo_path:
                canvas.drawImage(logo_path, 20, 20, width=40, height=40, preserveAspectRatio=True)
                
                # Adicionar dados de geração do documento
                canvas.setFont('Helvetica', 6)
                canvas.setFillColor(colors.black)
                canvas.drawString(20, 10, f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}")
                canvas.drawString(20, 4, "ABMEPI")
        except:
            pass
        
        # Dividir o texto em linhas
        lines = footer_text.strip().split('|')
        y_position = 50
        
        # Garantir que o texto das informações institucionais seja preto
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)
        
        for line in lines:
            line = line.strip()
            if line:
                canvas.drawRightString(580, y_position, line)
                y_position -= 10
        
        canvas.restoreState()
    
    # Adicionar logo2assejur.png no topo com proporção 8,66 por 2,41
    try:
        logo_asejur2_path = get_logo_path('logo2assejur.png')
        
        if logo_asejur2_path:
            # Proporção 8,66:2,41 = aproximadamente 3,59:1
            # Usando largura de 200px, altura será aproximadamente 56px
            logo = Image(logo_asejur2_path, width=200, height=56)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 28.35))  # 1cm de espaçamento
    except Exception as e:
        pass
    
    # Título do documento
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=15,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("<b>P R O C U R A Ç Ã O   A D   J U D I C I A   E T   E X T R A</b>", title_style))
    story.append(Spacer(1, 20))
    
    # Texto da procuração
    texto_style = ParagraphStyle(
        'TextoStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=4,
        spaceBefore=0,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman',
        leading=14
    )
    
    # Obter texto da procuração
    texto_procuracao = procuracao.get_texto_procuracao()
    
    # Dividir o texto em parágrafos e adicionar
    paragrafos = texto_procuracao.split('\n\n')
    for i, paragrafo in enumerate(paragrafos):
        if paragrafo.strip():
            story.append(Paragraph(paragrafo.strip(), texto_style))
            # Reduzir espaçamento entre parágrafos
            if i < len(paragrafos) - 1:
                story.append(Spacer(1, 8))
    
    # Adicionar data em português e nome do outorgante centralizados
    story.append(Spacer(1, 20))
    
    # Data em português
    from datetime import datetime
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    data_atual = datetime.now()
    data_pt = f"{data_atual.day} de {meses_pt[data_atual.month]} de {data_atual.year}"
    
    # Estilo para data e assinatura
    assinatura_style = ParagraphStyle(
        'AssinaturaStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Adicionar data e nome do outorgante centralizados
    story.append(Paragraph(f"{procuracao.outorgante.cidade or 'Teresina'} ({procuracao.outorgante.estado or 'PI'}), {data_pt}.", assinatura_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>{procuracao.outorgante.nome}</b>", assinatura_style))
    
    # Construir PDF com rodapé em todas as páginas
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def processo_edit(request, pk):
    """Editar processo jurídico"""
    processo = get_object_or_404(ProcessoJuridico, pk=pk)
    
    if request.method == 'POST':
        form = ProcessoJuridicoForm(request.POST, instance=processo)
        if form.is_valid():
            processo = form.save()
            messages.success(request, f'Processo {processo.numero_processo} atualizado com sucesso!')
            return redirect('assejus:processo_detail', pk=processo.pk)
    else:
        form = ProcessoJuridicoForm(instance=processo)
    
    return render(request, 'assejus/processo_form.html', {'form': form, 'title': 'Editar Processo'})


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def andamento_modal_create(request):
    """View para criar andamento via modal"""
    if request.method == 'POST':
        form = AndamentoForm(request.POST)
        if form.is_valid():
            andamento = form.save(commit=False)
            andamento.usuario_registro = request.user
            andamento.save()
            form.save_m2m()
            
            return JsonResponse({
                'success': True,
                'message': f'Andamento criado com sucesso!',
                'reload': True,
                'id': andamento.id,
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    # Verificar se há um processo específico na URL
    processo_id = request.GET.get('processo')
    initial_data = {}
    
    if processo_id:
        try:
            processo = ProcessoJuridico.objects.get(pk=processo_id)
            initial_data['processo'] = processo
        except ProcessoJuridico.DoesNotExist:
            pass
    
    form = AndamentoForm(initial=initial_data)
    
    # Buscar processos ativos para o contexto
    processos = ProcessoJuridico.objects.filter(
        situacao_atual__in=['andamento', 'suspenso']
    ).order_by('-data_atualizacao')
    
    # Atualizar o queryset do campo processo
    form.fields['processo'].queryset = processos
    
    form_html = render_to_string('assejus/forms/andamento_form_modal.html', {
        'form': form,
        'processos': processos
    }, request=request)
    return JsonResponse({'form_html': form_html})


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def andamento_modal_update(request, pk):
    """View para editar andamento via modal"""
    try:
        andamento = get_object_or_404(Andamento, pk=pk)
        
        if request.method == 'POST':
            form = AndamentoForm(request.POST, instance=andamento)
            if form.is_valid():
                andamento = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Andamento {andamento.titulo} atualizado com sucesso!',
                    'reload': True,
                    'id': andamento.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro na validação do formulário.',
                    'errors': form.errors
                })
        
        form = AndamentoForm(instance=andamento)
        form_html = render_to_string('assejus/forms/andamento_form_modal.html', {'form': form}, request=request)
        return JsonResponse({'form_html': form_html})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def consulta_modal_create(request):
    """View para criar consulta via modal"""
    if request.method == 'POST':
        form = ConsultaJuridicaForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Consulta jurídica criada com sucesso!',
                'reload': True,
                'id': consulta.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = ConsultaJuridicaForm()
    form_html = render_to_string('assejus/forms/consulta_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'form_html': form_html})


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def consulta_modal_update(request, pk):
    """View para editar consulta via modal"""
    try:
        consulta = get_object_or_404(ConsultaJuridica, pk=pk)
        
        if request.method == 'POST':
            form = ConsultaJuridicaForm(request.POST, instance=consulta)
            if form.is_valid():
                consulta = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Consulta jurídica atualizada com sucesso!',
                    'reload': True,
                    'id': consulta.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro na validação do formulário.',
                    'errors': form.errors
                })
        
        form = ConsultaJuridicaForm(instance=consulta)
        form_html = render_to_string('assejus/forms/consulta_form_modal.html', {'form': form}, request=request)
        return JsonResponse({'form_html': form_html})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def relatorio_modal_create(request):
    """View para criar relatório via modal"""
    if request.method == 'POST':
        form = RelatorioJuridicoForm(request.POST)
        if form.is_valid():
            relatorio = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Relatório jurídico criado com sucesso!',
                'reload': True,
                'id': relatorio.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro na validação do formulário.',
                'errors': form.errors
            })
    
    form = RelatorioJuridicoForm()
    form_html = render_to_string('assejus/forms/relatorio_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'form_html': form_html})


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def relatorio_modal_update(request, pk):
    """View para editar relatório via modal"""
    try:
        relatorio = get_object_or_404(RelatorioJuridico, pk=pk)
        
        if request.method == 'POST':
            form = RelatorioJuridicoForm(request.POST, instance=relatorio)
            if form.is_valid():
                relatorio = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Relatório jurídico atualizado com sucesso!',
                    'reload': True,
                    'id': relatorio.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro na validação do formulário.',
                    'errors': form.errors
                })
        
        form = RelatorioJuridicoForm(instance=relatorio)
        form_html = render_to_string('assejus/forms/relatorio_form_modal.html', {'form': form}, request=request)
        return JsonResponse({'form_html': form_html})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }, status=500)


@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def advogado_detail_modal(request, pk):
    """View para exibir detalhes do advogado via modal"""
    
    try:
        advogado = get_object_or_404(Advogado, pk=pk)
        
        # Calcular estatísticas do advogado
        total_casos = AtendimentoJuridico.objects.filter(advogado_responsavel=advogado).count()
        casos_em_andamento = AtendimentoJuridico.objects.filter(
            advogado_responsavel=advogado,
            status__in=['em_andamento', 'em_analise', 'aguardando_documentos', 'aguardando_decisao']
        ).count()
        casos_concluidos = AtendimentoJuridico.objects.filter(
            advogado_responsavel=advogado,
            status='concluido'
        ).count()
        
        
        context = {
            'advogado': advogado,
            'total_casos': total_casos,
            'casos_em_andamento': casos_em_andamento,
            'casos_concluidos': casos_concluidos,
        }
        
        
        # Renderizar o template de detalhes completo (incluindo o modal)
        modal_html = render(request, 'assejus/advogado_detail_modal.html', context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'modal_html': modal_html,
            'advogado': {
                'id': advogado.id,
                'nome': advogado.nome,
                'oab': advogado.oab,
                'uf_oab': advogado.uf_oab,
                'email': advogado.email,
                'telefone': advogado.telefone,
                'celular': advogado.celular,
                'endereco': advogado.endereco,
                'cidade': advogado.cidade,
                'estado': advogado.estado,
                'cep': advogado.cep,
                'especialidades': advogado.especialidades,
                'data_inscricao_oab': advogado.data_inscricao_oab.strftime('%d/%m/%Y') if advogado.data_inscricao_oab else '',
                'experiencia_anos': advogado.experiencia_anos,
                'ativo': advogado.ativo,
                'observacoes': advogado.observacoes,
                'data_cadastro': advogado.data_cadastro.strftime('%d/%m/%Y às %H:%M') if advogado.data_cadastro else '',
                'data_atualizacao': advogado.data_atualizacao.strftime('%d/%m/%Y às %H:%M') if advogado.data_atualizacao else '',
            }
        })
        
    except Exception as e:
        import traceback
        
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar detalhes do advogado: {str(e)}'
        })

@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def modal_base(request):
    """View para servir o template base de modais"""
    return render(request, 'assejus/modal_base.html')





