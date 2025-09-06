from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from associados.models import Associado


class CargoDiretoria(models.Model):
    """
    Modelo para definir os cargos da diretoria
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome do Cargo')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição do Cargo')
    )
    
    ordem_hierarquica = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_('Ordem Hierárquica'),
        help_text=_('1 = mais alto, 100 = mais baixo')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Cargo Ativo')
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Criação')
    )
    
    class Meta:
        ordering = ['ordem_hierarquica', 'nome']
        verbose_name = _('Cargo da Diretoria')
        verbose_name_plural = _('Cargos da Diretoria')
    
    def __str__(self):
        return self.nome


class MembroDiretoria(models.Model):
    """
    Modelo para membros da diretoria
    """
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='cargos_diretoria',
        verbose_name=_('Associado')
    )
    
    cargo = models.ForeignKey(
        CargoDiretoria,
        on_delete=models.CASCADE,
        related_name='membros',
        verbose_name=_('Cargo')
    )
    
    data_inicio = models.DateField(
        verbose_name=_('Data de Início')
    )
    
    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data de Fim')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Membro Ativo')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
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
        ordering = ['cargo__ordem_hierarquica', 'associado__nome']
        verbose_name = _('Membro da Diretoria')
        verbose_name_plural = _('Membros da Diretoria')
        unique_together = ['associado', 'cargo', 'data_inicio']
    
    def __str__(self):
        return f"{self.associado.nome} - {self.cargo.nome}"
    
    @property
    def periodo_ativo(self):
        """Retorna se o membro está ativo no período atual"""
        from django.utils import timezone
        hoje = timezone.now().date()
        
        if self.data_fim and self.data_fim < hoje:
            return False
        if self.data_inicio > hoje:
            return False
        return self.ativo
    
    @classmethod
    def get_presidente_atual(cls):
        """
        Retorna o presidente atual da diretoria
        """
        from django.utils import timezone
        hoje = timezone.now().date()
        
        # Buscar cargo de presidente (assumindo que tem ordem_hierarquica = 1)
        try:
            cargo_presidente = CargoDiretoria.objects.filter(
                ativo=True,
                ordem_hierarquica=1
            ).first()
            
            if not cargo_presidente:
                return None
            
            # Buscar membro ativo no cargo de presidente
            presidente = cls.objects.filter(
                cargo=cargo_presidente,
                ativo=True,
                data_inicio__lte=hoje
            ).filter(
                models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=hoje)
            ).select_related('associado', 'cargo').first()
            
            return presidente
            
        except Exception:
            return None


class AtaReuniao(models.Model):
    """
    Modelo para atas de reuniões da diretoria
    """
    TIPO_REUNIAO_CHOICES = [
        ('ordinaria', 'Reunião Ordinária'),
        ('extraordinaria', 'Reunião Extraordinária'),
        ('emergencia', 'Reunião de Emergência'),
        ('especial', 'Reunião Especial'),
    ]
    
    numero_sequencial = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Número Sequencial'),
        help_text=_('Número sequencial da ata por tipo de reunião')
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Título da Reunião')
    )
    
    tipo_reuniao = models.CharField(
        max_length=20,
        choices=TIPO_REUNIAO_CHOICES,
        default='ordinaria',
        verbose_name=_('Tipo de Reunião')
    )
    
    data_reuniao = models.DateTimeField(
        verbose_name=_('Data e Hora da Reunião')
    )
    
    local = models.CharField(
        max_length=200,
        verbose_name=_('Local da Reunião')
    )
    
    presidente = models.ForeignKey(
        MembroDiretoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reunioes_presididas',
        verbose_name=_('Presidente da Reunião')
    )
    
    secretario = models.ForeignKey(
        MembroDiretoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reunioes_secretariadas',
        verbose_name=_('Secretário da Reunião')
    )
    
    membros_presentes = models.ManyToManyField(
        MembroDiretoria,
        related_name='reunioes_presente',
        verbose_name=_('Membros Presentes')
    )
    
    membros_ausentes = models.ManyToManyField(
        MembroDiretoria,
        related_name='reunioes_ausente',
        blank=True,
        verbose_name=_('Membros Ausentes')
    )
    
    # Associados presentes (não membros da diretoria)
    associados_presentes = models.ManyToManyField(
        'associados.Associado',
        related_name='atas_presente',
        blank=True,
        verbose_name=_('Associados Presentes')
    )
    
    # Associados ausentes (não membros da diretoria)
    associados_ausentes = models.ManyToManyField(
        'associados.Associado',
        related_name='atas_ausente',
        blank=True,
        verbose_name=_('Associados Ausentes')
    )
    
    pauta = models.TextField(
        verbose_name=_('Pauta da Reunião')
    )
    
    deliberacoes = models.TextField(
        verbose_name=_('Deliberações')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    conteudo_completo = models.TextField(
        blank=True,
        verbose_name=_('Conteúdo Completo da Ata'),
        help_text=_('Editor único para toda a ata com modelos prontos')
    )
    
    arquivo_ata = models.FileField(
        upload_to='diretoria/atas/',
        null=True,
        blank=True,
        verbose_name=_('Arquivo da Ata')
    )
    
    aprovada = models.BooleanField(
        default=False,
        verbose_name=_('Ata Aprovada')
    )
    
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data de Aprovação')
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
        ordering = ['-data_reuniao']
        verbose_name = _('Ata de Reunião')
        verbose_name_plural = _('Atas de Reunião')
    
    def __str__(self):
        return f"{self.titulo} - {self.data_reuniao.strftime('%d/%m/%Y')}"
    
    def gerar_numero_sequencial(self):
        """
        Gera o próximo número sequencial para o tipo de reunião
        """
        if self.numero_sequencial:
            return self.numero_sequencial
            
        # Busca o último número para este tipo de reunião no mesmo ano
        ano_atual = self.data_reuniao.year
        ultima_ata = AtaReuniao.objects.filter(
            tipo_reuniao=self.tipo_reuniao,
            data_reuniao__year=ano_atual,
            numero_sequencial__isnull=False
        ).order_by('-numero_sequencial').first()
        
        if ultima_ata and ultima_ata.numero_sequencial:
            return ultima_ata.numero_sequencial + 1
        else:
            return 1
    
    def get_numero_formatado(self):
        """
        Retorna o número formatado da ata (ex: ORD-001/2024)
        """
        if not self.numero_sequencial:
            return "N/A"
        
        ano = self.data_reuniao.year
        prefixo = {
            'ordinaria': 'ORD',
            'extraordinaria': 'EXT',
            'emergencia': 'EMG',
            'especial': 'ESP'
        }.get(self.tipo_reuniao, 'ATA')
        
        return f"{prefixo}-{self.numero_sequencial:03d}/{ano}"
    
    def save(self, *args, **kwargs):
        # Gera o número sequencial se não existir
        if not self.numero_sequencial:
            self.numero_sequencial = self.gerar_numero_sequencial()
        super().save(*args, **kwargs)


class ModeloAta(models.Model):
    """
    Modelo para templates de atas de reunião
    """
    CATEGORIA_CHOICES = [
        ('geral', 'Geral'),
        ('ordinaria', 'Reunião Ordinária'),
        ('extraordinaria', 'Reunião Extraordinária'),
        ('emergencia', 'Emergência'),
        ('assembleia', 'Assembleia'),
    ]
    
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome do Modelo')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição do Modelo')
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='geral',
        verbose_name=_('Categoria')
    )
    
    conteudo = models.TextField(
        verbose_name=_('Conteúdo do Modelo')
    )
    
    publico = models.BooleanField(
        default=False,
        verbose_name=_('Modelo Público'),
        help_text=_('Se marcado, outros usuários podem usar este modelo')
    )
    
    criado_por = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='modelos_criados',
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
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Modelo Ativo')
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = _('Modelo de Ata')
        verbose_name_plural = _('Modelos de Ata')
    
    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class TemplateAta(models.Model):
    """
    Modelo para templates/modelos de atas prontos
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome do Template')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição do Template')
    )
    
    conteudo = models.TextField(
        verbose_name=_('Conteúdo do Template'),
        help_text=_('HTML do template com placeholders como [TITULO], [DATA], etc.')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Template Ativo')
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
        ordering = ['nome']
        verbose_name = _('Template de Ata')
        verbose_name_plural = _('Templates de Ata')
    
    def __str__(self):
        return self.nome


class ModeloAtaPersonalizado(models.Model):
    """
    Modelo para salvar templates personalizados de atas criados pelos usuários
    """
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome do Modelo')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição do Modelo')
    )
    
    conteudo_html = models.TextField(
        verbose_name=_('Conteúdo HTML do Modelo')
    )
    
    # Metadados da ata original
    titulo_original = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Título da Ata Original')
    )
    
    tipo_reuniao = models.CharField(
        max_length=20,
        choices=AtaReuniao.TIPO_REUNIAO_CHOICES,
        default='ordinaria',
        verbose_name=_('Tipo de Reunião')
    )
    
    # Usuário que criou o modelo
    criado_por = models.ForeignKey(
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='modelos_ata_criados',
        verbose_name=_('Criado por')
    )
    
    # Categorias para organização
    categoria = models.CharField(
        max_length=50,
        default='geral',
        verbose_name=_('Categoria'),
        help_text=_('Ex: reunião ordinária, assembleia, emergência')
    )
    
    # Status do modelo
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Modelo Ativo')
    )
    
    publico = models.BooleanField(
        default=False,
        verbose_name=_('Modelo Público'),
        help_text=_('Se marcado, outros usuários podem usar este modelo')
    )
    
    # Contadores de uso
    vezes_usado = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Vezes Usado')
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
        ordering = ['-data_atualizacao', 'nome']
        verbose_name = _('Modelo de Ata Personalizado')
        verbose_name_plural = _('Modelos de Ata Personalizados')
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_reuniao_display()}"
    
    def incrementar_uso(self):
        """Incrementa o contador de uso do modelo"""
        self.vezes_usado += 1
        self.save(update_fields=['vezes_usado'])


