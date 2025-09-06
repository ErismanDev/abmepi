from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Evento, ParticipanteEvento, Comunicado, ListaPresenca, Presenca


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'status', 'data_inicio', 'local', 'participantes_count', 'vagas_disponiveis', 'ativo')
    list_filter = ('tipo', 'status', 'ativo', 'data_inicio')
    search_fields = ('titulo', 'local', 'responsavel')
    list_per_page = 25
    ordering = ('-data_inicio',)
    
    fieldsets = (
        ('Informações do Evento', {
            'fields': ('titulo', 'descricao', 'tipo', 'status')
        }),
        ('Data e Local', {
            'fields': ('data_inicio', 'data_fim', 'local', 'endereco')
        }),
        ('Capacidade e Inscrição', {
            'fields': ('capacidade_maxima', 'valor_inscricao')
        }),
        ('Responsáveis', {
            'fields': ('responsavel', 'usuario_responsavel')
        }),
        ('Mídia', {
            'fields': ('imagem', 'arquivos_anexados')
        }),
        ('Controle', {
            'fields': ('ativo', 'observacoes')
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def participantes_count(self, obj):
        return obj.get_participantes_count()
    participantes_count.short_description = 'Participantes'
    
    def vagas_disponiveis(self, obj):
        vagas = obj.get_vagas_disponiveis()
        if vagas is not None:
            if vagas == 0:
                return format_html('<span style="color: red; font-weight: bold;">Lotado</span>')
            elif vagas <= 5:
                return format_html('<span style="color: orange; font-weight: bold;">{} vagas</span>', vagas)
            else:
                return f"{vagas} vagas"
        return "Ilimitado"
    vagas_disponiveis.short_description = 'Vagas Disponíveis'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario_responsavel')
    
    actions = ['ativar_eventos', 'desativar_eventos']
    
    def ativar_eventos(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} evento(s) ativado(s) com sucesso.')
    ativar_eventos.short_description = "Ativar eventos selecionados"
    
    def desativar_eventos(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} evento(s) desativado(s) com sucesso.')
    desativar_eventos.short_description = "Desativar eventos selecionados"


@admin.register(ParticipanteEvento)
class ParticipanteEventoAdmin(admin.ModelAdmin):
    list_display = ('associado', 'evento', 'status', 'data_inscricao', 'data_confirmacao', 'data_presenca')
    list_filter = ('status', 'data_inscricao', 'evento__tipo')
    search_fields = ('associado__nome', 'associado__cpf', 'evento__titulo')
    list_per_page = 25
    ordering = ('-data_inscricao',)
    
    fieldsets = (
        ('Participação', {
            'fields': ('associado', 'evento', 'status')
        }),
        ('Datas', {
            'fields': ('data_confirmacao', 'data_presenca')
        }),
        ('Outros', {
            'fields': ('observacoes',)
        }),
    )
    
    readonly_fields = ('data_inscricao',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado', 'evento')
    
    actions = ['confirmar_participantes', 'marcar_presenca']
    
    def confirmar_participantes(self, request, queryset):
        updated = queryset.update(
            status='confirmado',
            data_confirmacao=timezone.now()
        )
        self.message_user(request, f'{updated} participante(s) confirmado(s) com sucesso.')
    confirmar_participantes.short_description = "Confirmar participantes"
    
    def marcar_presenca(self, request, queryset):
        updated = queryset.update(
            status='presente',
            data_presenca=timezone.now()
        )
        self.message_user(request, f'{updated} participante(s) marcado(s) como presente(s).')
    marcar_presenca.short_description = "Marcar presença"


@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'prioridade', 'data_publicacao', 'autor', 'enviar_email', 'enviar_sms', 'ativo')
    list_filter = ('tipo', 'prioridade', 'ativo', 'data_publicacao')
    search_fields = ('titulo', 'conteudo', 'autor__username')
    list_per_page = 25
    ordering = ('-data_publicacao',)
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('titulo', 'conteudo', 'tipo', 'prioridade')
        }),
        ('Publicação', {
            'fields': ('data_expiracao', 'autor')
        }),
        ('Destinatários', {
            'fields': ('tipo_destinatarios', 'associados_especificos', 'advogados_especificos', 'destinatarios')
        }),
        ('Notificações', {
            'fields': ('enviar_email', 'enviar_sms')
        }),
        ('Mídia', {
            'fields': ('arquivos_anexados',)
        }),
        ('Controle', {
            'fields': ('ativo',)
        }),
    )
    
    readonly_fields = ('data_publicacao',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('autor')
    
    actions = ['ativar_comunicados', 'desativar_comunicados']
    
    def ativar_comunicados(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} comunicado(s) ativado(s) com sucesso.')
    ativar_comunicados.short_description = "Ativar comunicados selecionados"
    
    def desativar_comunicados(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} comunicado(s) desativado(s) com sucesso.')
    desativar_comunicados.short_description = "Desativar comunicados selecionados"


@admin.register(ListaPresenca)
class ListaPresencaAdmin(admin.ModelAdmin):
    list_display = ('evento', 'data_registro', 'usuario_registro', 'presentes_count', 'ausentes_count')
    list_filter = ('data_registro', 'evento__tipo')
    search_fields = ('evento__titulo', 'usuario_registro__username')
    list_per_page = 25
    ordering = ('-data_registro',)
    
    fieldsets = (
        ('Informações', {
            'fields': ('evento', 'observacoes')
        }),
        ('Sistema', {
            'fields': ('usuario_registro',)
        }),
    )
    
    readonly_fields = ('data_registro',)
    
    def presentes_count(self, obj):
        return obj.get_presentes_count()
    presentes_count.short_description = 'Presentes'
    
    def ausentes_count(self, obj):
        return obj.get_ausentes_count()
    ausentes_count.short_description = 'Ausentes'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('evento', 'usuario_registro')


@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('associado', 'evento', 'presente', 'horario_chegada', 'horario_saida')
    list_filter = ('presente', 'lista_presenca__evento__tipo')
    search_fields = ('associado__nome', 'associado__cpf', 'lista_presenca__evento__titulo')
    list_per_page = 25
    ordering = ('associado__nome',)
    
    fieldsets = (
        ('Presença', {
            'fields': ('lista_presenca', 'associado', 'presente')
        }),
        ('Horários', {
            'fields': ('horario_chegada', 'horario_saida')
        }),
        ('Outros', {
            'fields': ('observacoes',)
        }),
    )
    
    def evento(self, obj):
        return obj.lista_presenca.evento.titulo
    evento.short_description = 'Evento'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('associado', 'lista_presenca__evento')
    
    actions = ['marcar_presente', 'marcar_ausente']
    
    def marcar_presente(self, request, queryset):
        updated = queryset.update(presente=True)
        self.message_user(request, f'{updated} participante(s) marcado(s) como presente(s).')
    marcar_presente.short_description = "Marcar como presente"
    
    def marcar_ausente(self, request, queryset):
        updated = queryset.update(presente=False)
        self.message_user(request, f'{updated} participante(s) marcado(s) como ausente(s).')
    marcar_ausente.short_description = "Marcar como ausente"
