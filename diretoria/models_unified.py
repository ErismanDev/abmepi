from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class ModeloAtaUnificado(models.Model):
    """
    Modelo unificado para templates de atas de reunião
    """
    CATEGORIA_CHOICES = [
        ('geral', 'Geral'),
        ('ordinaria', 'Reunião Ordinária'),
        ('extraordinaria', 'Reunião Extraordinária'),
        ('emergencia', 'Emergência'),
        ('assembleia', 'Assembleia'),
        ('conselho', 'Conselho'),
        ('comissao', 'Comissão'),
    ]
    
    TIPO_CONTEUDO_CHOICES = [
        ('texto', 'Texto Simples'),
        ('html', 'HTML'),
        ('template', 'Template Django'),
    ]
    
    # Informações básicas
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome do Modelo'),
        help_text=_('Nome identificador do modelo')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição do Modelo'),
        help_text=_('Descrição detalhada do modelo')
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='geral',
        verbose_name=_('Categoria')
    )
    
    # Conteúdo do modelo
    tipo_conteudo = models.CharField(
        max_length=10,
        choices=TIPO_CONTEUDO_CHOICES,
        default='texto',
        verbose_name=_('Tipo de Conteúdo')
    )
    
    conteudo = models.TextField(
        verbose_name=_('Conteúdo do Modelo'),
        help_text=_('Conteúdo principal do modelo')
    )
    
    conteudo_html = models.TextField(
        blank=True,
        verbose_name=_('Conteúdo HTML'),
        help_text=_('Versão HTML do conteúdo (se aplicável)')
    )
    
    # Metadados
    titulo_original = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Título da Ata Original'),
        help_text=_('Título da ata que originou este modelo')
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Tags'),
        help_text=_('Tags separadas por vírgula para facilitar a busca')
    )
    
    # Configurações de visibilidade
    publico = models.BooleanField(
        default=False,
        verbose_name=_('Modelo Público'),
        help_text=_('Se marcado, outros usuários podem usar este modelo')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Modelo Ativo'),
        help_text=_('Se desmarcado, o modelo não aparecerá nas listagens')
    )
    
    # Estatísticas
    vezes_usado = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Vezes Usado'),
        help_text=_('Quantas vezes este modelo foi utilizado')
    )
    
    # Auditoria
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='modelos_ata_criados',
        verbose_name=_('Criado por')
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data de Atualização')
    )
    
    # Última vez que foi usado
    ultimo_uso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Último Uso')
    )
    
    class Meta:
        ordering = ['-data_atualizacao', 'nome']
        verbose_name = _('Modelo de Ata')
        verbose_name_plural = _('Modelos de Ata')
        indexes = [
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['publico', 'ativo']),
            models.Index(fields=['criado_por', 'ativo']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"
    
    def incrementar_uso(self):
        """Incrementa o contador de uso do modelo"""
        from django.utils import timezone
        self.vezes_usado += 1
        self.ultimo_uso = timezone.now()
        self.save(update_fields=['vezes_usado', 'ultimo_uso'])
    
    def get_tags_list(self):
        """Retorna as tags como uma lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Define as tags a partir de uma lista"""
        self.tags = ', '.join(tags_list)
    
    def get_conteudo_final(self):
        """Retorna o conteúdo apropriado baseado no tipo"""
        if self.tipo_conteudo == 'html' and self.conteudo_html:
            return self.conteudo_html
        return self.conteudo
    
    def is_owner(self, user):
        """Verifica se o usuário é o dono do modelo"""
        return self.criado_por == user
    
    def can_edit(self, user):
        """Verifica se o usuário pode editar o modelo"""
        return self.is_owner(user) or user.is_staff
    
    def can_delete(self, user):
        """Verifica se o usuário pode excluir o modelo"""
        return self.is_owner(user) or user.is_staff