class ResolucaoDiretoria(models.Model):
    """
    Modelo para resoluções da diretoria
    """
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('aprovada', 'Aprovada'),
        ('revogada', 'Revogada'),
        ('suspensa', 'Suspensa'),
    ]
    
    numero = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Número da Resolução')
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Título da Resolução')
    )
    
    ementa = models.TextField(
        verbose_name=_('Ementa')
    )
    
    texto_integral = models.TextField(
        verbose_name=_('Texto Integral')
    )
    
    data_resolucao = models.DateField(
        verbose_name=_('Data da Resolução')
    )
    
    data_publicacao = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data de Publicação')
    )
    
    data_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data de Vigência')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho',
        verbose_name=_('Status')
    )
    
    ata_reuniao = models.ForeignKey(
        AtaReuniao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolucoes',
        verbose_name=_('Ata de Reunião')
    )
    
    arquivo_resolucao = models.FileField(
        upload_to='diretoria/resolucoes/',
        null=True,
        blank=True,
        verbose_name=_('Arquivo da Resolução')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
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
        ordering = ['-data_resolucao', '-numero']
        verbose_name = _('Resolução da Diretoria')
        verbose_name_plural = _('Resoluções da Diretoria')
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"

# Importar o modelo de ata simples
from .models_ata_simples import AtaSimples


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
        'core.Usuario',
        on_delete=models.CASCADE,
        related_name='modelos_ata_unificados',
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
        verbose_name = _('Modelo de Ata Unificado')
        verbose_name_plural = _('Modelos de Ata Unificados')
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