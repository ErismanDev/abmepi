from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Advogado, AtendimentoJuridico, DocumentoJuridico, 
    Andamento, ConsultaJuridica, RelatorioJuridico,
    ProcessoJuridico
)
from .admin_actions import ASSEJUS_ACTIONS
from .admin_filters import ASSEJUS_FILTERS


@admin.register(Advogado)
class AdvogadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'oab', 'uf_oab', 'especialidades', 'ativo']
    list_filter = ['ativo', 'uf_oab', 'especialidades'] + ASSEJUS_FILTERS['Advogado']
    search_fields = ['nome', 'cpf', 'oab', 'email']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    actions = ASSEJUS_ACTIONS['Advogado']
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'cpf', 'oab', 'uf_oab')
        }),
        ('Contato', {
            'fields': ('email', 'telefone', 'celular')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Profissional', {
            'fields': ('especialidades', 'data_inscricao_oab', 'experiencia_anos')
        }),
        ('Status', {
            'fields': ('ativo', 'observacoes')
        }),
        ('Controle', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AtendimentoJuridico)
class AtendimentoJuridicoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'associado', 'tipo_demanda', 'status', 'prioridade', 'data_abertura']
    list_filter = ['status', 'prioridade', 'tipo_demanda', 'data_abertura'] + ASSEJUS_FILTERS['AtendimentoJuridico']
    search_fields = ['titulo', 'associado__nome', 'descricao']
    readonly_fields = ['data_abertura']
    date_hierarchy = 'data_abertura'
    actions = ASSEJUS_ACTIONS['AtendimentoJuridico']
    
    fieldsets = (
        ('Dados Básicos', {
            'fields': ('associado', 'tipo_demanda', 'titulo', 'descricao')
        }),
        ('Controle', {
            'fields': ('status', 'prioridade', 'data_limite')
        }),
        ('Responsáveis', {
            'fields': ('advogado_responsavel', 'usuario_responsavel')
        }),
        ('Resultado', {
            'fields': ('resultado', 'observacoes', 'data_conclusao')
        }),
        ('Controle', {
            'fields': ('data_abertura',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentoJuridico)
class DocumentoJuridicoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_documento', 'processo', 'usuario_upload', 'data_upload']
    list_filter = ['tipo_documento', 'data_upload'] + ASSEJUS_FILTERS['DocumentoJuridico']
    search_fields = ['titulo', 'descricao', 'processo__numero_processo']
    readonly_fields = ['data_upload']
    actions = ASSEJUS_ACTIONS['DocumentoJuridico']
    
    fieldsets = (
        ('Documento', {
            'fields': ('titulo', 'tipo_documento', 'descricao', 'arquivo')
        }),
        ('Relacionamento', {
            'fields': ('processo', 'usuario_upload')
        }),
        ('Controle', {
            'fields': ('data_upload',)
        }),
    )


@admin.register(Andamento)
class AndamentoAdmin(admin.ModelAdmin):
    list_display = ['processo', 'tipo_andamento', 'usuario_registro', 'data_andamento']
    list_filter = ['tipo_andamento', 'data_andamento'] + ASSEJUS_FILTERS['Andamento']
    search_fields = ['descricao_detalhada', 'processo__numero_processo']
    readonly_fields = ['data_andamento']
    actions = ASSEJUS_ACTIONS['Andamento']
    
    fieldsets = (
        ('Andamento', {
            'fields': ('processo', 'data_andamento', 'tipo_andamento', 'descricao_detalhada')
        }),
        ('Observações', {
            'fields': ('observacoes_cliente',)
        }),
        ('Controle', {
            'fields': ('usuario_registro', 'cliente_visualizou', 'data_visualizacao_cliente')
        }),
    )


@admin.register(ProcessoJuridico)
class ProcessoJuridicoAdmin(admin.ModelAdmin):
    list_display = ['numero_processo', 'parte_cliente', 'tipo_acao', 'situacao_atual', 'advogado_responsavel']
    list_filter = ['situacao_atual', 'tipo_acao', 'data_cadastro'] + ASSEJUS_FILTERS['ProcessoJuridico']
    search_fields = ['numero_processo', 'parte_cliente__nome', 'parte_contraria']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    actions = ASSEJUS_ACTIONS['ProcessoJuridico']
    
    fieldsets = (
        ('Dados do Processo', {
            'fields': ('numero_processo', 'vara_tribunal', 'tipo_acao', 'situacao_atual')
        }),
        ('Partes', {
            'fields': ('parte_cliente', 'parte_contraria')
        }),
        ('Responsável', {
            'fields': ('advogado_responsavel',)
        }),
        ('Observações', {
            'fields': ('observacoes_gerais',)
        }),
        ('Controle', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsultaJuridica)
class ConsultaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['associado', 'tipo', 'resolvida', 'data_consulta', 'data_resposta']
    list_filter = ['tipo', 'resolvida', 'data_consulta'] + ASSEJUS_FILTERS['ConsultaJuridica']
    search_fields = ['associado__nome', 'pergunta', 'resposta']
    readonly_fields = ['data_consulta']
    actions = ASSEJUS_ACTIONS['ConsultaJuridica']
    
    fieldsets = (
        ('Consulta', {
            'fields': ('associado', 'tipo', 'pergunta')
        }),
        ('Resposta', {
            'fields': ('resposta', 'usuario_resposta', 'data_resposta')
        }),
        ('Status', {
            'fields': ('resolvida',)
        }),
        ('Controle', {
            'fields': ('data_consulta',)
        }),
    )


@admin.register(RelatorioJuridico)
class RelatorioJuridicoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'periodo_inicio', 'periodo_fim', 'usuario_geracao', 'data_geracao']
    list_filter = ['tipo', 'data_geracao'] + ASSEJUS_FILTERS['RelatorioJuridico']
    search_fields = ['tipo']
    readonly_fields = ['data_geracao']
    actions = ASSEJUS_ACTIONS['RelatorioJuridico']
    
    fieldsets = (
        ('Relatório', {
            'fields': ('tipo', 'periodo_inicio', 'periodo_fim')
        }),
        ('Arquivo', {
            'fields': ('arquivo',)
        }),
        ('Controle', {
            'fields': ('usuario_geracao', 'data_geracao')
        }),
    )
