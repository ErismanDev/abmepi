from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from core.models import Usuario
from django.core.exceptions import ValidationError


class Associado(models.Model):
    """
    Modelo principal para cadastro de associados
    """
    # Dados pessoais
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome Completo')
    )
    
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        verbose_name=_('CPF')
    )
    
    rg = models.CharField(
        max_length=20,
        verbose_name=_('RG')
    )
    
    data_nascimento = models.DateField(
        verbose_name=_('Data de Nascimento')
    )
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name=_('Sexo')
    )
    
    foto = models.ImageField(
        upload_to='associados/fotos/',
        null=True,
        blank=True,
        verbose_name=_('Foto')
    )
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        verbose_name=_('Estado Civil')
    )
    
    # Naturalidade e Nacionalidade
    naturalidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Naturalidade (Cidade/Estado)')
    )
    
    nacionalidade = models.CharField(
        max_length=50,
        default='Brasileira',
        verbose_name=_('Nacionalidade')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail')
    )
    
    telefone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Telefone')
    )
    
    celular = models.CharField(
        max_length=15,
        verbose_name=_('Celular')
    )
    
    # Endereço
    cep = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='CEP deve estar no formato XXXXX-XXX'
            )
        ],
        verbose_name=_('CEP')
    )
    
    rua = models.CharField(
        max_length=200,
        verbose_name=_('Rua')
    )
    
    numero = models.CharField(
        max_length=10,
        verbose_name=_('Número')
    )
    
    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Complemento')
    )
    
    bairro = models.CharField(
        max_length=100,
        verbose_name=_('Bairro')
    )
    
    cidade = models.CharField(
        max_length=100,
        verbose_name=_('Cidade')
    )
    
    ESTADOS_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]
    estado = models.CharField(
        max_length=2,
        choices=ESTADOS_CHOICES,
        verbose_name=_('Estado')
    )
    
    # Dados funcionais
    TIPO_SOCIO_CHOICES = [
        ('fundador', 'Sócio Fundador'),
        ('benemerito', 'Sócio Benemérito'),
        ('contribuinte', 'Sócio Contribuinte'),
    ]
    tipo_socio = models.CharField(
        max_length=20,
        choices=TIPO_SOCIO_CHOICES,
        default='contribuinte',
        verbose_name=_('Tipo de Sócio')
    )
    
    TIPO_PROFISSIONAL_CHOICES = [
        ('bombeiro_militar', 'Bombeiro Militar'),
        ('policial_militar', 'Policial Militar'),
        ('civil', 'Civil'),
    ]
    tipo_profissional = models.CharField(
        max_length=20,
        choices=TIPO_PROFISSIONAL_CHOICES,
        default='bombeiro_militar',
        verbose_name=_('Tipo de Profissional')
    )
    
    matricula_militar = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Número da Matrícula Militar')
    )
    
    POSTO_GRADUACAO_CHOICES = [
        # Bombeiros Militares
        ('soldado_bm', 'Soldado BM'),
        ('cabo_bm', 'Cabo BM'),
        ('3sgt_bm', '3º Sargento BM'),
        ('2sgt_bm', '2º Sargento BM'),
        ('1sgt_bm', '1º Sargento BM'),
        ('subten_bm', 'Subtenente BM'),
        ('asp_bm', 'Aspirante BM'),
        ('2ten_bm', '2º Tenente BM'),
        ('1ten_bm', '1º Tenente BM'),
        ('cap_bm', 'Capitão BM'),
        ('maj_bm', 'Major BM'),
        ('ten_cel_bm', 'Tenente Coronel BM'),
        ('cel_bm', 'Coronel BM'),
        
        # Policiais Militares
        ('soldado_pm', 'Soldado PM'),
        ('cabo_pm', 'Cabo PM'),
        ('3sgt_pm', '3º Sargento PM'),
        ('2sgt_pm', '2º Sargento PM'),
        ('1sgt_pm', '1º Sargento PM'),
        ('subten_pm', 'Subtenente PM'),
        ('asp_pm', 'Aspirante PM'),
        ('2ten_pm', '2º Tenente PM'),
        ('1ten_pm', '1º Tenente PM'),
        ('cap_pm', 'Capitão PM'),
        ('maj_pm', 'Major PM'),
        ('ten_cel_pm', 'Tenente Coronel PM'),
        ('cel_pm', 'Coronel PM'),
        
        # Civis
        ('civil', 'Civil'),
        ('estudante', 'Estudante'),
        ('profissional_livre', 'Profissional Liberal'),
        ('servidor_publico', 'Servidor Público'),
        ('empresario', 'Empresário'),
        ('aposentado', 'Aposentado'),
    ]
    
    posto_graduacao = models.CharField(
        max_length=30,
        choices=POSTO_GRADUACAO_CHOICES,
        default='civil',
        verbose_name=_('Posto/Graduação')
    )
    
    nome_civil = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nome Civil (se diferente do nome militar)')
    )
    
    unidade_lotacao = models.CharField(
        max_length=100,
        verbose_name=_('Unidade de Lotação')
    )
    
    data_ingresso = models.DateField(
        verbose_name=_('Data de Ingresso')
    )
    
    SITUACAO_CHOICES = [
        ('ativo', 'Ativo'),
        ('reserva', 'Reserva'),
        ('reformado', 'Reformado'),
        ('pensionista', 'Pensionista'),
    ]
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='ativo',
        verbose_name=_('Situação')
    )
    
    # Dados dos pais
    nome_pai = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nome do Pai')
    )
    
    nome_mae = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nome da Mãe')
    )
    
    # Tipo de documento
    TIPO_DOCUMENTO_CHOICES = [
        ('rgpm', 'RGPM'),
        ('rgbm', 'RGBM'),
        ('gip', 'GIP'),
        ('rg', 'RG'),
    ]
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='rg',
        verbose_name=_('Tipo de Documento')
    )
    
    # Dados do sistema
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Usuário do Sistema')
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
        verbose_name=_('Associado Ativo')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    class Meta:
        verbose_name = _('Associado')
        verbose_name_plural = _('Associados')
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['matricula_militar']),
            models.Index(fields=['situacao']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.nome} - {self.cpf}"
    
    def get_endereco_completo(self):
        """Retorna o endereço completo formatado"""
        endereco = f"{self.rua}, {self.numero}"
        if self.complemento:
            endereco += f" - {self.complemento}"
        endereco += f" - {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep}"
        return endereco
    
    def get_idade(self):
        """Calcula a idade do associado"""
        from datetime import date
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class Documento(models.Model):
    """
    Modelo para anexar documentos digitalizados
    """
    TIPO_DOCUMENTO_CHOICES = [
        # Documentos Acadêmicos
        ('acao_civil_publica', 'Ação Civil Pública'),
        ('acao_popular', 'Ação Popular'),
        ('acordao', 'Acórdão'),
        ('ata_reuniao', 'Ata de Reunião'),
        ('atestado', 'Atestado'),
        ('atestado_medico', 'Atestado Médico'),
        ('atestado_militar', 'Atestado de Serviço Militar'),
        
        # Documentos Bancários e Financeiros
        ('boletim_ocorrencia', 'Boletim de Ocorrência'),
        
        # Documentos de Identificação
        ('carteira_trabalho', 'Carteira de Trabalho'),
        ('certificado_curso', 'Certificado de Curso'),
        ('certidao_casamento', 'Certidão de Casamento'),
        ('certidao_divorcio', 'Certidão de Divórcio'),
        ('certidao_militar', 'Certidão de Alistamento Militar'),
        ('certidao_nascimento', 'Certidão de Nascimento'),
        ('certidao_obito', 'Certidão de Óbito'),
        ('cnh', 'CNH - Carteira Nacional de Habilitação'),
        ('comprovante_residencia', 'Comprovante de Residência'),
        ('conta_agua', 'Conta de Água'),
        ('conta_luz', 'Conta de Luz'),
        ('conta_telefone', 'Conta de Telefone'),
        ('contrato_aluguel', 'Contrato de Aluguel'),
        ('contrato_social', 'Contrato Social'),
        ('contrato_trabalho', 'Contrato de Trabalho'),
        ('cpf', 'CPF'),
        
        # Documentos de Declaração
        ('declaracao', 'Declaração'),
        ('declaracao_empregador', 'Declaração do Empregador'),
        ('declaracao_matricula', 'Declaração de Matrícula'),
        ('declaracao_saude', 'Declaração de Saúde'),
        ('declaracao_servico', 'Declaração de Serviço Militar'),
        ('declaracao_veracidade', 'Declaração de Veracidade'),
        ('decisao_judicial', 'Decisão Judicial'),
        ('diploma', 'Diploma'),
        
        # Documentos de Edital e Estatuto
        ('edital', 'Edital'),
        ('escritura_imovel', 'Escritura de Imóvel'),
        ('estatuto', 'Estatuto'),
        ('exame_medico', 'Exame Médico'),
        ('extrato_bancario', 'Extrato Bancário'),
        ('extrato_fgts', 'Extrato FGTS'),
        ('extrato_inss', 'Extrato INSS'),
        
        # Documentos Jurídicos Específicos
        ('ficha_associativa', 'Ficha Associativa'),
        ('habeas_corpus', 'Habeas Corpus'),
        ('historico_escolar', 'Histórico Escolar'),
        ('inquerito_policial', 'Inquérito Policial'),
        ('mandado_seguranca', 'Mandado de Segurança'),
        
        # Documentos de Outros Tipos
        ('outro', 'Outro'),
        ('passaporte', 'Passaporte'),
        ('peticao', 'Petição'),
        ('procuracao', 'Procuração'),
        ('receita_medica', 'Receita Médica'),
        ('recurso', 'Recurso'),
        ('regimento_interno', 'Regimento Interno'),
        ('reservista', 'Certificado de Reservista'),
        ('rg', 'RG'),
        ('recibo_salario', 'Recibo de Salário'),
        
        # Documentos de Sentença e Termos
        ('sentenca', 'Sentença'),
        ('termo_compromisso', 'Termo de Compromisso'),
        ('termo_responsabilidade', 'Termo de Responsabilidade'),
        ('titulo_eleitor', 'Título de Eleitor'),
    ]
    
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name=_('Associado'),
        null=True,
        blank=True
    )
    
    dependente = models.ForeignKey(
        'Dependente',
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name=_('Dependente'),
        null=True,
        blank=True
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name=_('Tipo de Documento')
    )
    
    arquivo = models.FileField(
        upload_to='associados/documentos/',
        verbose_name=_('Arquivo')
    )
    
    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Descrição')
    )
    
    tipo_personalizado = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Tipo Personalizado'),
        help_text=_('Especifique o tipo de documento quando selecionar "Outro"')
    )
    
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data do Upload')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Documento Ativo')
    )
    
    class Meta:
        verbose_name = _('Documento')
        verbose_name_plural = _('Documentos')
        ordering = ['-data_upload']
    
    def clean(self):
        """Validação: documento deve estar associado a um associado OU dependente, não ambos"""
        # Só validar se o documento já foi salvo (tem ID) ou se ambos os campos estão preenchidos
        if self.pk or (self.associado and self.dependente):
            if not self.associado and not self.dependente:
                raise ValidationError(_('Documento deve estar associado a um associado ou dependente.'))
            if self.associado and self.dependente:
                raise ValidationError(_('Documento não pode estar associado a um associado e dependente simultaneamente.'))
    
    def __str__(self):
        tipo_display = self.get_tipo_display()
        if self.tipo == 'outro' and self.tipo_personalizado:
            tipo_display = self.tipo_personalizado
        
        if self.associado:
            return f"{self.associado.nome} - {tipo_display}"
        elif self.dependente:
            return f"{self.dependente.nome} ({self.dependente.associado.nome}) - {tipo_display}"
        return f"Documento - {tipo_display}"


