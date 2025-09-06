from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class Usuario(AbstractUser):
    """
    Modelo de usuário personalizado para autenticação por CPF
    """
    ADMINISTRADOR_SISTEMA = 'administrador_sistema'
    ASSOCIADO = 'associado'
    ADVOGADO = 'advogado'
    PSICOLOGO = 'psicologo'
    ATENDENTE_ADVOGADO = 'atendente_advogado'
    ATENDENTE_PSICOLOGO = 'atendente_psicologo'
    ATENDENTE_GERAL = 'atendente_geral'
    
    TIPO_USUARIO_CHOICES = [
        (ADMINISTRADOR_SISTEMA, 'Administrador do Sistema'),
        (ASSOCIADO, 'Associado'),
        (ADVOGADO, 'Advogado'),
        (PSICOLOGO, 'Psicólogo'),
        (ATENDENTE_ADVOGADO, 'Atendente de Advogado'),
        (ATENDENTE_PSICOLOGO, 'Atendente de Psicólogo'),
        (ATENDENTE_GERAL, 'Atendente Geral'),
    ]
    
    # Sobrescrever username para usar CPF
    username = models.CharField(
        _('CPF'),
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        help_text=_('CPF no formato XXX.XXX.XXX-XX')
    )
    
    # Campos adicionais
    tipo_usuario = models.CharField(
        max_length=25,
        choices=TIPO_USUARIO_CHOICES,
        default=ASSOCIADO,
        verbose_name=_('Tipo de Usuário')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Usuário Ativo')
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    
    ultimo_acesso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Último Acesso')
    )
    
    primeiro_acesso = models.BooleanField(
        default=True,
        verbose_name=_('Primeiro Acesso'),
        help_text=_('Indica se é o primeiro acesso do usuário (deve alterar a senha)')
    )
    
    # Campo para armazenar temporariamente a senha em texto plano (apenas para administradores)
    senha_temporaria = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Senha Temporária'),
        help_text=_('Senha em texto plano para visualização de administradores (apenas temporariamente)')
    )
    
    # Data de expiração da senha temporária
    senha_temporaria_expira = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expiração da Senha Temporária'),
        help_text=_('Data e hora em que a senha temporária expira')
    )
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def save(self, *args, **kwargs):
        # Garantir que o email seja único
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class LogAtividade(models.Model):
    """
    Modelo para registrar atividades dos usuários
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_('Usuário')
    )
    
    acao = models.CharField(
        max_length=100,
        verbose_name=_('Ação')
    )
    
    modulo = models.CharField(
        max_length=50,
        verbose_name=_('Módulo')
    )
    
    detalhes = models.TextField(
        blank=True,
        verbose_name=_('Detalhes')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Endereço IP')
    )
    
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data e Hora')
    )
    
    class Meta:
        verbose_name = _('Log de Atividade')
        verbose_name_plural = _('Logs de Atividade')
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data_hora}"


class ConfiguracaoSistema(models.Model):
    """
    Modelo para configurações do sistema
    """
    chave = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Chave')
    )
    
    valor = models.TextField(
        verbose_name=_('Valor')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data de Atualização')
    )
    
    class Meta:
        verbose_name = _('Configuração do Sistema')
        verbose_name_plural = _('Configurações do Sistema')
        ordering = ['chave']
    
    def __str__(self):
        return self.chave


class InstitucionalConfig(models.Model):
    """
    Configurações da página institucional
    """
    titulo_principal = models.CharField(max_length=200, default="ABMEPI")
    subtitulo_hero = models.TextField(default="Associação de Bombeiros e Policiais Militares - Unindo forças para proteger e servir nossa comunidade")
    
    # Seção Sobre
    titulo_sobre = models.CharField(max_length=200, default="Sobre a ABMEPI")
    texto_sobre_1 = models.TextField(default="A Associação de Bombeiros e Policiais Militares (ABMEPI) é uma entidade dedicada ao bem-estar e desenvolvimento profissional dos membros das forças de segurança pública.")
    texto_sobre_2 = models.TextField(default="Nossa missão é proporcionar suporte integral aos associados, oferecendo serviços de qualidade, assessoria jurídica especializada e uma rede de benefícios que valoriza o trabalho e dedicação desses profissionais.")
    texto_sobre_3 = models.TextField(default="Com anos de experiência e uma equipe comprometida, a ABMEPI se tornou referência em gestão associativa, sempre priorizando a excelência e a satisfação de nossos membros.")
    
    # Seção CTA
    titulo_cta = models.CharField(max_length=200, default="Pronto para se juntar a nós?")
    texto_cta = models.TextField(default="Acesse nosso sistema completo e descubra todos os benefícios disponíveis para nossos associados. Faça login agora e aproveite!")
    
    # Informações de Contato
    telefone = models.CharField(max_length=20, default="(11) 99999-9999")
    email = models.EmailField(default="contato@abmepi.org.br")
    endereco = models.CharField(max_length=200, default="São Paulo, SP")
    
    # Redes Sociais
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # Redes Sociais ASSEJUR
    assejur_facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook ASSEJUR")
    assejur_instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram ASSEJUR")
    assejur_linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn ASSEJUR")
    assejur_youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube ASSEJUR")
    assejur_twitter_url = models.URLField(blank=True, null=True, verbose_name="Twitter ASSEJUR")
    
    # Serviços Prestados aos Associados
    servicos_juridicos = models.BooleanField(default=True, verbose_name="Serviços Jurídicos")
    servicos_psicologicos = models.BooleanField(default=True, verbose_name="Serviços Psicológicos")
    servicos_medicos = models.BooleanField(default=True, verbose_name="Serviços Médicos")
    servicos_odontologicos = models.BooleanField(default=True, verbose_name="Serviços Odontológicos")
    servicos_financeiros = models.BooleanField(default=True, verbose_name="Serviços Financeiros")
    servicos_educacionais = models.BooleanField(default=True, verbose_name="Serviços Educacionais")
    servicos_recreativos = models.BooleanField(default=True, verbose_name="Serviços Recreativos")
    servicos_sociais = models.BooleanField(default=True, verbose_name="Serviços Sociais")
    servicos_esportivos = models.BooleanField(default=True, verbose_name="Serviços Esportivos")
    servicos_culturais = models.BooleanField(default=True, verbose_name="Serviços Culturais")
    servicos_hotel_transito = models.BooleanField(default=True, verbose_name="Hotel de Trânsito")
    hotel_transito_telefone = models.CharField(max_length=20, default="(11) 99999-9999", verbose_name="Telefone do Hotel de Trânsito")
    hotel_transito_imagem = models.ImageField(upload_to='hotel_transito/', blank=True, null=True, verbose_name="Imagem do Hotel de Trânsito")
    
    # Configurações de Exibição
    mostrar_estatisticas = models.BooleanField(default=True)
    mostrar_servicos = models.BooleanField(default=True)
    mostrar_sobre = models.BooleanField(default=True)
    mostrar_cta = models.BooleanField(default=True)
    
    # Meta
    meta_description = models.TextField(blank=True, help_text="Descrição para SEO")
    meta_keywords = models.CharField(max_length=500, blank=True, help_text="Palavras-chave para SEO")
    
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração Institucional"
        verbose_name_plural = "Configurações Institucionais"
    
    def __str__(self):
        return f"Configuração Institucional - {self.data_atualizacao.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Garantir que só existe uma instância
        if not self.pk and InstitucionalConfig.objects.exists():
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração atual ou cria uma nova com valores padrão"""
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'titulo_principal': 'ABMEPI',
                'subtitulo_hero': 'Associação de Bombeiros e Policiais Militares - Unindo forças para proteger e servir nossa comunidade',
                'titulo_sobre': 'Sobre a ABMEPI',
                'texto_sobre_1': 'A Associação de Bombeiros e Policiais Militares (ABMEPI) é uma entidade dedicada ao bem-estar e desenvolvimento profissional dos membros das forças de segurança pública.',
                'texto_sobre_2': 'Nossa missão é proporcionar suporte integral aos associados, oferecendo serviços de qualidade, assessoria jurídica especializada e uma rede de benefícios que valoriza o trabalho e dedicação desses profissionais.',
                'texto_sobre_3': 'Com anos de experiência e uma equipe comprometida, a ABMEPI se tornou referência em gestão associativa, sempre priorizando a excelência e a satisfação de nossos membros.',
                'titulo_cta': 'Pronto para se juntar a nós?',
                'texto_cta': 'Acesse nosso sistema completo e descubra todos os benefícios disponíveis para nossos associados. Faça login agora e aproveite!',
                'telefone': '(11) 99999-9999',
                'email': 'contato@abmepi.org.br',
                'endereco': 'São Paulo, SP',
                'assejur_facebook_url': '',
                'assejur_instagram_url': '',
                'assejur_linkedin_url': '',
                'assejur_youtube_url': '',
                'assejur_twitter_url': '',
                'servicos_juridicos': True,
                'servicos_psicologicos': True,
                'servicos_medicos': True,
                'servicos_odontologicos': True,
                'servicos_financeiros': True,
                'servicos_educacionais': True,
                'servicos_recreativos': True,
                'servicos_sociais': True,
                'servicos_esportivos': True,
                'servicos_culturais': True,
                'servicos_hotel_transito': True,
                'hotel_transito_telefone': '(11) 99999-9999',
                'hotel_transito_imagem': None,
            }
        )
        return config


