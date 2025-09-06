from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from associados.models import Associado
from core.models import Usuario


class EmpresaParceira(models.Model):
    """
    Modelo para cadastro de empresas parceiras
    """
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome da Empresa')
    )
    
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        verbose_name=_('CNPJ')
    )
    
    razao_social = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Razão Social')
    )
    
    endereco = models.TextField(
        verbose_name=_('Endereço')
    )
    
    cidade = models.CharField(
        max_length=100,
        verbose_name=_('Cidade')
    )
    
    estado = models.CharField(
        max_length=2,
        verbose_name=_('Estado')
    )
    
    cep = models.CharField(
        max_length=9,
        blank=True,
        verbose_name=_('CEP')
    )
    
    telefone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Telefone')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail')
    )
    
    website = models.URLField(
        blank=True,
        verbose_name=_('Website')
    )
    
    contato_principal = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Contato Principal')
    )
    
    telefone_contato = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Telefone do Contato')
    )
    
    email_contato = models.EmailField(
        blank=True,
        verbose_name=_('E-mail do Contato')
    )
    
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Cadastro')
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data de Atualização')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Empresa Ativa')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    class Meta:
        verbose_name = _('Empresa Parceira')
        verbose_name_plural = _('Empresas Parceiras')
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Convenio(models.Model):
    """
    Modelo para cadastro de convênios
    """
    CATEGORIA_CHOICES = [
        ('saude', 'Saúde'),
        ('educacao', 'Educação'),
        ('lazer', 'Lazer'),
        ('comercio', 'Comércio'),
        ('servicos', 'Serviços'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('pendente', 'Pendente'),
        ('expirado', 'Expirado'),
    ]
    
    empresa = models.ForeignKey(
        EmpresaParceira,
        on_delete=models.CASCADE,
        related_name='convenios',
        verbose_name=_('Empresa Parceira')
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Título do Convênio')
    )
    
    descricao = models.TextField(
        verbose_name=_('Descrição')
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name=_('Categoria')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ativo',
        verbose_name=_('Status')
    )
    
    data_inicio = models.DateField(
        verbose_name=_('Data de Início')
    )
    
    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data de Fim')
    )
    
    desconto = models.CharField(
        max_length=100,
        verbose_name=_('Desconto Oferecido')
    )
    
    condicoes = models.TextField(
        blank=True,
        verbose_name=_('Condições do Convênio')
    )
    
    documentos_necessarios = models.TextField(
        blank=True,
        verbose_name=_('Documentos Necessários')
    )
    
    usuario_responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Usuário Responsável')
    )
    
    arquivos_anexados = models.FileField(
        upload_to='beneficios/convenios/',
        null=True,
        blank=True,
        verbose_name=_('Arquivos Anexados')
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
        verbose_name=_('Convênio Ativo')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    class Meta:
        verbose_name = _('Convênio')
        verbose_name_plural = _('Convênios')
        ordering = ['-data_inicio']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['categoria']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.empresa.nome}"
    
    def is_valido(self):
        """Verifica se o convênio está válido"""
        from datetime import date
        if self.data_fim:
            return date.today() <= self.data_fim
        return True


class Beneficio(models.Model):
    """
    Modelo para registro dos benefícios utilizados pelos associados
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('utilizado', 'Utilizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='beneficios',
        verbose_name=_('Associado')
    )
    
    convenio = models.ForeignKey(
        Convenio,
        on_delete=models.CASCADE,
        related_name='beneficios',
        verbose_name=_('Convênio')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name=_('Status')
    )
    
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data da Solicitação')
    )
    
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data da Aprovação')
    )
    
    data_utilizacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data da Utilização')
    )
    
    valor_beneficio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Valor do Benefício')
    )
    
    desconto_aplicado = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Desconto Aplicado')
    )
    
    usuario_aprovacao = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficios_aprovados',
        verbose_name=_('Usuário que Aprovou')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    comprovante = models.FileField(
        upload_to='beneficios/comprovantes/',
        null=True,
        blank=True,
        verbose_name=_('Comprovante')
    )
    
    class Meta:
        verbose_name = _('Benefício')
        verbose_name_plural = _('Benefícios')
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['associado', 'status']),
        ]
    
    def __str__(self):
        return f"{self.associado.nome} - {self.convenio.titulo} - {self.get_status_display()}"
    
    def get_dias_aprovacao(self):
        """Calcula quantos dias demorou para aprovação"""
        if self.data_aprovacao:
            return (self.data_aprovacao - self.data_solicitacao).days
        return None


class CategoriaBeneficio(models.Model):
    """
    Modelo para categorias de benefícios
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome da Categoria')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição')
    )
    
    icone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Ícone (FontAwesome)')
    )
    
    cor = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_('Cor (Hex)')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Categoria Ativa')
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ordem de Exibição')
    )
    
    class Meta:
        verbose_name = _('Categoria de Benefício')
        verbose_name_plural = _('Categorias de Benefícios')
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class RelatorioBeneficios(models.Model):
    """
    Modelo para relatórios de benefícios
    """
    TIPO_RELATORIO_CHOICES = [
        ('beneficios_por_categoria', 'Benefícios por Categoria'),
        ('beneficios_por_associado', 'Benefícios por Associado'),
        ('beneficios_por_empresa', 'Benefícios por Empresa'),
        ('utilizacao_mensal', 'Utilização Mensal'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_RELATORIO_CHOICES,
        verbose_name=_('Tipo de Relatório')
    )
    
    periodo_inicio = models.DateField(
        verbose_name=_('Período Início')
    )
    
    periodo_fim = models.DateField(
        verbose_name=_('Período Fim')
    )
    
    arquivo = models.FileField(
        upload_to='beneficios/relatorios/',
        verbose_name=_('Arquivo do Relatório')
    )
    
    data_geracao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Geração')
    )
    
    usuario_geracao = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Usuário que Gerou')
    )
    
    class Meta:
        verbose_name = _('Relatório de Benefícios')
        verbose_name_plural = _('Relatórios de Benefícios')
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.periodo_inicio} a {self.periodo_fim}"
