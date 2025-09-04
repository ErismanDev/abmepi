from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import date
from decimal import Decimal
from associados.models import Associado
from core.models import Usuario


class TipoMensalidade(models.Model):
    """
    Modelo para tipos de mensalidade de associados (recorrentes)
    """
    CATEGORIA_CHOICES = [
        ('mensalidade', 'Mensalidade de Associado'),
    ]
    
    nome = models.CharField(
        max_length=100,
        verbose_name=_('Nome')
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name=_('Descrição')
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor')
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='mensalidade',
        verbose_name=_('Categoria')
    )
    
    recorrente = models.BooleanField(
        default=True,
        verbose_name=_('Recorrente')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Ativo')
    )
    
    class Meta:
        verbose_name = _('Tipo de Mensalidade')
        verbose_name_plural = _('Tipos de Mensalidade')
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"


class Mensalidade(models.Model):
    """
    Modelo para controle de mensalidades dos associados
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]
    
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='mensalidades',
        verbose_name=_('Associado')
    )
    
    tipo = models.ForeignKey(
        TipoMensalidade,
        on_delete=models.CASCADE,
        verbose_name=_('Tipo de Recebimento')
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor')
    )
    
    data_vencimento = models.DateField(
        verbose_name=_('Data de Vencimento')
    )
    
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data do Pagamento')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name=_('Status')
    )
    
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Forma de Pagamento')
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
        verbose_name = _('Mensalidade')
        verbose_name_plural = _('Mensalidades')
        ordering = ['-data_vencimento']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['data_vencimento']),
            models.Index(fields=['associado', 'status']),
        ]
    
    def __str__(self):
        return f"{self.associado.nome} - {self.tipo.nome} - {self.data_vencimento}"
    
    def get_dias_atraso(self):
        """Calcula os dias de atraso da mensalidade"""
        if self.status == 'pendente' and self.data_vencimento < date.today():
            return (date.today() - self.data_vencimento).days
        return 0
    
    def get_valor_com_multa(self):
        """Calcula o valor com multa por atraso"""
        if self.status == 'pendente' and self.data_vencimento < date.today():
            dias_atraso = self.get_dias_atraso()
            if dias_atraso > 0:
                multa = self.valor * Decimal('0.02')  # 2% de multa
                juros = self.valor * Decimal('0.001') * dias_atraso  # 0.1% ao dia
                return self.valor + multa + juros
        return self.valor


class Pagamento(models.Model):
    """
    Modelo para registro de pagamentos
    """
    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('dinheiro', 'Dinheiro'),
        ('transferencia', 'Transferência Bancária'),
        ('outro', 'Outro'),
    ]
    
    mensalidade = models.ForeignKey(
        Mensalidade,
        on_delete=models.CASCADE,
        related_name='pagamentos',
        verbose_name=_('Mensalidade')
    )
    
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor Pago')
    )
    
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name=_('Forma de Pagamento')
    )
    
    data_pagamento = models.DateTimeField(
        verbose_name=_('Data e Hora do Pagamento')
    )
    
    comprovante = models.FileField(
        upload_to='financeiro/comprovantes/',
        null=True,
        blank=True,
        verbose_name=_('Comprovante')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Usuário que Registrou')
    )
    
    class Meta:
        verbose_name = _('Pagamento')
        verbose_name_plural = _('Pagamentos')
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f"{self.mensalidade.associado.nome} - R$ {self.valor_pago} - {self.get_forma_pagamento_display()}"


class Despesa(models.Model):
    """
    Modelo para controle de despesas da associação
    """
    CATEGORIA_CHOICES = [
        ('administrativa', 'Administrativa'),
        ('operacional', 'Operacional'),
        ('manutencao', 'Manutenção'),
        ('eventos', 'Eventos'),
        ('outros', 'Outros'),
    ]
    
    descricao = models.CharField(
        max_length=200,
        verbose_name=_('Descrição')
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name=_('Categoria')
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Valor')
    )
    
    data_despesa = models.DateField(
        verbose_name=_('Data da Despesa')
    )
    
    data_vencimento = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Data de Vencimento')
    )
    
    pago = models.BooleanField(
        default=False,
        verbose_name=_('Pago')
    )
    
    fornecedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Fornecedor')
    )
    
    nota_fiscal = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Número da Nota Fiscal')
    )
    
    comprovante = models.FileField(
        upload_to='financeiro/despesas/',
        null=True,
        blank=True,
        verbose_name=_('Comprovante')
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
        verbose_name = _('Despesa')
        verbose_name_plural = _('Despesas')
        ordering = ['-data_despesa']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} - {self.data_despesa}"


class RelatorioFinanceiro(models.Model):
    """
    Modelo para armazenar relatórios financeiros gerados
    """
    TIPO_RELATORIO_CHOICES = [
        ('mensalidades', 'Relatório de Mensalidades'),
        ('receitas', 'Relatório de Receitas'),
        ('despesas', 'Relatório de Despesas'),
        ('inadimplencia', 'Relatório de Inadimplência'),
        ('balanco', 'Balanço Geral'),
    ]
    
    tipo = models.CharField(
        max_length=20,
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
        upload_to='financeiro/relatorios/',
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
        verbose_name = _('Relatório Financeiro')
        verbose_name_plural = _('Relatórios Financeiros')
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.periodo_inicio} a {self.periodo_fim}"


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
    
    # Mensagem personalizada (simplificada para uma só)
    mensagem = models.TextField(max_length=200, default="Pague suas mensalidades na sede da associação ou pelo QR Code e envie o comprovante para o telefone informado", help_text="Mensagem personalizada para o carnê")
    telefone_comprovante = models.CharField(max_length=20, default="86 988197790", help_text="Telefone para envio do comprovante")
    
    # Configurações do QR Code
    qr_code_ativo = models.BooleanField(default=True, help_text="Exibir QR Code no carnê")
    qr_code_imagem = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="Imagem do QR Code (PNG, JPG)")
    qr_code_tamanho = models.IntegerField(default=15, help_text="Tamanho do QR Code em mm")
    
    # Configurações gerais
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Cobrança"
        verbose_name_plural = "Configuração de Cobrança"
        ordering = ['-ativo', '-data_criacao']
    
    def __str__(self):
        return f"{self.nome} {'(Ativo)' if self.ativo else '(Inativo)'}"
    
    def save(self, *args, **kwargs):
        # Se esta configuração for ativada, desativar todas as outras
        if self.ativo:
            ConfiguracaoCobranca.objects.exclude(pk=self.pk).update(ativo=False)
        super().save(*args, **kwargs)
    
    def get_mensagem_completa(self):
        """Retorna a mensagem completa formatada"""
        return f"{self.mensagem} {self.telefone_comprovante}"
    
    @classmethod
    def get_configuracao_ativa(cls):
        """Retorna a configuração ativa ou cria uma padrão"""
        config = cls.objects.filter(ativo=True).first()
        if not config:
            # Criar configuração padrão se não existir
            config = cls.objects.create(
                nome="Configuração Padrão",
                ativo=True,
                chave_pix="86 988197790",
                titular="Gustavo Henrique de Araujo Sousa",
                banco="MERCADO PAGO"
            )
        return config
    
    @classmethod
    def get_configuracao_unica(cls):
        """Retorna a única configuração ou cria uma padrão"""
        # Tentar obter a configuração ativa
        config = cls.objects.filter(ativo=True).first()
        if config:
            return config
        
        # Se não houver ativa, tentar obter qualquer uma
        config = cls.objects.first()
        if config:
            config.ativo = True
            config.save()
            return config
        
        # Se não houver nenhuma, criar uma padrão
        return cls.objects.create(
            nome="Configuração Padrão",
            ativo=True,
            chave_pix="86 988197790",
            titular="Gustavo Henrique de Araujo Sousa",
            banco="MERCADO PAGO"
        )