class FeedPost(models.Model):
    """
    Modelo para posts do feed institucional
    """
    TIPO_POST_CHOICES = [
        ('noticia', 'Notícia'),
        ('evento', 'Evento'),
        ('treinamento', 'Treinamento'),
        ('premiacao', 'Premiação'),
        ('convenio', 'Convênio'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título do Post"
    )
    
    conteudo = models.TextField(
        verbose_name="Conteúdo do Post"
    )
    
    tipo_post = models.CharField(
        max_length=20,
        choices=TIPO_POST_CHOICES,
        default='noticia',
        verbose_name="Tipo de Post"
    )
    
    imagem = models.ImageField(
        upload_to='feed_posts/',
        blank=True,
        null=True,
        verbose_name="Imagem do Post"
    )
    
    autor = models.CharField(
        max_length=100,
        default="ABMEPI Oficial",
        verbose_name="Autor do Post"
    )
    
    likes = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Likes"
    )
    
    comentarios = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Comentários"
    )
    
    compartilhamentos = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Compartilhamentos"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Post Ativo"
    )
    
    destaque = models.BooleanField(
        default=False,
        verbose_name="Post em Destaque"
    )
    
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    data_publicacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Publicação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        verbose_name = "Post do Feed"
        verbose_name_plural = "Posts do Feed"
        ordering = ['-destaque', '-ordem_exibicao', '-data_publicacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_post_display()}"
    
    def get_tempo_relativo(self):
        """Retorna o tempo relativo desde a publicação"""
        from django.utils import timezone
        from datetime import timedelta
        
        agora = timezone.now()
        diferenca = agora - self.data_publicacao
        
        if diferenca.days > 0:
            if diferenca.days == 1:
                return "Há 1 dia"
            elif diferenca.days < 7:
                return f"Há {diferenca.days} dias"
            else:
                semanas = diferenca.days // 7
                if semanas == 1:
                    return "Há 1 semana"
                else:
                    return f"Há {semanas} semanas"
        elif diferenca.seconds >= 3600:
            horas = diferenca.seconds // 3600
            if horas == 1:
                return "Há 1 hora"
            else:
                return f"Há {horas} horas"
        elif diferenca.seconds >= 60:
            minutos = diferenca.seconds // 60
            if minutos == 1:
                return "Há 1 minuto"
            else:
                return f"Há {minutos} minutos"
        else:
            return "Agora mesmo"
    
    def get_likes_count(self):
        """Retorna a contagem real de likes (autenticados + anônimos)"""
        likes_autenticados = self.like_set.count()
        likes_anonimos = self.likeanonimo_set.count()
        return likes_autenticados + likes_anonimos
    
    def get_comentarios_count(self):
        """Retorna a contagem real de comentários ativos"""
        return self.comentario_set.filter(ativo=True).count()
    
    def user_liked(self, user):
        """Verifica se o usuário curtiu este post"""
        if user.is_authenticated:
            return self.like_set.filter(usuario=user).exists()
        return False
    
    def sync_counters(self):
        """Sincroniza os contadores com os dados reais do banco"""
        # Atualizar contador de likes (autenticados + anônimos)
        likes_count = self.get_likes_count()
        
        # Atualizar contador de comentários (apenas ativos)
        comments_count = self.comentario_set.filter(ativo=True).count()
        
        # Atualizar os campos
        self.likes = likes_count
        self.comentarios = comments_count
        self.save(update_fields=['likes', 'comentarios'])
        
        return {
            'likes': likes_count,
            'comentarios': comments_count
        }
    
    def get_total_likes_count(self, session_likes=None):
        """Retorna o total de likes (já inclui anônimos do banco)"""
        return self.get_likes_count()


class Like(models.Model):
    """
    Modelo para likes dos posts do feed
    """
    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        verbose_name="Post"
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ('post', 'usuario')  # Um usuário só pode curtir um post uma vez
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} curtiu {self.post.titulo}"


