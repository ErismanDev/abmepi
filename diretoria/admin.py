from django.contrib import admin
from .models import CargoDiretoria, MembroDiretoria, AtaReuniao, ResolucaoDiretoria, ModeloAtaPersonalizado, ModeloAtaUnificado


@admin.register(CargoDiretoria)
class CargoDiretoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ordem_hierarquica', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem_hierarquica', 'nome']
    list_editable = ['ordem_hierarquica', 'ativo']


@admin.register(MembroDiretoria)
class MembroDiretoriaAdmin(admin.ModelAdmin):
    list_display = ['associado', 'cargo', 'data_inicio', 'data_fim', 'ativo']
    list_filter = ['cargo', 'ativo', 'data_inicio', 'data_fim']
    search_fields = ['associado__nome', 'cargo__nome']
    ordering = ['cargo__ordem_hierarquica', 'associado__nome']
    list_editable = ['ativo']
    raw_id_fields = ['associado']


@admin.register(AtaReuniao)
class AtaReuniaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_reuniao', 'data_reuniao', 'local', 'aprovada']
    list_filter = ['tipo_reuniao', 'aprovada', 'data_reuniao']
    search_fields = ['titulo', 'pauta', 'deliberacoes']
    ordering = ['-data_reuniao']
    list_editable = ['aprovada']
    filter_horizontal = ['membros_presentes', 'membros_ausentes', 'associados_presentes', 'associados_ausentes']
    raw_id_fields = ['presidente', 'secretario']


@admin.register(ResolucaoDiretoria)
class ResolucaoDiretoriaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'data_resolucao', 'status']
    list_filter = ['status', 'data_resolucao', 'data_publicacao']
    search_fields = ['numero', 'titulo', 'ementa']
    ordering = ['-data_resolucao', '-numero']
    list_editable = ['status']
    raw_id_fields = ['ata_reuniao']


@admin.register(ModeloAtaPersonalizado)
class ModeloAtaPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'tipo_reuniao', 'criado_por', 'vezes_usado', 'publico', 'ativo', 'data_criacao']
    list_filter = ['categoria', 'tipo_reuniao', 'publico', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao', 'criado_por__username', 'criado_por__first_name', 'criado_por__last_name']
    ordering = ['-data_atualizacao']
    list_editable = ['publico', 'ativo']
    raw_id_fields = ['criado_por']
    readonly_fields = ['vezes_usado', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'tipo_reuniao')
        }),
        ('Conteúdo', {
            'fields': ('conteudo_html', 'titulo_original')
        }),
        ('Configurações', {
            'fields': ('criado_por', 'publico', 'ativo')
        }),
        ('Estatísticas', {
            'fields': ('vezes_usado', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ModeloAtaUnificado)
class ModeloAtaUnificadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'tipo_conteudo', 'criado_por', 'vezes_usado', 'publico', 'ativo', 'data_criacao']
    list_filter = ['categoria', 'tipo_conteudo', 'publico', 'ativo', 'data_criacao']
    search_fields = ['nome', 'descricao', 'tags', 'criado_por__username', 'criado_por__first_name', 'criado_por__last_name']
    ordering = ['-data_atualizacao']
    list_editable = ['publico', 'ativo']
    raw_id_fields = ['criado_por']
    readonly_fields = ['vezes_usado', 'ultimo_uso', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'categoria', 'tipo_conteudo')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'conteudo_html', 'titulo_original')
        }),
        ('Organização', {
            'fields': ('tags',)
        }),
        ('Configurações', {
            'fields': ('criado_por', 'publico', 'ativo')
        }),
        ('Estatísticas', {
            'fields': ('vezes_usado', 'ultimo_uso', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('criado_por')