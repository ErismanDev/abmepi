from django.db import models
from django.contrib.auth import get_user_model
from associados.models import Associado

User = get_user_model()


class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='agendado')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=200)
    endereco = models.TextField(blank=True)
    capacidade_maxima = models.PositiveIntegerField(null=True, blank=True)
    valor_inscricao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    responsavel = models.CharField(max_length=200, blank=True)
    usuario_responsavel = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    imagem = models.ImageField(upload_to='administrativo/eventos/', null=True, blank=True)
    arquivos_anexados = models.FileField(
        upload_to='administrativo/eventos/arquivos/', null=True, blank=True
    )
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo


class ParticipanteEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participantes')
    associado = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='participacoes_evento')
    status = models.CharField(max_length=20, default='pendente')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_presenca = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Participante do Evento'
        verbose_name_plural = 'Participantes dos Eventos'
        ordering = ['data_inscricao']
    
    def __str__(self):
        return f"{self.associado.nome} - {self.evento.titulo}"


class Comunicado(models.Model):
    TIPO_CHOICES = [
        ('informacao', 'Informação'),
        ('aviso', 'Aviso'),
        ('lembrete', 'Lembrete'),
        ('urgencia', 'Urgência'),
        ('evento', 'Evento'),
        ('outro', 'Outro'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    DESTINATARIOS_CHOICES = [
        ('todos', 'Todos os Associados, Advogados e Psicólogos'),
        ('associados', 'Apenas Associados'),
        ('advogados', 'Apenas Advogados'),
        ('psicologos', 'Apenas Psicólogos'),
        ('especificos', 'Seleção Específica'),
    ]
    
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='normal')
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Campo para escolher o tipo de destinatários
    tipo_destinatarios = models.CharField(
        max_length=20, 
        choices=DESTINATARIOS_CHOICES, 
        default='todos',
        verbose_name='Tipo de Destinatários'
    )
    
    # Campos para seleção específica
    associados_especificos = models.ManyToManyField(
        'associados.Associado',
        blank=True,
        verbose_name='Associados Específicos'
    )
    advogados_especificos = models.ManyToManyField(
        'assejus.Advogado',
        blank=True,
        verbose_name='Advogados Específicos'
    )
    psicologos_especificos = models.ManyToManyField(
        'psicologia.Psicologo',
        blank=True,
        verbose_name='Psicólogos Específicos'
    )
    
    # Campo de texto para destinatários personalizados (mantido para compatibilidade)
    destinatarios = models.TextField(blank=True, verbose_name='Destinatários Personalizados')
    
    enviar_email = models.BooleanField(default=False)
    enviar_sms = models.BooleanField(default=False)
    enviar_notificacao = models.BooleanField(default=False, verbose_name='Enviar Notificação')
    arquivos_anexados = models.FileField(
        upload_to='administrativo/comunicados/', null=True, blank=True
    )
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'
        ordering = ['-data_publicacao']
    
    def __str__(self):
        return self.titulo


class ListaPresenca(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='listas_presenca')
    data_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Lista de Presenca'
        verbose_name_plural = 'Listas de Presenca'
        ordering = ['-data_registro']
    
    def __str__(self):
        return f"Lista de Presenca - {self.evento.titulo}"


class Presenca(models.Model):
    lista_presenca = models.ForeignKey(
        ListaPresenca, on_delete=models.CASCADE, related_name='presencas'
    )
    associado = models.ForeignKey(Associado, on_delete=models.CASCADE, related_name='presencas')
    presente = models.BooleanField(default=False)
    horario_chegada = models.TimeField(null=True, blank=True)
    horario_saida = models.TimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Presenca'
        verbose_name_plural = 'Presencas'
        ordering = ['associado']
    
    def __str__(self):
        status = "Presente" if self.presente else "Ausente"
        return f"{self.associado.nome} - {status}"
    
    @classmethod
    def contar_presentes(cls, queryset):
        """Conta quantas presenças estão marcadas como presentes"""
        return queryset.filter(presente=True).count()
    
    @classmethod
    def contar_ausentes(cls, queryset):
        """Conta quantas presenças estão marcadas como ausentes"""
        return queryset.filter(presente=False).count()