class LikeAnonimo(models.Model):
    """
    Modelo para likes anônimos dos posts do feed (usando sessão)
    """
    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        verbose_name="Post"
    )
    
    session_key = models.CharField(
        max_length=40,
        verbose_name="Chave da Sessão"
    )
    
    nome_anonimo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Nome do Usuário Anônimo"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    class Meta:
        verbose_name = "Like Anônimo"
        verbose_name_plural = "Likes Anônimos"
        unique_together = ('post', 'session_key')  # Uma sessão só pode curtir um post uma vez
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Like anônimo em {self.post.titulo} (Sessão: {self.session_key})"


class Comentario(models.Model):
    """
    Modelo para comentários dos posts do feed
    """
    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        verbose_name="Post"
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    
    nome_anonimo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Nome do Usuário Anônimo"
    )
    
    conteudo = models.TextField(
        verbose_name="Comentário"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Comentário Ativo"
    )
    
    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['data_criacao']
    
    def __str__(self):
        if self.usuario:
            return f"{self.usuario.username} comentou em {self.post.titulo}"
        else:
            return f"{self.nome_anonimo or 'Anônimo'} comentou em {self.post.titulo}"
    
    def get_author_name(self):
        """Retorna o nome do autor do comentário"""
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        else:
            return self.nome_anonimo or 'Visitante'
    
    def get_tempo_relativo(self):
        """Retorna o tempo relativo desde a criação do comentário"""
        from django.utils import timezone
        from datetime import timedelta
        
        agora = timezone.now()
        diferenca = agora - self.data_criacao
        
        if diferenca.days > 0:
            if diferenca.days == 1:
                return "há 1 dia"
            elif diferenca.days < 7:
                return f"há {diferenca.days} dias"
            else:
                semanas = diferenca.days // 7
                if semanas == 1:
                    return "há 1 semana"
                else:
                    return f"há {semanas} semanas"
        elif diferenca.seconds >= 3600:
            horas = diferenca.seconds // 3600
            if horas == 1:
                return "há 1 hora"
            else:
                return f"há {horas} horas"
        elif diferenca.seconds >= 60:
            minutos = diferenca.seconds // 60
            if minutos == 1:
                return "há 1 minuto"
            else:
                return f"há {minutos} minutos"
        else:
            return "agora mesmo"


