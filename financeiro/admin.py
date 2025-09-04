from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import TipoMensalidade, Mensalidade, Pagamento, Despesa, RelatorioFinanceiro, ConfiguracaoCobranca


@admin.register(TipoMensalidade)
class TipoMensalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'valor', 'recorrente', 'ativo')
    list_filter = ('categoria', 'recorrente', 'ativo')
    search_fields = ('nome', 'descricao')
    ordering = ('categoria', 'nome')
    
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'descricao', 'valor', 'categoria')
        }),
        ('Controle', {
            'fields': ('recorrente', 'ativo')
        }),
    )


@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('associado', 'tipo', 'valor', 'data_vencimento', 'status', 'dias_atraso', 'valor_com_multa')
    list_filter = ('status', 'tipo', 'data_vencimento', 'associado__situacao')
    search_fields = ('associado__nome', 'associado__cpf')
    list_per_page = 25
    ordering = ('-data_vencimento',)
    
    fieldsets = (
        ('Informações da Mensalidade', {
            'fields': ('associado', 'tipo', 'valor', 'data_vencimento')
        }),
        ('Status e Pagamento', {
            'fields': ('status', 'data_pagamento', 'forma_pagamento')
        }),
        ('Outros', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def dias_atraso(self, obj):
        dias = obj.get_dias_atraso()
        if dias > 0:
            return format_html('<span style="color: red; font-weight: bold;">{} dias</span>', dias)
        return "Em dia"
    dias_atraso.short_description = 'Dias em Atraso'
    
    def valor_com_multa(self, obj):
        valor = obj.get_valor_com_multa()
        if valor != obj.valor:
            return format_html('<span style="color: red; font-weight: bold;">R$ {:.2f}</span>', valor)
        return f"R$ {obj.valor:.2f}"
    valor_com_multa.short_description = 'Valor com Multa'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado', 'tipo')
    
    actions = ['marcar_como_pago', 'marcar_como_pendente']
    
    def marcar_como_pago(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='pago', data_pagamento=timezone.now().date())
        self.message_user(request, f'{updated} mensalidade(s) marcada(s) como paga(s).')
    marcar_como_pago.short_description = "Marcar como pago"
    
    def marcar_como_pendente(self, request, queryset):
        updated = queryset.update(status='pendente', data_pagamento=None)
        self.message_user(request, f'{updated} mensalidade(s) marcada(s) como pendente(s).')
    marcar_como_pendente.short_description = "Marcar como pendente"


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('mensalidade', 'valor_pago', 'forma_pagamento', 'data_pagamento', 'usuario_registro')
    list_filter = ('forma_pagamento', 'data_pagamento')
    search_fields = ('mensalidade__associado__nome', 'mensalidade__associado__cpf')
    list_per_page = 25
    ordering = ('-data_pagamento',)
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('mensalidade', 'valor_pago', 'forma_pagamento')
        }),
        ('Documentos', {
            'fields': ('comprovante', 'observacoes')
        }),
        ('Sistema', {
            'fields': ('usuario_registro',)
        }),
    )
    
    readonly_fields = ('data_pagamento',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mensalidade__associado', 'usuario_registro')


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'categoria', 'valor', 'data_despesa', 'pago', 'fornecedor')
    list_filter = ('categoria', 'pago', 'data_despesa')
    search_fields = ('descricao', 'fornecedor', 'nota_fiscal')
    list_per_page = 25
    ordering = ('-data_despesa',)
    
    fieldsets = (
        ('Informações da Despesa', {
            'fields': ('descricao', 'categoria', 'valor', 'data_despesa', 'data_vencimento')
        }),
        ('Fornecedor e Documentos', {
            'fields': ('fornecedor', 'nota_fiscal', 'comprovante')
        }),
        ('Controle', {
            'fields': ('pago', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    actions = ['marcar_como_pago', 'marcar_como_nao_pago']
    
    def marcar_como_pago(self, request, queryset):
        updated = queryset.update(pago=True)
        self.message_user(request, f'{updated} despesa(s) marcada(s) como paga(s).')
    marcar_como_pago.short_description = "Marcar como pago"
    
    def marcar_como_nao_pago(self, request, queryset):
        updated = queryset.update(pago=False)
        self.message_user(request, f'{updated} despesa(s) marcada(s) como não paga(s).')
    marcar_como_nao_pago.short_description = "Marcar como não pago"


@admin.register(RelatorioFinanceiro)
class RelatorioFinanceiroAdmin(admin.ModelAdmin):
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


@admin.register(ConfiguracaoCobranca)
class ConfiguracaoCobrancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'chave_pix', 'titular', 'banco', 'data_atualizacao']
    list_filter = ['ativo', 'qr_code_ativo', 'data_criacao']
    search_fields = ['nome', 'chave_pix', 'titular', 'banco']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    # Não permitir criar múltiplas configurações
    def has_add_permission(self, request):
        # Só permitir adicionar se não existir nenhuma configuração
        return not ConfiguracaoCobranca.objects.exists()
    
    # Não permitir excluir a configuração
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Redirecionar para a configuração única
    def changelist_view(self, request, extra_context=None):
        # Se existir configuração, redirecionar para edição
        config = ConfiguracaoCobranca.objects.first()
        if config:
            return self.response_post_save_change(request, config)
        # Se não existir, redirecionar para criação
        return self.add_view(request)
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('nome', 'ativo')
        }),
        ('Dados de Cobrança', {
            'fields': ('chave_pix', 'titular', 'banco')
        }),
        ('Mensagem Personalizada', {
            'fields': ('mensagem', 'telefone_comprovante')
        }),
        ('Configurações do QR Code', {
            'fields': ('qr_code_ativo', 'qr_code_imagem', 'qr_code_tamanho')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        # Se esta configuração for ativada, desativar as outras
        if obj.ativo:
            ConfiguracaoCobranca.objects.exclude(pk=obj.pk).update(ativo=False)
        super().save_model(request, obj, form, change)
