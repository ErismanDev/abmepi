from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Quarto(models.Model):
    """Modelo para cadastro de quartos do hotel de trânsito"""
    
    TIPO_QUARTO_CHOICES = [
        ('individual', 'Individual'),
        ('duplo', 'Duplo'),
        ('triplo', 'Triplo'),
        ('suite', 'Suíte'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('ocupado', 'Ocupado'),
        ('manutencao', 'Em Manutenção'),
        ('reservado', 'Reservado'),
    ]
    
    numero = models.CharField(max_length=10, unique=True, verbose_name="Número do Quarto")
    tipo = models.CharField(max_length=20, choices=TIPO_QUARTO_CHOICES, verbose_name="Tipo de Quarto")
    capacidade = models.PositiveIntegerField(verbose_name="Capacidade")
    valor_diaria = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor da Diária")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status")
    
    # Características do quarto
    ar_condicionado = models.BooleanField(default=True, verbose_name="Ar Condicionado")
    tv = models.BooleanField(default=True, verbose_name="TV")
    wifi = models.BooleanField(default=True, verbose_name="Wi-Fi")
    banheiro_privativo = models.BooleanField(default=True, verbose_name="Banheiro Privativo")
    frigobar = models.BooleanField(default=False, verbose_name="Frigobar")
    
    # Observações
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Quarto"
        verbose_name_plural = "Quartos"
        ordering = ['numero']
    
    def __str__(self):
        return f"Quarto {self.numero} - {self.get_tipo_display()}"


class Hospede(models.Model):
    """Modelo para cadastro de hóspedes (associados ou não associados)"""
    
    TIPO_HOSPEDE_CHOICES = [
        ('associado', 'Associado'),
        ('visitante', 'Visitante'),
        ('funcionario', 'Funcionário'),
        ('conveniado', 'Conveniado'),
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('cpf', 'CPF'),
        ('rg', 'RG'),
        ('passaporte', 'Passaporte'),
        ('cnh', 'CNH'),
        ('outro', 'Outro'),
    ]
    
    # Tipo de hóspede
    tipo_hospede = models.CharField(max_length=20, choices=TIPO_HOSPEDE_CHOICES, verbose_name="Tipo de Hóspede")
    
    # Relacionamento com associado (se for associado)
    associado = models.ForeignKey(
        'associados.Associado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Associado",
        related_name="hospedagens"
    )
    
    # Dados pessoais (para não associados ou complementar dados de associados)
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    
    # Foto do hóspede
    foto = models.ImageField(upload_to='hospedes/', null=True, blank=True, verbose_name="Foto")
    
    # Documentos
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo de Documento")
    numero_documento = models.CharField(max_length=20, verbose_name="Número do Documento")
    orgao_emissor = models.CharField(max_length=10, blank=True, verbose_name="Órgão Emissor")
    uf_emissor = models.CharField(max_length=2, blank=True, verbose_name="UF Emissor")
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    telefone_secundario = models.CharField(max_length=20, blank=True, verbose_name="Telefone Secundário")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")
    endereco = models.CharField(max_length=200, blank=True, verbose_name="Endereço")
    numero = models.CharField(max_length=10, blank=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, verbose_name="Estado")
    
    # Dados profissionais (para não associados)
    profissao = models.CharField(max_length=100, blank=True, verbose_name="Profissão")
    empresa = models.CharField(max_length=200, blank=True, verbose_name="Empresa")
    
    # Status e controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Hóspede"
        verbose_name_plural = "Hóspedes"
        ordering = ['nome_completo']
    
    def __str__(self):
        if self.associado:
            return f"{self.nome_completo} (Associado: {self.associado.nome})"
        return f"{self.nome_completo} ({self.get_tipo_hospede_display()})"
    
    def save(self, *args, **kwargs):
        # Se for associado, preencher automaticamente alguns campos
        if self.associado:
            if not self.nome_completo:
                self.nome_completo = self.associado.nome
            if not self.data_nascimento:
                self.data_nascimento = self.associado.data_nascimento
            if not self.telefone:
                self.telefone = self.associado.telefone or self.associado.celular
            if not self.email:
                self.email = self.associado.email
            # Se não tiver foto própria, usar a foto do associado
            if not self.foto and self.associado.foto:
                self.foto = self.associado.foto
        
        super().save(*args, **kwargs)


