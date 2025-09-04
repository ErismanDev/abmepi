from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Psicologo(models.Model):
    """Modelo para cadastro de psicólogos"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    crp = models.CharField(max_length=20, unique=True, verbose_name="CRP")
    uf_crp = models.CharField(max_length=2, blank=True, verbose_name="UF do CRP")
    
    # Dados pessoais
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    cpf = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, verbose_name="RG")
    orgao_emissor = models.CharField(max_length=20, blank=True, verbose_name="Órgão Emissor")
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    telefone_secundario = models.CharField(max_length=20, blank=True, verbose_name="Telefone Secundário")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    email_secundario = models.EmailField(blank=True, verbose_name="E-mail Secundário")
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")
    endereco = models.CharField(max_length=200, blank=True, verbose_name="Endereço")
    numero = models.CharField(max_length=10, blank=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, verbose_name="Estado")
    
    # Dados profissionais
    especialidades = models.TextField(verbose_name="Especialidades", blank=True)
    formacao_academica = models.TextField(verbose_name="Formação Acadêmica", blank=True)
    cursos_complementares = models.TextField(verbose_name="Cursos Complementares", blank=True)
    experiencia_profissional = models.TextField(verbose_name="Experiência Profissional", blank=True)
    areas_atuacao = models.TextField(verbose_name="Áreas de Atuação", blank=True)
    
    # Dados de trabalho
    horario_atendimento = models.TextField(verbose_name="Horário de Atendimento", blank=True)
    valor_consulta = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Valor da Consulta")
    aceita_planos_saude = models.BooleanField(default=False, verbose_name="Aceita Planos de Saúde")
    planos_aceitos = models.TextField(blank=True, verbose_name="Planos Aceitos")
    
    # Documentos
    foto = models.ImageField(upload_to='psicologos/fotos/', null=True, blank=True, verbose_name="Foto")
    curriculo = models.FileField(upload_to='psicologos/curriculos/', null=True, blank=True, verbose_name="Currículo")
    documentos_complementares = models.FileField(upload_to='psicologos/documentos/', null=True, blank=True, verbose_name="Documentos Complementares")
    
    # Status e controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Psicólogo"
        verbose_name_plural = "Psicólogos"
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} - CRP: {self.crp}/{self.uf_crp}"
    
    @property
    def pacientes(self):
        """Retorna todos os pacientes responsáveis por este psicólogo"""
        return self.pacientes_responsavel.all()
    
    @property 
    def total_pacientes(self):
        """Retorna o total de pacientes deste psicólogo"""
        return self.pacientes_responsavel.count()
    
    @property
    def pacientes_ativos(self):
        """Retorna o total de pacientes ativos deste psicólogo"""
        return self.pacientes_responsavel.filter(ativo=True).count()


class Paciente(models.Model):
    """Modelo para cadastro de pacientes - permite múltiplos psicólogos"""
    
    # Relacionamento com associado ou dependente
    associado = models.OneToOneField(
        'associados.Associado', 
        on_delete=models.CASCADE, 
        verbose_name="Associado"
    )
    
    # Relacionamento many-to-many com psicólogos através do modelo PacientePsicologo
    psicologos = models.ManyToManyField(
        Psicologo,
        through='PacientePsicologo',
        verbose_name="Psicólogos",
        blank=True
    )
    
    # Mantém campo psicologo_responsavel para compatibilidade (será deprecated)
    psicologo_responsavel = models.ForeignKey(
        Psicologo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Psicólogo Responsável Principal",
        related_name="pacientes_responsavel"
    )
    
    # Dados clínicos
    data_primeira_consulta = models.DateField(null=True, blank=True, verbose_name="Data da Primeira Consulta")
    observacoes_iniciais = models.TextField(verbose_name="Observações Iniciais", blank=True)
    
    # Status e controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['associado__nome']
    
    def __str__(self):
        return f"{self.associado.nome}"
    
    @property
    def nome_completo(self):
        """Retorna o nome completo do associado"""
        return self.associado.nome
    
    @property
    def cpf(self):
        """Retorna o CPF do associado"""
        return self.associado.cpf
    
    @property
    def email(self):
        """Retorna o email do associado"""
        return self.associado.email
    
    @property
    def telefone(self):
        """Retorna o telefone do associado"""
        return self.associado.telefone
    
    def get_psicologos_ativos(self):
        """Retorna lista de psicólogos que estão atendendo este paciente atualmente"""
        return self.psicologos.filter(
            pacientepsicologo__ativo=True
        ).order_by('-pacientepsicologo__principal', 'pacientepsicologo__data_inicio')
    
    def get_psicologo_principal(self):
        """Retorna o psicólogo principal do paciente"""
        try:
            return self.psicologos.get(
                pacientepsicologo__ativo=True,
                pacientepsicologo__principal=True
            )
        except (Psicologo.DoesNotExist, Psicologo.MultipleObjectsReturned):
            # Se não há principal ou há múltiplos, retorna o primeiro ativo
            psicologos_ativos = self.get_psicologos_ativos()
            return psicologos_ativos.first() if psicologos_ativos.exists() else None
    
    def get_psicologos_anteriores(self):
        """Retorna lista de psicólogos que já atenderam este paciente (inativos)"""
        return self.psicologos.filter(
            pacientepsicologo__ativo=False
        ).order_by('-pacientepsicologo__data_fim')
    
    def get_todos_psicologos(self):
        """Retorna todos os psicólogos que já atenderam ou estão atendendo este paciente"""
        return self.psicologos.all().order_by(
            '-pacientepsicologo__ativo',
            '-pacientepsicologo__principal',
            '-pacientepsicologo__data_inicio'
        )
    
    def pode_ser_atendido_por(self, psicologo):
        """Verifica se o paciente pode ser atendido por um psicólogo específico"""
        # Verifica se o psicólogo é o responsável atual
        if hasattr(self, 'psicologo_responsavel') and self.psicologo_responsavel:
            return self.psicologo_responsavel == psicologo
        return False
    
    def esta_sendo_atendido_por(self, psicologo):
        """Verifica se o paciente está sendo atendido atualmente por um psicólogo específico"""
        return self.psicologo_responsavel == psicologo
    
    def transferir_para_psicologo(self, novo_psicologo, motivo_transferencia="", observacoes=""):
        """Transfere o paciente para um novo psicólogo"""
        from datetime import date
        
        # Verificar se o novo psicólogo é diferente do atual
        if self.psicologo_responsavel == novo_psicologo:
            return False, "O paciente já está sendo atendido por este psicólogo"
        
        # Registrar a transferência no histórico usando PacientePsicologo
        if self.psicologo_responsavel:
            # Desativar o relacionamento atual
            PacientePsicologo.objects.filter(
                paciente=self,
                psicologo=self.psicologo_responsavel,
                ativo=True
            ).update(
                ativo=False,
                data_fim=date.today(),
                motivo_encerramento=motivo_transferencia
            )
        
        # Atualizar o psicólogo responsável
        self.psicologo_responsavel = novo_psicologo
        self.save()
        
        # Criar ou atualizar o relacionamento com o novo psicólogo
        # Primeiro, tentar encontrar um registro existente
        try:
            relacionamento_existente = PacientePsicologo.objects.get(
                paciente=self,
                psicologo=novo_psicologo
            )
            # Se existir, apenas atualizar os campos necessários
            relacionamento_existente.ativo = True
            relacionamento_existente.principal = True
            relacionamento_existente.data_inicio = date.today()
            relacionamento_existente.data_fim = None  # Remover data de fim se existir
            relacionamento_existente.motivo_inicio = f"Transferido de {self.psicologo_responsavel.nome_completo if self.psicologo_responsavel else 'Sem psicólogo'}"
            if observacoes:
                relacionamento_existente.observacoes = observacoes
            relacionamento_existente.save()
        except PacientePsicologo.DoesNotExist:
            # Se não existir, criar um novo
            PacientePsicologo.objects.create(
                paciente=self,
                psicologo=novo_psicologo,
                data_inicio=date.today(),
                ativo=True,
                principal=True,
                motivo_inicio=f"Transferido de {self.psicologo_responsavel.nome_completo if self.psicologo_responsavel else 'Sem psicólogo'}",
                observacoes=observacoes
            )
        
        return True, f"Paciente transferido com sucesso para {novo_psicologo.nome_completo}"
    
    def adicionar_psicologo(self, psicologo, principal=False, especialidade_foco="", motivo_inicio=""):
        """Método deprecated - usar transferir_para_psicologo"""
        return False, "Use o método transferir_para_psicologo para alterar o psicólogo responsável"
    
    def remover_psicologo(self, psicologo, motivo_encerramento=""):
        """Remove o psicólogo responsável pelo paciente (deixa sem psicólogo)"""
        from datetime import date
        
        if self.psicologo_responsavel != psicologo:
            return False, "Este psicólogo não é o responsável atual pelo paciente"
        
        # Registrar a remoção no histórico usando PacientePsicologo
        # Verificar se já existe um registro para este paciente e psicólogo
        try:
            relacionamento_existente = PacientePsicologo.objects.get(
                paciente=self,
                psicologo=psicologo
            )
            # Se existir, apenas atualizar os campos necessários
            relacionamento_existente.ativo = False
            relacionamento_existente.principal = False
            relacionamento_existente.data_fim = date.today()
            relacionamento_existente.motivo_encerramento = motivo_encerramento
            relacionamento_existente.observacoes = "Psicólogo removido do atendimento"
            relacionamento_existente.save()
        except PacientePsicologo.DoesNotExist:
            # Se não existir, criar um novo registro inativo
            PacientePsicologo.objects.create(
                paciente=self,
                psicologo=psicologo,
                data_inicio=date.today(),
                ativo=False,
                principal=False,
                data_fim=date.today(),
                motivo_encerramento=motivo_encerramento,
                observacoes="Psicólogo removido do atendimento"
            )
        
        # Remover o psicólogo responsável
        self.psicologo_responsavel = None
        self.save()
        
        return True, "Psicólogo removido com sucesso do atendimento"
    
    @property
    def tem_sessoes_realizadas(self):
        """Verifica se o paciente possui sessões realizadas"""
        from .models import Sessao
        return Sessao.objects.filter(
            paciente=self,
            status='realizada'
        ).exists()


class PacientePsicologo(models.Model):
    """Modelo intermediário para relação many-to-many entre paciente e psicólogo"""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, verbose_name="Psicólogo")
    data_inicio = models.DateField(verbose_name="Data de Início do Atendimento")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim do Atendimento")
    ativo = models.BooleanField(default=True, verbose_name="Atendimento Ativo")
    principal = models.BooleanField(default=False, verbose_name="Psicólogo Principal")
    especialidade_foco = models.CharField(max_length=200, blank=True, verbose_name="Especialidade/Foco do Atendimento")
    motivo_inicio = models.TextField(blank=True, verbose_name="Motivo do Início do Atendimento")
    motivo_encerramento = models.TextField(blank=True, verbose_name="Motivo do Encerramento")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Paciente-Psicólogo"
        verbose_name_plural = "Relacionamentos Paciente-Psicólogo"
        ordering = ['-data_inicio']
        # Removido unique_together para permitir histórico de transferências
        indexes = [
            models.Index(fields=['paciente', 'ativo']),
            models.Index(fields=['psicologo', 'ativo']),
        ]
    
    def __str__(self):
        status = "Ativo" if self.ativo else "Encerrado"
        principal = " (Principal)" if self.principal else ""
        return f"{self.paciente} ↔ {self.psicologo} - {status}{principal}"
    
    def save(self, *args, **kwargs):
        # Se este é o psicólogo principal, remover principal de outros
        if self.principal:
            PacientePsicologo.objects.filter(
                paciente=self.paciente,
                principal=True
            ).exclude(id=self.id).update(principal=False)
        super().save(*args, **kwargs)


class PsicologoResponsavel(models.Model):
    """Modelo para rastrear histórico de psicólogos responsáveis por pacientes (DEPRECATED - usar PacientePsicologo)"""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, verbose_name="Psicólogo")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    motivo_transferencia = models.TextField(blank=True, verbose_name="Motivo da Transferência")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    ativo = models.BooleanField(default=False, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Psicólogo Responsável (Deprecated)"
        verbose_name_plural = "Psicólogos Responsáveis (Deprecated)"
        ordering = ['-data_inicio']
        unique_together = ['paciente', 'psicologo', 'data_inicio']
    
    def __str__(self):
        return f"{self.paciente} - {self.psicologo} ({self.data_inicio})"
    
    def save(self, *args, **kwargs):
        # Se este registro está sendo ativado, desativar outros
        if self.ativo:
            PsicologoResponsavel.objects.filter(
                paciente=self.paciente,
                ativo=True
            ).exclude(id=self.id).update(ativo=False)
        super().save(*args, **kwargs)


class Sessao(models.Model):
    """Modelo para registro de sessões psicológicas"""
    TIPO_SESSAO_CHOICES = [
        ('avaliacao', 'Avaliação'),
        ('terapia', 'Terapia'),
        ('retorno', 'Retorno'),
        ('emergencial', 'Emergencial'),
    ]
    
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('remarcada', 'Remarcada'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, verbose_name="Psicólogo")
    data_hora = models.DateTimeField(verbose_name="Data e Hora")
    duracao = models.IntegerField(
        default=50, 
        validators=[MinValueValidator(30), MaxValueValidator(120)],
        verbose_name="Duração (minutos)"
    )
    tipo_sessao = models.CharField(
        max_length=20, 
        choices=TIPO_SESSAO_CHOICES, 
        default='terapia',
        verbose_name="Tipo de Sessão"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='agendada',
        verbose_name="Status"
    )
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    valor = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Valor"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Sessão"
        verbose_name_plural = "Sessões"
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.paciente} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class Prontuario(models.Model):
    """Modelo para prontuário eletrônico do paciente - Padrão de Clínica Psicológica Profissional"""
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    
    # Seção 1: Queixa e Motivo da Consulta
    queixa_principal = models.TextField(verbose_name="Queixa Principal", help_text="Motivo principal que levou o paciente a buscar atendimento")
    queixas_secundarias = models.TextField(verbose_name="Queixas Secundárias", blank=True, help_text="Outros sintomas ou problemas relatados")
    expectativas_tratamento = models.TextField(verbose_name="Expectativas do Tratamento", blank=True, help_text="O que o paciente espera alcançar")
    
    # Seção 2: Histórico Clínico
    historico_familiar = models.TextField(verbose_name="Histórico Familiar", blank=True, help_text="Histórico familiar relevante para o caso")
    historico_pessoal = models.TextField(verbose_name="Histórico Pessoal", blank=True, help_text="Experiências e vivências do paciente")
    historico_medico = models.TextField(verbose_name="Histórico Médico", blank=True, help_text="Doenças, medicações, tratamentos médicos")
    historico_psicologico = models.TextField(verbose_name="Histórico Psicológico", blank=True, help_text="Tratamentos psicológicos anteriores, diagnósticos")
    
    # Seção 3: Avaliação Psicológica
    hipotese_diagnostica = models.TextField(verbose_name="Hipótese Diagnóstica", blank=True, help_text="Impressão clínica inicial")
    sintomas_principais = models.TextField(verbose_name="Sintomas Principais", blank=True, help_text="Sintomas mais relevantes para a avaliação")
    fatores_estressores = models.TextField(verbose_name="Fatores Estressores", blank=True, help_text="Principais fontes de estresse")
    recursos_coping = models.TextField(verbose_name="Recursos de Coping", blank=True, help_text="Estratégias para lidar com problemas")
    
    # Seção 4: Plano Terapêutico
    plano_terapeutico = models.TextField(verbose_name="Plano Terapêutico", blank=True, help_text="Estratégias e técnicas de intervenção")
    objetivos_tratamento = models.TextField(verbose_name="Objetivos do Tratamento", blank=True, help_text="Objetivos específicos e mensuráveis")
    tecnicas_intervencao = models.TextField(verbose_name="Técnicas de Intervenção", blank=True, help_text="Técnicas específicas que serão utilizadas")
    prazo_estimado = models.TextField(verbose_name="Prazo Estimado", blank=True, help_text="Prazo estimado para o tratamento")
    
    # Seção 5: Observações e Considerações
    observacoes_gerais = models.TextField(verbose_name="Observações Gerais", blank=True, help_text="Observações gerais sobre o caso")
    consideracoes_especiais = models.TextField(verbose_name="Considerações Especiais", blank=True, help_text="Aspectos que merecem atenção especial")
    recomendacoes = models.TextField(verbose_name="Recomendações", blank=True, help_text="Recomendações para paciente e familiares")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Prontuário"
        verbose_name_plural = "Prontuários"
    
    def __str__(self):
        return f"Prontuário de {self.paciente}"


class Evolucao(models.Model):
    """Modelo para evoluções das sessões"""
    sessao = models.ForeignKey(Sessao, on_delete=models.CASCADE, verbose_name="Sessão")
    data_evolucao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Evolução")
    conteudo = models.TextField(verbose_name="Conteúdo da Evolução")
    observacoes_terapeuta = models.TextField(verbose_name="Observações do Terapeuta", blank=True)
    proximos_passos = models.TextField(verbose_name="Próximos Passos", blank=True)
    
    class Meta:
        verbose_name = "Evolução"
        verbose_name_plural = "Evoluções"
        ordering = ['-data_evolucao']
    
    def __str__(self):
        if self.data_evolucao:
            return f"Evolução - {self.sessao.paciente} - {self.data_evolucao.strftime('%d/%m/%Y')}"
        else:
            return f"Evolução - {self.sessao.paciente} - Nova"


class Documento(models.Model):
    """Modelo para documentos do paciente"""
    TIPO_DOCUMENTO_CHOICES = [
        ('laudo', 'Laudo'),
        ('relatorio', 'Relatório'),
        ('atestado', 'Atestado'),
        ('outro', 'Outro'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, verbose_name="Psicólogo")
    tipo = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    arquivo = models.FileField(upload_to='documentos_psicologia/', verbose_name="Arquivo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.paciente}"


class Agenda(models.Model):
    """Modelo para agenda de horários dos psicólogos"""
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE, verbose_name="Psicólogo")
    data = models.DateField(verbose_name="Data")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(verbose_name="Hora de Fim")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível")
    observacoes = models.TextField(verbose_name="Observações", blank=True)
    
    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"
        ordering = ['data', 'hora_inicio']
        unique_together = ['psicologo', 'data', 'hora_inicio']
    
    def __str__(self):
        return f"{self.psicologo} - {self.data} {self.hora_inicio}"