class AssejurNews(models.Model):
    """
    Modelo para notícias da Assessoria Jurídica (ASSEJUR)
    """
    CATEGORIA_CHOICES = [
        ('direito_previdenciario', 'Direito Previdenciário'),
        ('direito_administrativo', 'Direito Administrativo'),
        ('direito_militar', 'Direito Militar'),
        ('direito_civil', 'Direito Civil'),
        ('direito_penal', 'Direito Penal'),
        ('direito_trabalhista', 'Direito Trabalhista'),
        ('direito_constitucional', 'Direito Constitucional'),
        ('direito_tributario', 'Direito Tributário'),
    ]
    
    ICONE_CHOICES = [
        ('fas fa-gavel', '🔨 Gavel (Direito)'),
        ('fas fa-balance-scale', '⚖️ Balança (Justiça)'),
        ('fas fa-shield-alt', '🛡️ Escudo (Militar)'),
        ('fas fa-user-tie', '👔 Usuário (Civil)'),
        ('fas fa-briefcase', '💼 Pasta (Trabalhista)'),
        ('fas fa-book', '📚 Livro (Constitucional)'),
        ('fas fa-calculator', '🧮 Calculadora (Tributário)'),
        ('fas fa-university', '🏛️ Universidade (Institucional)'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título da Notícia"
    )
    
    resumo = models.TextField(
        max_length=500,
        verbose_name="Resumo da Notícia"
    )
    
    conteudo = models.TextField(
        verbose_name="Conteúdo Completo",
        blank=True
    )
    
    categoria = models.CharField(
        max_length=30,
        choices=CATEGORIA_CHOICES,
        default='direito_previdenciario',
        verbose_name="Categoria"
    )
    
    icone = models.CharField(
        max_length=30,
        choices=ICONE_CHOICES,
        default='fas fa-gavel',
        verbose_name="Ícone"
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media',
        verbose_name="Prioridade"
    )
    
    link_externo = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link Externo (Ler mais)"
    )
    
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tags (separadas por vírgula)"
    )
    
    imagem = models.ImageField(
        upload_to='noticias_juridicas/',
        blank=True,
        null=True,
        verbose_name="Imagem da Notícia"
    )
    
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Autor"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Notícia Ativa"
    )
    
    destaque = models.BooleanField(
        default=False,
        verbose_name="Destacar no Carrossel"
    )
    
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    data_publicacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Publicação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    visualizacoes = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Visualizações"
    )
    
    imagem = models.ImageField(
        upload_to='assejur_news/',
        blank=True,
        null=True,
        verbose_name="Imagem da Notícia"
    )
    
    imagem_legenda = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Legenda da Imagem"
    )
    
    class Meta:
        verbose_name = "Notícia ASSEJUR"
        verbose_name_plural = "Notícias ASSEJUR"
        ordering = ['-destaque', '-ordem_exibicao', '-data_publicacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_categoria_display()}"
    
    def get_categoria_display_friendly(self):
        """Retorna o nome da categoria de forma amigável"""
        return dict(self.CATEGORIA_CHOICES).get(self.categoria, self.categoria)
    
    def get_prioridade_color(self):
        """Retorna a cor baseada na prioridade"""
        cores = {
            'baixa': 'info',
            'media': 'warning', 
            'alta': 'danger',
            'urgente': 'dark'
        }
        return cores.get(self.prioridade, 'secondary')
    
    def get_tempo_relativo(self):
        """Retorna o tempo relativo desde a publicação"""
        from django.utils import timezone
        
        agora = timezone.now()
        diferenca = agora - self.data_publicacao
        
        if diferenca.days > 0:
            if diferenca.days == 1:
                return "Há 1 dia"
            elif diferenca.days < 7:
                return f"Há {diferenca.days} dias"
            else:
                semanas = diferenca.days // 7
                if semanas == 1:
                    return "Há 1 semana"
                else:
                    return f"Há {semanas} semanas"
        elif diferenca.seconds >= 3600:
            horas = diferenca.seconds // 3600
            if horas == 1:
                return "Há 1 hora"
            else:
                return f"Há {horas} horas"
        elif diferenca.seconds >= 60:
            minutos = diferenca.seconds // 60
            if minutos == 1:
                return "Há 1 minuto"
            else:
                return f"Há {minutos} minutos"
        else:
            return "Agora mesmo"
    
    def get_comentarios_count(self):
        """Retorna o número total de comentários ativos"""
        return self.comentarios.filter(ativo=True).count()
    
    def get_comentarios_ativos(self):
        """Retorna os comentários ativos da notícia"""
        return self.comentarios.filter(ativo=True).select_related('usuario').order_by('data_criacao')
    
    def incrementar_visualizacoes(self):
        """Incrementa o contador de visualizações"""
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])


