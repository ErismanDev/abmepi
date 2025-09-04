from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q


def marcar_atendimentos_concluidos(modeladmin, request, queryset):
    """Marca atendimentos selecionados como concluídos"""
    updated = queryset.update(
        status='concluido',
        data_conclusao=timezone.now()
    )
    messages.success(
        request, 
        f'{updated} atendimento(s) marcado(s) como concluído(s) com sucesso.'
    )
marcar_atendimentos_concluidos.short_description = "Marcar como concluído"


def marcar_atendimentos_em_andamento(modeladmin, request, queryset):
    """Marca atendimentos selecionados como em andamento"""
    updated = queryset.update(status='em_andamento')
    messages.success(
        request, 
        f'{updated} atendimento(s) marcado(s) como em andamento com sucesso.'
    )
marcar_atendimentos_em_andamento.short_description = "Marcar como em andamento"


def marcar_consultas_resolvidas(modeladmin, request, queryset):
    """Marca consultas selecionadas como resolvidas"""
    updated = queryset.update(
        resolvida=True,
        data_resposta=timezone.now(),
        usuario_resposta=request.user
    )
    messages.success(
        request, 
        f'{updated} consulta(s) marcada(s) como resolvida(s) com sucesso.'
    )
marcar_consultas_resolvidas.short_description = "Marcar como resolvida"


def ativar_advogados(modeladmin, request, queryset):
    """Ativa advogados selecionados"""
    updated = queryset.update(ativo=True)
    messages.success(
        request, 
        f'{updated} advogado(s) ativado(s) com sucesso.'
    )
ativar_advogados.short_description = "Ativar advogados"


def desativar_advogados(modeladmin, request, queryset):
    """Desativa advogados selecionados"""
    updated = queryset.update(ativo=False)
    messages.success(
        request, 
        f'{updated} advogado(s) desativado(s) com sucesso.'
    )
desativar_advogados.short_description = "Desativar advogados"


def exportar_dados_assejus(modeladmin, request, queryset):
    """Exporta dados selecionados para CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assejus_export.csv"'
    
    writer = csv.writer(response)
    
    # Cabeçalho baseado no modelo
    if queryset.model == modeladmin.model:
        # Escreve cabeçalho baseado nos campos do modelo
        field_names = [field.name for field in queryset.model._meta.fields]
        writer.writerow(field_names)
        
        # Escreve dados
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if hasattr(value, 'strftime'):  # Se for data
                    value = value.strftime('%d/%m/%Y')
                row.append(str(value) if value is not None else '')
            writer.writerow(row)
    
    messages.success(request, f'Exportação concluída com sucesso!')
    return response
exportar_dados_assejus.short_description = "Exportar dados selecionados"


def limpar_dados_antigos(modeladmin, request, queryset):
    """Remove dados antigos (mais de 5 anos)"""
    from datetime import timedelta
    
    # Calcula data limite (5 anos atrás)
    data_limite = timezone.now() - timedelta(days=5*365)
    
    # Filtra objetos antigos
    if hasattr(queryset.model, 'data_cadastro'):
        antigos = queryset.filter(data_cadastro__lt=data_limite)
    elif hasattr(queryset.model, 'data_abertura'):
        antigos = queryset.filter(data_abertura__lt=data_limite)
    elif hasattr(queryset.model, 'data_consulta'):
        antigos = queryset.filter(data_consulta__lt=data_limite)
    else:
        messages.warning(request, 'Modelo não possui campo de data para limpeza.')
        return
    
    count = antigos.count()
    if count > 0:
        antigos.delete()
        messages.success(
            request, 
            f'{count} registro(s) antigo(s) removido(s) com sucesso.'
        )
    else:
        messages.info(request, 'Nenhum registro antigo encontrado para remoção.')

limpar_dados_antigos.short_description = "Limpar dados antigos (>5 anos)"


# Dicionário de ações por modelo
ASSEJUS_ACTIONS = {
    'Advogado': [ativar_advogados, desativar_advogados, exportar_dados_assejus],
    'AtendimentoJuridico': [
        marcar_atendimentos_concluidos, 
        marcar_atendimentos_em_andamento, 
        exportar_dados_assejus
    ],
    'ConsultaJuridica': [
        marcar_consultas_resolvidas, 
        exportar_dados_assejus
    ],
    'DocumentoJuridico': [exportar_dados_assejus],
    'Andamento': [exportar_dados_assejus],
    'RelatorioJuridico': [exportar_dados_assejus, limpar_dados_antigos],
    'ProcessoJuridico': [exportar_dados_assejus],
}
