from django.contrib import admin
from django.utils.html import format_html
from .models import EmpresaParceira, Convenio, Beneficio, CategoriaBeneficio, RelatorioBeneficios


@admin.register(EmpresaParceira)
class EmpresaParceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'telefone', 'email', 'ativo')
    list_filter = ('estado', 'ativo', 'data_cadastro')
    search_fields = ('nome', 'cnpj', 'razao_social', 'cidade')
    list_per_page = 25
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações da Empresa', {
            'fields': ('nome', 'cnpj', 'razao_social')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'website')
        }),
        ('Contato Principal', {
            'fields': ('contato_principal', 'telefone_contato', 'email_contato')
        }),
        ('Controle', {
            'fields': ('ativo', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    actions = ['ativar_empresas', 'desativar_empresas']
    
    def ativar_empresas(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} empresa(s) ativada(s) com sucesso.')
    ativar_empresas.short_description = "Ativar empresas selecionadas"
    
    def desativar_empresas(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} empresa(s) desativada(s) com sucesso.')
    desativar_empresas.short_description = "Desativar empresas selecionadas"


@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa', 'categoria', 'status', 'data_inicio', 'data_fim', 'desconto', 'ativo')
    list_filter = ('status', 'categoria', 'ativo', 'data_inicio')
    search_fields = ('titulo', 'empresa__nome', 'desconto')
    list_per_page = 25
    ordering = ('-data_inicio',)
    
    fieldsets = (
        ('Informações do Convênio', {
            'fields': ('empresa', 'titulo', 'descricao', 'categoria')
        }),
        ('Status e Período', {
            'fields': ('status', 'data_inicio', 'data_fim')
        }),
        ('Benefícios', {
            'fields': ('desconto', 'condicoes', 'documentos_necessarios')
        }),
        ('Responsável', {
            'fields': ('usuario_responsavel',)
        }),
        ('Mídia', {
            'fields': ('arquivos_anexados',)
        }),
        ('Controle', {
            'fields': ('ativo', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('empresa', 'usuario_responsavel')
    
    actions = ['ativar_convenios', 'desativar_convenios']
    
    def ativar_convenios(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} convênio(s) ativado(s) com sucesso.')
    ativar_convenios.short_description = "Ativar convênios selecionados"
    
    def desativar_convenios(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} convênio(s) desativado(s) com sucesso.')
    desativar_convenios.short_description = "Desativar convênios selecionados"


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('associado', 'convenio', 'status', 'data_solicitacao', 'data_aprovacao', 'valor_beneficio', 'dias_aprovacao')
    list_filter = ('status', 'data_solicitacao', 'convenio__categoria')
    search_fields = ('associado__nome', 'associado__cpf', 'convenio__titulo')
    list_per_page = 25
    ordering = ('-data_solicitacao',)
    
    fieldsets = (
        ('Benefício', {
            'fields': ('associado', 'convenio', 'status')
        }),
        ('Valores', {
            'fields': ('valor_beneficio', 'desconto_aplicado')
        }),
        ('Datas', {
            'fields': ('data_aprovacao', 'data_utilizacao')
        }),
        ('Aprovação', {
            'fields': ('usuario_aprovacao',)
        }),
        ('Documentos', {
            'fields': ('comprovante', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_solicitacao',)
    
    def dias_aprovacao(self, obj):
        dias = obj.get_dias_aprovacao()
        if dias is not None:
            if dias <= 1:
                return format_html('<span style="color: green; font-weight: bold;">{} dia</span>', dias)
            elif dias <= 3:
                return format_html('<span style="color: blue; font-weight: bold;">{} dias</span>', dias)
            else:
                return format_html('<span style="color: orange; font-weight: bold;">{} dias</span>', dias)
        return "Pendente"
    dias_aprovacao.short_description = 'Dias para Aprovação'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado', 'convenio', 'usuario_aprovacao')
    
    actions = ['aprovar_beneficios', 'rejeitar_beneficios']
    
    def aprovar_beneficios(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='aprovado',
            data_aprovacao=timezone.now(),
            usuario_aprovacao=request.user
        )
        self.message_user(request, f'{updated} benefício(s) aprovado(s) com sucesso.')
    aprovar_beneficios.short_description = "Aprovar benefícios selecionados"
    
    def rejeitar_beneficios(self, request, queryset):
        updated = queryset.update(status='rejeitado')
        self.message_user(request, f'{updated} benefício(s) rejeitado(s) com sucesso.')
    rejeitar_beneficios.short_description = "Rejeitar benefícios selecionados"


@admin.register(CategoriaBeneficio)
class CategoriaBeneficioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'icone', 'cor', 'ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    list_per_page = 25
    ordering = ('ordem', 'nome')
    
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'descricao')
        }),
        ('Aparência', {
            'fields': ('icone', 'cor')
        }),
        ('Controle', {
            'fields': ('ativo', 'ordem')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    actions = ['ativar_categorias', 'desativar_categorias']
    
    def ativar_categorias(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} categoria(s) ativada(s) com sucesso.')
    ativar_categorias.short_description = "Ativar categorias selecionadas"
    
    def desativar_categorias(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} categoria(s) desativada(s) com sucesso.')
    desativar_categorias.short_description = "Desativar categorias selecionadas"


@admin.register(RelatorioBeneficios)
class RelatorioBeneficiosAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'periodo_inicio', 'periodo_fim', 'data_geracao', 'usuario_geracao')
    list_filter = ('tipo', 'data_geracao')
    search_fields = ('tipo', 'usuario_geracao__username')
    list_per_page = 25
    ordering = ('-data_geracao',)
    
    fieldsets = (
        ('Informações do Relatório', {
            'fields': ('tipo', 'periodo_inicio', 'periodo_fim')
        }),
        ('Arquivo', {
            'fields': ('arquivo',)
        }),
        ('Sistema', {
            'fields': ('usuario_geracao',)
        }),
    )
    
    readonly_fields = ('data_geracao',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario_geracao')
