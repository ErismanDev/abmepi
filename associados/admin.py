from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.utils import timezone
from .models import Associado, Documento, Dependente, PreCadastroAssociado, DependentePreCadastro


@admin.register(Associado)
class AssociadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'tipo_socio', 'tipo_profissional', 'matricula_militar', 'posto_graduacao', 'situacao', 'ativo', 'foto_preview')
    list_filter = ('tipo_socio', 'tipo_profissional', 'situacao', 'ativo', 'estado', 'sexo', 'estado_civil')
    search_fields = ('nome', 'cpf', 'matricula_militar', 'email')
    list_per_page = 25
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'rg', 'data_nascimento', 'sexo', 'foto', 'estado_civil', 'naturalidade', 'nacionalidade', 'email', 'telefone', 'celular')
        }),
        ('Dados dos Pais', {
            'fields': ('nome_pai', 'nome_mae')
        }),
        ('Endereço', {
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Funcionais', {
            'fields': ('tipo_socio', 'tipo_profissional', 'matricula_militar', 'posto_graduacao', 'nome_civil', 'unidade_lotacao', 'data_ingresso', 'situacao', 'tipo_documento')
        }),
        ('Sistema', {
            'fields': ('usuario', 'ativo', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sem foto"
    foto_preview.short_description = 'Foto'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['ativar_associados', 'desativar_associados']
    
    def ativar_associados(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} associado(s) ativado(s) com sucesso.')
    ativar_associados.short_description = "Ativar associados selecionados"
    
    def desativar_associados(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} associado(s) desativado(s) com sucesso.')
    desativar_associados.short_description = "Desativar associados selecionados"


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('associado', 'tipo', 'descricao', 'data_upload', 'ativo')
    list_filter = ('tipo', 'ativo', 'data_upload')
    search_fields = ('associado__nome', 'descricao')
    list_per_page = 25
    ordering = ('-data_upload',)
    
    fieldsets = (
        ('Informações do Documento', {
            'fields': ('associado', 'tipo', 'arquivo', 'descricao')
        }),
        ('Controle', {
            'fields': ('ativo',)
        }),
    )
    
    readonly_fields = ('data_upload',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado')


@admin.register(Dependente)
class DependenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'associado', 'parentesco', 'data_nascimento', 'idade', 'email', 'ativo')
    list_filter = ('parentesco', 'ativo', 'data_nascimento')
    search_fields = ('nome', 'associado__nome', 'cpf', 'email')
    list_per_page = 25
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações do Dependente', {
            'fields': ('associado', 'nome', 'parentesco', 'data_nascimento', 'foto', 'cpf', 'email')
        }),
        ('Controle', {
            'fields': ('ativo', 'observacoes')
        }),
    )
    
    def idade(self, obj):
        return obj.get_idade()
    idade.short_description = 'Idade'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado')


@admin.register(PreCadastroAssociado)
class PreCadastroAssociadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'tipo_profissao', 'email', 'status', 'data_solicitacao', 'foto_preview')
    list_filter = ('status', 'tipo_profissao', 'estado', 'data_solicitacao')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    list_per_page = 25
    ordering = ('-data_solicitacao',)
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'rg', 'data_nascimento', 'sexo', 'foto', 'estado_civil', 'naturalidade', 'nacionalidade', 'email', 'telefone', 'celular')
        }),
        ('Dados dos Pais', {
            'fields': ('nome_pai', 'nome_mae')
        }),
        ('Endereço', {
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Profissionais', {
            'fields': ('tipo_profissao', 'posto_graduacao', 'orgao', 'matricula', 'situacao', 'tipo_documento')
        }),
        ('Status e Controle', {
            'fields': ('status', 'observacoes', 'data_solicitacao', 'data_analise', 'analisado_por', 'motivo_rejeicao')
        }),
    )
    
    readonly_fields = ('data_solicitacao', 'data_analise', 'analisado_por')
    
    actions = ['aprovar_pre_cadastros', 'rejeitar_pre_cadastros']
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sem foto"
    foto_preview.short_description = 'Foto'
    
    def aprovar_pre_cadastros(self, request, queryset):
        """Aprova pré-cadastros selecionados e os converte em associados"""
        aprovados = 0
        erros = 0
        
        for pre_cadastro in queryset.filter(status='pendente'):
            try:
                associado = pre_cadastro.converter_para_associado(request.user)
                aprovados += 1
                messages.success(request, f'Pré-cadastro de {pre_cadastro.nome} aprovado e convertido para associado ID: {associado.id}')
            except Exception as e:
                erros += 1
                messages.error(request, f'Erro ao aprovar {pre_cadastro.nome}: {str(e)}')
        
        if aprovados > 0:
            self.message_user(request, f'{aprovados} pré-cadastro(s) aprovado(s) e convertido(s) para associado(s) com sucesso.')
        
        if erros > 0:
            self.message_user(request, f'{erros} erro(s) ocorreram durante o processo de aprovação.')
    
    aprovar_pre_cadastros.short_description = "Aprovar pré-cadastros selecionados e converter para associados"
    
    def rejeitar_pre_cadastros(self, request, queryset):
        """Rejeita pré-cadastros selecionados"""
        rejeitados = queryset.filter(status='pendente').update(
            status='rejeitado',
            data_analise=timezone.now(),
            analisado_por=request.user
        )
        
        if rejeitados > 0:
            self.message_user(request, f'{rejeitados} pré-cadastro(s) rejeitado(s) com sucesso.')
        else:
            self.message_user(request, 'Nenhum pré-cadastro pendente foi selecionado para rejeição.')
    
    rejeitar_pre_cadastros.short_description = "Rejeitar pré-cadastros selecionados"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('analisado_por')


@admin.register(DependentePreCadastro)
class DependentePreCadastroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pre_cadastro', 'parentesco', 'data_nascimento', 'idade', 'email')
    list_filter = ('parentesco', 'data_nascimento')
    search_fields = ('nome', 'pre_cadastro__nome', 'cpf', 'email')
    list_per_page = 25
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações do Dependente', {
            'fields': ('pre_cadastro', 'nome', 'parentesco', 'data_nascimento', 'foto', 'cpf', 'email')
        }),
        ('Controle', {
            'fields': ('observacoes',)
        }),
    )
    
    def idade(self, obj):
        return obj.get_idade()
    idade.short_description = 'Idade'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pre_cadastro')