class AssejurInformativo(models.Model):
    """
    Modelo para informativos da Assessoria Jurídica
    """
    ICONE_CHOICES = [
        ('fas fa-exclamation-triangle', '⚠️ Triângulo (Alerta)'),
        ('fas fa-clock', '🕐 Relógio (Horário)'),
        ('fas fa-phone', '📞 Telefone (Contato)'),
        ('fas fa-envelope', '✉️ Envelope (Email)'),
        ('fas fa-map-marker-alt', '📍 Marcador (Localização)'),
        ('fas fa-calendar', '📅 Calendário (Data)'),
        ('fas fa-info-circle', 'ℹ️ Informação'),
        ('fas fa-bullhorn', '📢 Megafone (Anúncio)'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título do Informativo"
    )
    
    conteudo = models.TextField(
        verbose_name="Conteúdo do Informativo"
    )
    
    icone = models.CharField(
        max_length=30,
        choices=ICONE_CHOICES,
        default='fas fa-info-circle',
        verbose_name="Ícone"
    )
    
    cor_icone = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name="Cor do Ícone (HEX)"
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media',
        verbose_name="Prioridade"
    )
    
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Autor"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Informativo Ativo"
    )
    
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        verbose_name = "Informativo ASSEJUR"
        verbose_name_plural = "Informativos ASSEJUR"
        ordering = ['-ordem_exibicao', '-data_criacao']
    
    def __str__(self):
        return self.titulo
    
    def get_prioridade_color(self):
        """Retorna a cor baseada na prioridade"""
        cores = {
            'baixa': 'info',
            'media': 'warning',
            'alta': 'danger', 
            'urgente': 'dark'
        }
        return cores.get(self.prioridade, 'secondary')


