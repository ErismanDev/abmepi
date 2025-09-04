from django.contrib import admin
from .models import ConfiguracaoCobranca

@admin.register(ConfiguracaoCobranca)
class ConfiguracaoCobrancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'chave_pix', 'titular', 'banco', 'data_atualizacao']
    list_filter = ['ativo', 'qr_code_ativo', 'data_criacao', 'data_atualizacao']
    search_fields = ['nome', 'chave_pix', 'titular', 'banco']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativo')
        }),
        ('Dados de Cobrança', {
            'fields': ('chave_pix', 'titular', 'banco')
        }),
        ('Mensagem Personalizada', {
            'fields': ('mensagem_linha1', 'mensagem_linha2', 'mensagem_linha3', 'telefone_comprovante'),
            'description': 'Configure as mensagens que aparecerão no carnê'
        }),
        ('Configurações do QR Code', {
            'fields': ('qr_code_ativo', 'qr_code_tamanho'),
            'description': 'Configure a exibição e tamanho do QR Code'
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        # Se esta configuração for ativada, desativar as outras
        if obj.ativo:
            ConfiguracaoCobranca.objects.exclude(id=obj.id).update(ativo=False)
        super().save_model(request, obj, form, change)
