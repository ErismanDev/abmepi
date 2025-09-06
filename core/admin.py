from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario, LogAtividade, ConfiguracaoSistema, InstitucionalConfig, FeedPost, Like, Comentario, AssejurNewsComentario, ExPresidente, HistoriaAssociacao, HistoriaImagem
from .forms import UsuarioCreationForm, UsuarioChangeForm


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'ativo', 'is_staff')
    list_filter = ('tipo_usuario', 'ativo', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissões'), {
            'fields': ('tipo_usuario', 'ativo', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'tipo_usuario'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(LogAtividade)
class LogAtividadeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'modulo', 'ip_address', 'data_hora')
    list_filter = ('modulo', 'data_hora', 'usuario')
    search_fields = ('usuario__username', 'acao', 'modulo', 'detalhes')
    readonly_fields = ('usuario', 'acao', 'modulo', 'detalhes', 'ip_address', 'data_hora')
    ordering = ('-data_hora',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'ativo', 'data_criacao', 'data_atualizacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('chave', 'descricao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    ordering = ('chave',)


@admin.register(InstitucionalConfig)
class InstitucionalConfigAdmin(admin.ModelAdmin):
    """
    Admin para configurações da página institucional
    """
    list_display = ['titulo_principal', 'data_atualizacao']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Configurações Gerais', {
            'fields': ('titulo_principal', 'subtitulo_hero')
        }),
        ('Seção Sobre', {
            'fields': ('titulo_sobre', 'texto_sobre_1', 'texto_sobre_2', 'texto_sobre_3')
        }),
        ('Seção Call-to-Action', {
            'fields': ('titulo_cta', 'texto_cta')
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'email', 'endereco')
        }),
        ('Redes Sociais', {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Configurações de Exibição', {
            'fields': ('mostrar_estatisticas', 'mostrar_servicos', 'mostrar_sobre', 'mostrar_cta')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Permitir apenas uma instância"""
        return not InstitucionalConfig.objects.exists()


@admin.register(AssejurNewsComentario)
class AssejurNewsComentarioAdmin(admin.ModelAdmin):
    """
    Admin para comentários das notícias ASSEJUR
    """
    list_display = ('noticia', 'get_author_name', 'conteudo', 'data_criacao', 'ativo')
    list_filter = ('ativo', 'data_criacao', 'noticia__categoria')
    search_fields = ('conteudo', 'nome_anonimo', 'usuario__username', 'noticia__titulo')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    ordering = ('-data_criacao',)
    
    fieldsets = (
        ('Informações do Comentário', {
            'fields': ('noticia', 'conteudo', 'ativo')
        }),
        ('Autor', {
            'fields': ('usuario', 'nome_anonimo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    get_author_name.short_description = 'Autor'
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Não permitir exclusão"""
        return False


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    """
    Admin para posts do feed institucional
    """
    list_display = ['titulo', 'tipo_post', 'autor', 'ativo', 'destaque', 'ordem_exibicao', 'data_publicacao']
    list_filter = ['tipo_post', 'ativo', 'destaque', 'data_publicacao']
    search_fields = ['titulo', 'conteudo', 'autor']
    list_editable = ['ativo', 'destaque', 'ordem_exibicao']
    ordering = ['-destaque', '-ordem_exibicao', '-data_publicacao']
    readonly_fields = ['data_publicacao', 'data_atualizacao', 'likes', 'comentarios', 'compartilhamentos']
    
    fieldsets = (
        ('Informações do Post', {
            'fields': ('titulo', 'conteudo', 'tipo_post', 'autor')
        }),
        ('Mídia', {
            'fields': ('imagem',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'destaque', 'ordem_exibicao')
        }),
        ('Estatísticas', {
            'fields': ('likes', 'comentarios', 'compartilhamentos'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_publicacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo post
            obj.likes = 0
            obj.comentarios = 0
            obj.compartilhamentos = 0
        super().save_model(request, obj, form, change)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin para likes dos posts do feed
    """
    list_display = ['post', 'usuario', 'data_criacao']
    list_filter = ['data_criacao', 'post']
    search_fields = ['post__titulo', 'usuario__username', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['data_criacao']
    ordering = ['-data_criacao']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'usuario')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """
    Admin para comentários dos posts do feed
    """
    list_display = ['post', 'usuario', 'conteudo_resumido', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'data_criacao', 'post']
    search_fields = ['post__titulo', 'usuario__username', 'usuario__first_name', 'usuario__last_name', 'conteudo']
    list_editable = ['ativo']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações do Comentário', {
            'fields': ('post', 'usuario', 'conteudo')
        }),
        ('Configurações', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def conteudo_resumido(self, obj):
        """Retorna uma versão resumida do conteúdo para a lista"""
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_resumido.short_description = 'Comentário'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'usuario')


@admin.register(ExPresidente)
class ExPresidenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'posto_graduacao', 'periodo_completo', 'ativo', 'ordem_exibicao')
    list_filter = ('ativo', 'periodo_inicio', 'periodo_fim')
    search_fields = ('nome', 'posto_graduacao', 'biografia')
    ordering = ('ordem_exibicao', 'periodo_inicio')
    list_editable = ('ativo', 'ordem_exibicao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'posto_graduacao', 'foto')
        }),
        ('Período de Mandato', {
            'fields': ('periodo_inicio', 'periodo_fim')
        }),
        ('Biografia e Realizações', {
            'fields': ('biografia', 'principais_realizacoes'),
            'classes': ('wide',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'ordem_exibicao')
        })
    )
    
    def periodo_completo(self, obj):
        return obj.periodo_completo
    periodo_completo.short_description = 'Período'


class HistoriaImagemInline(admin.TabularInline):
    model = HistoriaImagem
    extra = 1
    fields = ('imagem', 'legenda', 'ordem_exibicao', 'ativo')
    ordering = ('ordem_exibicao', 'created_at')


@admin.register(HistoriaAssociacao)
class HistoriaAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'ano', 'destaque', 'ativo', 'ordem_exibicao', 'imagens_count')
    list_filter = ('tipo', 'ativo', 'destaque', 'data_marcante')
    search_fields = ('titulo', 'descricao')
    ordering = ('ordem_exibicao', 'data_marcante')
    list_editable = ('destaque', 'ativo', 'ordem_exibicao')
    inlines = [HistoriaImagemInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'tipo', 'data_marcante', 'imagem')
        }),
        ('Conteúdo', {
            'fields': ('descricao',),
            'classes': ('wide',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'destaque', 'ordem_exibicao')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related('galeria_imagens')
    
    def ano(self, obj):
        return obj.ano
    ano.short_description = 'Ano'
    
    def imagens_count(self, obj):
        return obj.galeria_imagens.filter(ativo=True).count()
    imagens_count.short_description = 'Imagens na Galeria'


@admin.register(HistoriaImagem)
class HistoriaImagemAdmin(admin.ModelAdmin):
    list_display = ('evento', 'imagem_preview', 'legenda', 'ordem_exibicao', 'ativo', 'created_at')
    list_filter = ('ativo', 'evento', 'created_at')
    search_fields = ('evento__titulo', 'legenda')
    ordering = ('evento', 'ordem_exibicao', 'created_at')
    list_editable = ('ativo', 'ordem_exibicao')
    
    fieldsets = (
        ('Informações da Imagem', {
            'fields': ('evento', 'imagem', 'legenda')
        }),
        ('Configurações', {
            'fields': ('ativo', 'ordem_exibicao')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('evento')
    
    def imagem_preview(self, obj):
        if obj.imagem:
            return f'<img src="{obj.imagem.url}" style="max-width: 50px; max-height: 50px; object-fit: cover;">'
        return 'Sem imagem'
    imagem_preview.allow_tags = True
    imagem_preview.short_description = 'Preview'