class AssejurNewsComentario(models.Model):
    """
    Modelo para comentários das notícias da Assessoria Jurídica
    """
    noticia = models.ForeignKey(
        AssejurNews,
        on_delete=models.CASCADE,
        verbose_name="Notícia",
        related_name='comentarios'
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    
    nome_anonimo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Nome do Usuário Anônimo"
    )
    
    conteudo = models.TextField(
        verbose_name="Comentário"
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Comentário Ativo"
    )
    
    class Meta:
        verbose_name = "Comentário de Notícia ASSEJUR"
        verbose_name_plural = "Comentários de Notícias ASSEJUR"
        ordering = ['data_criacao']
    
    def __str__(self):
        if self.usuario:
            return f"{self.usuario.username} comentou em {self.noticia.titulo}"
        else:
            return f"{self.nome_anonimo or 'Anônimo'} comentou em {self.noticia.titulo}"
    
    def get_author_name(self):
        """Retorna o nome do autor do comentário"""
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        else:
            return self.nome_anonimo or 'Visitante'
    
    def get_tempo_relativo(self):
        """Retorna o tempo relativo desde a criação do comentário"""
        from django.utils import timezone
        from datetime import timedelta
        
        agora = timezone.now()
        diferenca = agora - self.data_criacao
        
        if diferenca.days > 0:
            if diferenca.days == 1:
                return "há 1 dia"
            elif diferenca.days < 7:
                return f"há {diferenca.days} dias"
            else:
                semanas = diferenca.days // 7
                if semanas == 1:
                    return "há 1 semana"
                else:
                    return f"há {semanas} semanas"
        elif diferenca.seconds >= 3600:
            horas = diferenca.seconds // 3600
            if horas == 1:
                return "há 1 hora"
            else:
                return f"há {horas} horas"
        elif diferenca.seconds >= 60:
            minutos = diferenca.seconds // 60
            if minutos == 1:
                return "há 1 minuto"
            else:
                return f"há {minutos} minutos"
        else:
            return "agora mesmo"