class Dependente(models.Model):
    """
    Modelo para cadastro de dependentes
    """
    PARENTESCO_CHOICES = [
        ('filho', 'Filho(a)'),
        ('conjuge', 'Cônjuge'),
        ('pai', 'Pai'),
        ('mae', 'Mãe'),
        ('outro', 'Outro'),
    ]
    
    associado = models.ForeignKey(
        Associado,
        on_delete=models.CASCADE,
        related_name='dependentes',
        verbose_name=_('Associado')
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome Completo')
    )
    
    parentesco = models.CharField(
        max_length=20,
        choices=PARENTESCO_CHOICES,
        verbose_name=_('Parentesco')
    )
    
    data_nascimento = models.DateField(
        verbose_name=_('Data de Nascimento')
    )
    
    foto = models.ImageField(
        upload_to='associados/dependentes/fotos/',
        null=True,
        blank=True,
        verbose_name=_('Foto')
    )
    
    cpf = models.CharField(
        max_length=14,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        verbose_name=_('CPF')
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name=_('Dependente Ativo')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    class Meta:
        verbose_name = _('Dependente')
        verbose_name_plural = _('Dependentes')
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_parentesco_display()} - {self.associado.nome}"
    
    def get_idade(self):
        """Calcula a idade do dependente"""
        from datetime import date
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class PreCadastroAssociado(models.Model):
    """
    Modelo para pré-cadastro de associados (aguardando aprovação)
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    
    # Dados pessoais
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome Completo')
    )
    
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        verbose_name=_('CPF')
    )
    
    rg = models.CharField(
        max_length=20,
        verbose_name=_('RG')
    )
    
    data_nascimento = models.DateField(
        verbose_name=_('Data de Nascimento')
    )
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name=_('Sexo')
    )
    
    foto = models.ImageField(
        upload_to='associados/pre_cadastro/fotos/',
        null=True,
        blank=True,
        verbose_name=_('Foto')
    )
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        verbose_name=_('Estado Civil')
    )
    
    # Naturalidade e Nacionalidade
    naturalidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Naturalidade (Cidade/Estado)')
    )
    
    nacionalidade = models.CharField(
        max_length=50,
        default='Brasileira',
        verbose_name=_('Nacionalidade')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail')
    )
    
    telefone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Telefone')
    )
    
    celular = models.CharField(
        max_length=15,
        verbose_name=_('Celular')
    )
    
    # Endereço
    cep = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='CEP deve estar no formato XXXXX-XXX'
            )
        ],
        verbose_name=_('CEP')
    )
    
    rua = models.CharField(
        max_length=200,
        verbose_name=_('Rua')
    )
    
    numero = models.CharField(
        max_length=10,
        verbose_name=_('Número')
    )
    
    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Complemento')
    )
    
    bairro = models.CharField(
        max_length=100,
        verbose_name=_('Bairro')
    )
    
    cidade = models.CharField(
        max_length=100,
        verbose_name=_('Cidade')
    )
    
    estado = models.CharField(
        max_length=2,
        verbose_name=_('Estado')
    )
    
    # Dados profissionais
    TIPO_PROFISSAO_CHOICES = [
        ('bombeiro', 'Bombeiro'),
        ('policial', 'Policial'),
        ('militar', 'Militar'),
        ('civil', 'Civil'),
        ('outro', 'Outro'),
    ]
    tipo_profissao = models.CharField(
        max_length=20,
        choices=TIPO_PROFISSAO_CHOICES,
        verbose_name=_('Tipo de Profissão')
    )
    
    posto_graduacao = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Posto/Graduação')
    )
    
    orgao = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Órgão/Instituição')
    )
    
    matricula = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Matrícula')
    )
    
    # Dados dos pais
    nome_pai = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nome do Pai')
    )
    
    nome_mae = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nome da Mãe')
    )
    
    # Situação funcional
    SITUACAO_CHOICES = [
        ('ativo', 'Ativo'),
        ('reserva', 'Reserva'),
        ('reformado', 'Reformado'),
        ('pensionista', 'Pensionista'),
    ]
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='ativo',
        verbose_name=_('Situação')
    )
    
    # Tipo de documento
    TIPO_DOCUMENTO_CHOICES = [
        ('rgpm', 'RGPM'),
        ('rgbm', 'RGBM'),
        ('gip', 'GIP'),
        ('rg', 'RG'),
    ]
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='rg',
        verbose_name=_('Tipo de Documento')
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name=_('Status')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    # Documentos anexados
    copia_rg = models.FileField(
        upload_to='pre_cadastros/documentos/rg/',
        blank=True,
        null=True,
        verbose_name=_('Cópia do RG')
    )
    
    copia_cpf = models.FileField(
        upload_to='pre_cadastros/documentos/cpf/',
        blank=True,
        null=True,
        verbose_name=_('Cópia do CPF')
    )
    
    comprovante_residencia = models.FileField(
        upload_to='pre_cadastros/documentos/residencia/',
        blank=True,
        null=True,
        verbose_name=_('Comprovante de Residência')
    )
    
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data da Solicitação')
    )
    
    data_analise = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data da Análise')
    )
    
    analisado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Analisado por')
    )
    
    # Campos adicionais para aprovação
    motivo_rejeicao = models.TextField(
        blank=True,
        verbose_name=_('Motivo da Rejeição')
    )
    
    class Meta:
        verbose_name = "Pré-Cadastro de Associado"
        verbose_name_plural = "Pré-Cadastros de Associados"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.nome} - {self.cpf} ({self.get_status_display()})"
    
    def get_status_display_color(self):
        """Retorna a cor CSS para o status"""
        colors = {
            'pendente': 'warning',
            'aprovado': 'success',
            'rejeitado': 'danger',
        }
        return colors.get(self.status, 'secondary')
    
    def converter_para_associado(self, usuario_aprovador):
        """
        Converte o pré-cadastro aprovado em um associado real
        """
        from django.utils import timezone
        import shutil
        import os
        from django.conf import settings
        
        # Mapear campos do pré-cadastro para o associado
        dados_associado = {
            'nome': self.nome,
            'cpf': self.cpf,
            'rg': self.rg,
            'data_nascimento': self.data_nascimento,
            'sexo': self.sexo,
            'foto': self.foto,
            'estado_civil': self.estado_civil,
            'naturalidade': self.naturalidade,
            'nacionalidade': self.nacionalidade,
            'email': self.email,
            'telefone': self.telefone,
            'celular': self.celular,
            'cep': self.cep,
            'rua': self.rua,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'nome_pai': self.nome_pai,
            'nome_mae': self.nome_mae,
            'situacao': self.situacao,
            'tipo_documento': self.tipo_documento,
            'observacoes': f"Convertido do pré-cadastro ID: {self.id}. {self.observacoes or ''}",
        }
        
        # Mapear dados profissionais
        if self.tipo_profissao == 'bombeiro':
            dados_associado['tipo_profissional'] = 'bombeiro_militar'
            dados_associado['posto_graduacao'] = self.posto_graduacao or 'soldado_bm'
        elif self.tipo_profissao == 'policial':
            dados_associado['tipo_profissional'] = 'policial_militar'
            dados_associado['posto_graduacao'] = self.posto_graduacao or 'soldado_pm'
        else:
            dados_associado['tipo_profissional'] = 'civil'
            dados_associado['posto_graduacao'] = 'civil'
        
        # Campos específicos do associado
        dados_associado['tipo_socio'] = 'contribuinte'
        dados_associado['matricula_militar'] = self.matricula or f"PC{self.id:06d}"
        dados_associado['nome_civil'] = self.nome
        dados_associado['unidade_lotacao'] = self.orgao or 'Não informado'
        dados_associado['data_ingresso'] = timezone.now().date()
        dados_associado['situacao'] = 'ativo'
        dados_associado['ativo'] = True
        
        # Criar o associado
        associado = Associado.objects.create(**dados_associado)
        
        # Transferir dependentes do pré-cadastro para o associado
        dependentes_pre_cadastro = self.dependentes.all()
        for dep_pre in dependentes_pre_cadastro:
            Dependente.objects.create(
                associado=associado,
                nome=dep_pre.nome,
                parentesco=dep_pre.parentesco,
                data_nascimento=dep_pre.data_nascimento,
                foto=dep_pre.foto,
                cpf=dep_pre.cpf,
                email=dep_pre.email,
                observacoes=f"Transferido do pré-cadastro ID: {self.id}. {dep_pre.observacoes or ''}"
            )
        
        # Transferir documentos do pré-cadastro para o associado
        documentos_para_criar = []
        
        # RG
        if self.copia_rg:
            documentos_para_criar.append({
                'associado': associado,
                'tipo': 'rg',
                'arquivo': self.copia_rg,
                'descricao': 'Cópia do RG - Transferido do pré-cadastro'
            })
        
        # CPF
        if self.copia_cpf:
            documentos_para_criar.append({
                'associado': associado,
                'tipo': 'cpf',
                'arquivo': self.copia_cpf,
                'descricao': 'Cópia do CPF - Transferido do pré-cadastro'
            })
        
        # Comprovante de Residência
        if self.comprovante_residencia:
            documentos_para_criar.append({
                'associado': associado,
                'tipo': 'comprovante_residencia',
                'arquivo': self.comprovante_residencia,
                'descricao': 'Comprovante de Residência - Transferido do pré-cadastro'
            })
        
        # Criar os documentos
        for doc_data in documentos_para_criar:
            Documento.objects.create(**doc_data)
        
        # Atualizar o pré-cadastro
        self.status = 'aprovado'
        self.data_analise = timezone.now()
        self.analisado_por = usuario_aprovador
        self.observacoes = f"{self.observacoes or ''}\n\nAprovado e convertido para associado ID: {associado.id}. Transferidos {dependentes_pre_cadastro.count()} dependentes e {len(documentos_para_criar)} documentos."
        self.save()
        
        return associado


class DependentePreCadastro(models.Model):
    """
    Modelo para cadastro de dependentes do pré-cadastro
    """
    PARENTESCO_CHOICES = [
        ('filho', 'Filho(a)'),
        ('conjuge', 'Cônjuge'),
        ('pai', 'Pai'),
        ('mae', 'Mãe'),
        ('outro', 'Outro'),
    ]
    
    pre_cadastro = models.ForeignKey(
        PreCadastroAssociado,
        on_delete=models.CASCADE,
        related_name='dependentes',
        verbose_name=_('Pré-Cadastro')
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name=_('Nome Completo')
    )
    
    parentesco = models.CharField(
        max_length=20,
        choices=PARENTESCO_CHOICES,
        verbose_name=_('Parentesco')
    )
    
    data_nascimento = models.DateField(
        verbose_name=_('Data de Nascimento')
    )
    
    foto = models.ImageField(
        upload_to='associados/pre_cadastro/dependentes/fotos/',
        null=True,
        blank=True,
        verbose_name=_('Foto')
    )
    
    cpf = models.CharField(
        max_length=14,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        verbose_name=_('CPF')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name=_('Observações')
    )
    
    class Meta:
        verbose_name = _('Dependente do Pré-Cadastro')
        verbose_name_plural = _('Dependentes do Pré-Cadastro')
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_parentesco_display()} - {self.pre_cadastro.nome}"
    
    def get_idade(self):
        """Calcula a idade do dependente"""
        from datetime import date
        return date.today().year - self.data_nascimento.year - (
            (date.today().month, date.today().day) < 
            (self.data_nascimento.month, self.data_nascimento.day)
        )