class Reserva(models.Model):
    """Modelo para reservas de quartos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
    ]
    
    # Dados da reserva
    codigo_reserva = models.CharField(max_length=20, unique=True, verbose_name="Código da Reserva")
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE, verbose_name="Quarto")
    hospede = models.ForeignKey(Hospede, on_delete=models.CASCADE, verbose_name="Hóspede")
    
    # Datas
    data_entrada = models.DateField(verbose_name="Data de Entrada")
    data_saida = models.DateField(verbose_name="Data de Saída")
    hora_entrada = models.TimeField(default='14:00', verbose_name="Hora de Entrada")
    hora_saida = models.TimeField(default='12:00', verbose_name="Hora de Saída")
    
    # Valores
    valor_diaria = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor da Diária")
    quantidade_diarias = models.PositiveIntegerField(verbose_name="Quantidade de Diárias")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    data_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Data da Reserva")
    data_confirmacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Confirmação")
    data_cancelamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Cancelamento")
    
    # Observações
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    motivo_cancelamento = models.TextField(blank=True, verbose_name="Motivo do Cancelamento")
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-data_reserva']
    
    def __str__(self):
        return f"Reserva {self.codigo_reserva} - {self.hospede.nome_completo}"
    
    def save(self, *args, **kwargs):
        # Calcular quantidade de diárias e valor total
        if self.data_entrada and self.data_saida:
            delta = self.data_saida - self.data_entrada
            self.quantidade_diarias = delta.days
            self.valor_total = self.valor_diaria * self.quantidade_diarias
        super().save(*args, **kwargs)


class Hospedagem(models.Model):
    """Modelo para registro de hospedagens efetivas"""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Dados da hospedagem
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, verbose_name="Reserva", null=True, blank=True)
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE, verbose_name="Quarto")
    hospede = models.ForeignKey(Hospede, on_delete=models.CASCADE, verbose_name="Hóspede")
    
    # Datas reais
    data_entrada_real = models.DateTimeField(verbose_name="Data e Hora de Entrada Real")
    data_saida_real = models.DateTimeField(null=True, blank=True, verbose_name="Data e Hora de Saída Real")
    
    # Valores reais
    valor_diaria_real = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor da Diária Real")
    quantidade_diarias_real = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Diárias Real")
    valor_total_real = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Total Real")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    # Observações
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    motivo_cancelamento = models.TextField(blank=True, verbose_name="Motivo do Cancelamento")
    
    class Meta:
        verbose_name = "Hospedagem"
        verbose_name_plural = "Hospedagens"
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"Hospedagem {self.id} - {self.hospede.nome_completo} - Quarto {self.quarto.numero}"
    
    def save(self, *args, **kwargs):
        # Garantir que quantidade_diarias_real tenha um valor válido
        if not self.quantidade_diarias_real:
            self.quantidade_diarias_real = 1
        
        # Calcular quantidade de diárias e valor total reais
        if self.data_entrada_real:
            if self.data_saida_real:
                # Se ambas as datas estão preenchidas, calcular baseado na diferença
                delta = self.data_saida_real.date() - self.data_entrada_real.date()
                self.quantidade_diarias_real = max(1, delta.days)  # Mínimo de 1 dia
            else:
                # Se apenas a data de entrada está preenchida, considerar 1 dia
                self.quantidade_diarias_real = 1
            
            # Calcular valor total baseado na quantidade de diárias
            if self.valor_diaria_real:
                self.valor_total_real = self.valor_diaria_real * self.quantidade_diarias_real
            else:
                self.valor_total_real = 0
        else:
            # Se não há data de entrada, definir valores padrão
            self.quantidade_diarias_real = 1
            self.valor_total_real = 0
        
        super().save(*args, **kwargs)


class ServicoAdicional(models.Model):
    """Modelo para serviços adicionais oferecidos pelo hotel"""
    
    TIPO_SERVICO_CHOICES = [
        ('alimentacao', 'Alimentação'),
        ('transporte', 'Transporte'),
        ('lavanderia', 'Lavanderia'),
        ('limpeza', 'Limpeza'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    tipo = models.CharField(max_length=20, choices=TIPO_SERVICO_CHOICES, verbose_name="Tipo de Serviço")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Serviço Adicional"
        verbose_name_plural = "Serviços Adicionais"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"


class ServicoUtilizado(models.Model):
    """Modelo para registro de serviços utilizados pelos hóspedes"""
    
    hospedagem = models.ForeignKey(Hospedagem, on_delete=models.CASCADE, verbose_name="Hospedagem")
    servico = models.ForeignKey(ServicoAdicional, on_delete=models.CASCADE, verbose_name="Serviço")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    valor_unitario = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor Unitário")
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor Total")
    data_utilizacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Utilização")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Serviço Utilizado"
        verbose_name_plural = "Serviços Utilizados"
        ordering = ['-data_utilizacao']
    
    def __str__(self):
        return f"{self.servico.nome} - {self.hospedagem.hospede.nome_completo}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = self.valor_unitario * self.quantidade
        super().save(*args, **kwargs)