class ConfiguracaoCobranca(models.Model):
    """
    Configurações para cobrança e carnê de pagamento
    """
    nome = models.CharField(max_length=100, help_text="Nome da configuração (ex: Configuração Padrão)")
    ativo = models.BooleanField(default=True, help_text="Configuração ativa para uso")
    
    # Dados de cobrança
    chave_pix = models.CharField(max_length=100, help_text="Chave PIX para pagamento")
    titular = models.CharField(max_length=100, help_text="Nome do titular da conta")
    banco = models.CharField(max_length=100, help_text="Nome do banco ou instituição")
    
    # Mensagem personalizada
    mensagem_linha1 = models.CharField(max_length=100, default="Pague Suas mensalidade na sede da", help_text="Primeira linha da mensagem")
    mensagem_linha2 = models.CharField(max_length=100, default="associação ou pelo QRcode e mande o", help_text="Segunda linha da mensagem")
    mensagem_linha3 = models.CharField(max_length=100, default="comprovante para", help_text="Terceira linha da mensagem")
    telefone_comprovante = models.CharField(max_length=20, default="86 988197790", help_text="Telefone para envio do comprovante")
    
    # Configurações do QR Code
    qr_code_ativo = models.BooleanField(default=True, help_text="Exibir QR Code no carnê")
    qr_code_tamanho = models.IntegerField(default=15, help_text="Tamanho do QR Code em mm")
    
    # Configurações gerais
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Cobrança"
        verbose_name_plural = "Configurações de Cobrança"
        ordering = ['-ativo', '-data_criacao']
    
    def __str__(self):
        return f"{self.nome} {'(Ativo)' if self.ativo else '(Inativo)'}"
    
    def get_mensagem_completa(self):
        """Retorna a mensagem completa formatada"""
        return f"{self.mensagem_linha1}\n{self.mensagem_linha2}\n{self.mensagem_linha3} {self.telefone_comprovante}"
    
    def get_configuracao_ativa(self):
        """Retorna a configuração ativa ou cria uma padrão"""
        config = ConfiguracaoCobranca.objects.filter(ativo=True).first()
        if not config:
            # Criar configuração padrão se não existir
            config = ConfiguracaoCobranca.objects.create(
                nome="Configuração Padrão",
                ativo=True,
                chave_pix="86 988197790",
                titular="Gustavo Henrique de Araujo Sousa",
                banco="MERCADO PAGO"
            )
        return config


class Notificacao(models.Model):
    """
    Modelo para notificações do sistema
    """
    TIPO_CHOICES = [
        ('reserva_hotel', 'Reserva de Hotel'),
        ('mensalidade_vencida', 'Mensalidade Vencida'),
        ('atendimento_juridico', 'Atendimento Jurídico'),
        ('atendimento_psicologico', 'Atendimento Psicológico'),
        ('sistema', 'Sistema'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('lida', 'Lida'),
        ('resolvida', 'Resolvida'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Dados da notificação
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    
    # Usuários relacionados
    usuario_destino = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificacoes_recebidas',
        verbose_name="Usuário Destino"
    )
    usuario_origem = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notificacoes_enviadas',
        verbose_name="Usuário Origem"
    )
    
    # Dados relacionados (opcional)
    objeto_tipo = models.CharField(max_length=50, blank=True, verbose_name="Tipo do Objeto")
    objeto_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID do Objeto")
    url_acao = models.URLField(blank=True, verbose_name="URL de Ação")
    
    # Controle de tempo
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    
    # Prioridade
    prioridade = models.PositiveIntegerField(default=1, verbose_name="Prioridade")  # 1=baixa, 2=média, 3=alta
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-prioridade', '-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario_destino.get_full_name()}"
    
    def marcar_como_lida(self):
        """Marcar notificação como lida"""
        if self.status == 'pendente':
            from django.utils import timezone
            self.status = 'lida'
            self.data_leitura = timezone.now()
            self.save()
    
    def marcar_como_resolvida(self):
        """Marcar notificação como resolvida"""
        from django.utils import timezone
        self.status = 'resolvida'
        self.data_resolucao = timezone.now()
        self.save()
    
    @classmethod
    def criar_notificacao_reserva_hotel(cls, reserva, usuario_destino):
        """Criar notificação para reserva de hotel"""
        return cls.objects.create(
            titulo=f"Nova Reserva de Hotel - {reserva.codigo_reserva}",
            mensagem=f"O associado {reserva.hospede.nome_completo} fez uma reserva no quarto {reserva.quarto.numero} para o período de {reserva.data_entrada} a {reserva.data_saida}.",
            tipo='reserva_hotel',
            usuario_destino=usuario_destino,
            objeto_tipo='Reserva',
            objeto_id=reserva.id,
            url_acao=f"/hotel-transito/reservas/{reserva.id}/",
            prioridade=2
        )


