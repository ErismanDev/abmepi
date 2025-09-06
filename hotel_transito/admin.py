from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Quarto, Hospede, Reserva, Hospedagem, 
    ServicoAdicional, ServicoUtilizado
)


@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'tipo', 'capacidade', 'valor_diaria', 
        'status', 'ar_condicionado', 'tv', 'wifi', 'ativo'
    ]
    list_filter = ['tipo', 'status', 'ar_condicionado', 'tv', 'wifi', 'ativo']
    search_fields = ['numero', 'observacoes']
    list_editable = ['status', 'ativo']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'tipo', 'capacidade', 'valor_diaria', 'status')
        }),
        ('Características', {
            'fields': ('ar_condicionado', 'tv', 'wifi', 'banheiro_privativo', 'frigobar')
        }),
        ('Outras Informações', {
            'fields': ('observacoes', 'ativo', 'data_cadastro', 'data_atualizacao')
        }),
    )


@admin.register(Hospede)
class HospedeAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo', 'tipo_hospede', 'associado_link', 'telefone', 
        'email', 'cidade', 'estado', 'ativo'
    ]
    list_filter = ['tipo_hospede', 'ativo', 'estado', 'cidade']
    search_fields = ['nome_completo', 'numero_documento', 'email', 'telefone']
    list_editable = ['ativo']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    
    def associado_link(self, obj):
        if obj.associado:
            url = reverse('admin:associados_associado_change', args=[obj.associado.id])
            return format_html('<a href="{}">{}</a>', url, obj.associado.matricula)
        return "Não Associado"
    associado_link.short_description = "Associado"
    associado_link.admin_order_field = 'associado__matricula'
    
    fieldsets = (
        ('Tipo de Hóspede', {
            'fields': ('tipo_hospede', 'associado')
        }),
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'data_nascimento', 'foto')
        }),
        ('Documentos', {
            'fields': ('tipo_documento', 'numero_documento', 'orgao_emissor', 'uf_emissor')
        }),
        ('Contato', {
            'fields': ('telefone', 'telefone_secundario', 'email')
        }),
        ('Endereço', {
            'fields': ('cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Profissionais', {
            'fields': ('profissao', 'empresa'),
            'classes': ('collapse',)
        }),
        ('Outras Informações', {
            'fields': ('observacoes', 'ativo', 'data_cadastro', 'data_atualizacao')
        }),
    )


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_reserva', 'hospede', 'quarto', 'data_entrada', 
        'data_saida', 'quantidade_diarias', 'valor_total', 'status'
    ]
    list_filter = ['status', 'data_entrada', 'data_saida', 'quarto__tipo']
    search_fields = ['codigo_reserva', 'hospede__nome_completo', 'quarto__numero']
    list_editable = ['status']
    readonly_fields = [
        'codigo_reserva', 'quantidade_diarias', 'valor_total', 
        'data_reserva', 'data_confirmacao', 'data_cancelamento'
    ]
    
    fieldsets = (
        ('Dados da Reserva', {
            'fields': ('codigo_reserva', 'quarto', 'hospede')
        }),
        ('Datas', {
            'fields': ('data_entrada', 'data_saida', 'hora_entrada', 'hora_saida')
        }),
        ('Valores', {
            'fields': ('valor_diaria', 'quantidade_diarias', 'valor_total')
        }),
        ('Status', {
            'fields': ('status', 'data_confirmacao', 'data_cancelamento')
        }),
        ('Outras Informações', {
            'fields': ('observacoes', 'motivo_cancelamento', 'data_reserva')
        }),
    )


@admin.register(Hospedagem)
class HospedagemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'hospede', 'quarto', 'data_entrada_real', 
        'data_saida_real', 'quantidade_diarias_real', 'valor_total_real', 'status'
    ]
    list_filter = ['status', 'quarto__tipo', 'data_entrada_real']
    search_fields = ['hospede__nome_completo', 'quarto__numero']
    list_editable = ['status']
    readonly_fields = [
        'quantidade_diarias_real', 'valor_total_real', 
        'data_cadastro', 'data_atualizacao'
    ]
    
    fieldsets = (
        ('Dados da Hospedagem', {
            'fields': ('reserva', 'quarto', 'hospede')
        }),
        ('Datas Reais', {
            'fields': ('data_entrada_real', 'data_saida_real')
        }),
        ('Valores Reais', {
            'fields': ('valor_diaria_real', 'quantidade_diarias_real', 'valor_total_real')
        }),
        ('Status', {
            'fields': ('status', 'motivo_cancelamento')
        }),
        ('Outras Informações', {
            'fields': ('observacoes', 'data_cadastro', 'data_atualizacao')
        }),
    )


@admin.register(ServicoAdicional)
class ServicoAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'valor', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['valor', 'ativo']


@admin.register(ServicoUtilizado)
class ServicoUtilizadoAdmin(admin.ModelAdmin):
    list_display = [
        'servico', 'hospede', 'quarto', 'quantidade', 
        'valor_unitario', 'valor_total', 'data_utilizacao'
    ]
    list_filter = ['servico__tipo', 'data_utilizacao']
    search_fields = ['servico__nome', 'hospede__nome_completo']
    readonly_fields = ['valor_total', 'data_utilizacao']
    
    def hospede(self, obj):
        return obj.hospedagem.hospede.nome_completo
    hospede.short_description = "Hóspede"
    hospede.admin_order_field = 'hospedagem__hospede__nome_completo'
    
    def quarto(self, obj):
        return obj.hospedagem.quarto.numero
    quarto.short_description = "Quarto"
    quarto.admin_order_field = 'hospedagem__quarto__numero'