class ExPresidente(models.Model):
    """
    Modelo para armazenar informações dos ex-presidentes da ABMEPI
    """
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    posto_graduacao = models.CharField(max_length=100, blank=True, verbose_name="Posto/Graduação")
    foto = models.ImageField(
        upload_to='ex_presidentes/',
        null=True,
        blank=True,
        verbose_name="Foto"
    )
    periodo_inicio = models.DateField(verbose_name="Início do Mandato")
    periodo_fim = models.DateField(verbose_name="Fim do Mandato")
    biografia = models.TextField(blank=True, verbose_name="Biografia")
    principais_realizacoes = models.TextField(blank=True, verbose_name="Principais Realizações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem_exibicao = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    
    # Controle de tempo
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Ex-Presidente"
        verbose_name_plural = "Ex-Presidentes"
        ordering = ['ordem_exibicao', 'periodo_inicio']
    
    def __str__(self):
        return f"{self.nome} ({self.periodo_inicio.year}-{self.periodo_fim.year})"
    
    @property
    def periodo_completo(self):
        """Retorna o período formatado"""
        return f"{self.periodo_inicio.strftime('%Y')} - {self.periodo_fim.strftime('%Y')}"


class HistoriaAssociacao(models.Model):
    """
    Modelo para armazenar marcos históricos da ABMEPI
    """
    TIPO_CHOICES = [
        ('fundacao', 'Fundação'),
        ('conquista', 'Conquista'),
        ('evento', 'Evento Importante'),
        ('reconhecimento', 'Reconhecimento'),
        ('expansao', 'Expansão'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    data_marcante = models.DateField(verbose_name="Data Marcante")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='evento',
        verbose_name="Tipo"
    )
    imagem = models.ImageField(
        upload_to='historia/',
        null=True,
        blank=True,
        verbose_name="Imagem Principal"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    destaque = models.BooleanField(default=False, verbose_name="Destaque")
    ordem_exibicao = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    
    # Controle de tempo
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Marco Histórico"
        verbose_name_plural = "História da Associação"
        ordering = ['ordem_exibicao', 'data_marcante']
    
    def __str__(self):
        return f"{self.titulo} ({self.data_marcante.year})"
    
    @property
    def ano(self):
        """Retorna apenas o ano da data marcante"""
        return self.data_marcante.year


class HistoriaImagem(models.Model):
    """
    Modelo para imagens da galeria de cada evento histórico
    """
    evento = models.ForeignKey(
        HistoriaAssociacao,
        on_delete=models.CASCADE,
        related_name='galeria_imagens',
        verbose_name="Evento Histórico"
    )
    
    imagem = models.ImageField(
        upload_to='historia/galeria/',
        verbose_name="Imagem"
    )
    
    legenda = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Legenda da Imagem"
    )
    
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    # Controle de tempo
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    class Meta:
        verbose_name = "Imagem da História"
        verbose_name_plural = "Imagens da História"
        ordering = ['evento', 'ordem_exibicao', 'created_at']
    
    def __str__(self):
        return f"{self.evento.titulo} - {self.legenda or 'Imagem'}"