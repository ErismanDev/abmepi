from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

User = get_user_model()

def validar_numero_processo_cnj(value):
    """
    Valida se o número do processo está no padrão CNJ
    Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
    Exemplo: 0001234-56.2024.8.26.0001
    """
    # Remove espaços e converte para maiúsculo
    numero = value.strip().upper()
    
    # Padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
    pattern = r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$'
    
    if not re.match(pattern, numero):
        raise ValidationError(
            'Número do processo deve estar no padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO '
            '(exemplo: 0001234-56.2024.8.26.0001)'
        )
    
    return numero

# Choices para tipos de demandas
TIPOS_DEMANDA = [
    ('civil', 'Civil'),
    ('trabalhista', 'Trabalhista'),
    ('previdenciario', 'Previdenciário'),
    ('penal', 'Penal'),
    ('administrativo', 'Administrativo'),
    ('tributario', 'Tributário'),
    ('ambiental', 'Ambiental'),
    ('consumidor', 'Consumidor'),
    ('familia', 'Família'),
    ('sucessoes', 'Sucessões'),
    ('contratos', 'Contratos'),
    ('propriedade', 'Propriedade'),
    ('outros', 'Outros'),
]

# Choices para status dos atendimentos
STATUS_ATENDIMENTO = [
    ('aberto', 'Aberto'),
    ('em_analise', 'Em Análise'),
    ('em_andamento', 'Em Andamento'),
    ('aguardando_documentos', 'Aguardando Documentos'),
    ('aguardando_decisao', 'Aguardando Decisão'),
    ('suspenso', 'Suspenso'),
    ('concluido', 'Concluído'),
    ('arquivado', 'Arquivado'),
    ('cancelado', 'Cancelado'),
]

# Choices para prioridades
PRIORIDADES = [
    ('baixa', 'Baixa'),
    ('media', 'Média'),
    ('alta', 'Alta'),
    ('urgente', 'Urgente'),
    ('critica', 'Crítica'),
]

# Choices para tipos de documentos
TIPOS_DOCUMENTO = [
    ('peticao', 'Petição'),
    ('contrato', 'Contrato'),
    ('procuração', 'Procuração'),
    ('documento_identidade', 'Documento de Identidade'),
    ('comprovante', 'Comprovante'),
    ('laudo', 'Laudo'),
    ('parecer', 'Parecer'),
    ('sentenca', 'Sentença'),
    ('acordao', 'Acórdão'),
    ('outros', 'Outros'),
]

# Choices para tipos de consultas
TIPOS_CONSULTA = [
    ('duvida_juridica', 'Dúvida Jurídica'),
    ('orientacao_legal', 'Orientação Legal'),
    ('analise_documento', 'Análise de Documento'),
    ('consulta_processo', 'Consulta de Processo'),
    ('orientacao_trabalhista', 'Orientação Trabalhista'),
    ('orientacao_previdenciaria', 'Orientação Previdenciária'),
    ('orientacao_civil', 'Orientação Civil'),
    ('outros', 'Outros'),
]

# Choices para tipos de relatórios
TIPOS_RELATORIO = [
    ('mensal', 'Mensal'),
    ('trimestral', 'Trimestral'),
    ('semestral', 'Semestral'),
    ('anual', 'Anual'),
    ('especial', 'Especial'),
    ('outros', 'Outros'),
]

# Choices para escopo do relatório
ESCOPO_RELATORIO = [
    ('total', 'Total Geral'),
    ('por_advogado', 'Por Advogado Específico'),
]


class Advogado(models.Model):
    user = models.OneToOneField(
        'core.Usuario', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='advogado',
        verbose_name='Usuário do Sistema'
    )
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    oab = models.CharField(max_length=20, unique=True)
    uf_oab = models.CharField(max_length=2)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    celular = models.CharField(max_length=20, blank=True)
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    foto = models.ImageField(
        upload_to='assejus/advogados/fotos/',
        null=True,
        blank=True,
        verbose_name='Foto'
    )
    especialidades = models.CharField(max_length=200, blank=True)
    data_inscricao_oab = models.DateField()
    experiencia_anos = models.PositiveIntegerField()
    
    # Choices para situação
    SITUACAO_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
        ('aposentado', 'Aposentado'),
    ]
    
    situacao = models.CharField(
        max_length=20, 
        choices=SITUACAO_CHOICES,
        default='ativo'
    )
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Advogado'
        verbose_name_plural = 'Advogados'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - OAB: {self.oab}"
    
    def get_especialidades_list(self):
        """Retorna lista de especialidades separadas por vírgula"""
        if self.especialidades:
            return [esp.strip() for esp in self.especialidades.split(',') if esp.strip()]
        return []
    
    def criar_usuario_sistema(self):
        """Cria um usuário do sistema para o advogado"""
        from core.models import Usuario
        from django.contrib.auth.hashers import make_password
        
        if not self.user:
            # Usar senha padrão fixa
            senha_padrao = "12345678"
            
            # Criar usuário
            usuario = Usuario.objects.create(
                username=self.cpf,
                first_name=self.nome.split()[0] if self.nome else '',
                last_name=' '.join(self.nome.split()[1:]) if len(self.nome.split()) > 1 else '',
                email=self.email,
                password=make_password(senha_padrao),
                tipo_usuario='advogado',
                ativo=self.ativo,
                primeiro_acesso=True
            )
            
            # Associar usuário ao advogado
            self.user = usuario
            self.save(update_fields=['user'])
            
            return usuario, senha_padrao
        return self.user, None
    
    def save(self, *args, **kwargs):
        """Sobrescrever save para criar usuário automaticamente se necessário"""
        # Verificar se é uma nova instância
        is_new = self.pk is None
        
        # Salvar o advogado primeiro
        super().save(*args, **kwargs)
        
        # Se for novo e não tiver usuário, criar automaticamente
        if is_new and not self.user:
            try:
                usuario, senha = self.criar_usuario_sistema()
                if usuario:
                    pass
            except Exception as e:
                pass


class AtendimentoJuridico(models.Model):
    associado = models.ForeignKey(
        'associados.Associado', on_delete=models.CASCADE,
        related_name='atendimentos_juridicos',
        verbose_name='Associado'
    )
    tipo_demanda = models.CharField(max_length=20, choices=TIPOS_DEMANDA, verbose_name='Tipo de Demanda')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_ATENDIMENTO, default='aberto', verbose_name='Status')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADES, default='media', verbose_name='Prioridade')
    
    # Novos campos para processo judicial
    numero_processo = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Número do Processo',
        help_text='Número do processo judicial (opcional)'
    )
    comarca = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Comarca',
        help_text='Comarca onde tramita o processo (opcional)'
    )
    vara = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Vara',
        help_text='Vara judicial específica (opcional)'
    )
    
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_limite = models.DateField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    advogado_responsavel = models.ForeignKey(
        Advogado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='casos_responsavel'
    )
    usuario_responsavel = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='casos_responsavel'
    )
    resultado = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Atendimento Juridico'
        verbose_name_plural = 'Atendimentos Juridicos'
        ordering = ['-data_abertura']
    
    def __str__(self):
        return f"{self.titulo} - {self.associado.nome}"





class ProcessoJuridico(models.Model):
    SITUACAO_CHOICES = [
        ('andamento', 'Em Andamento'),
        ('suspenso', 'Suspenso'),
        ('arquivado', 'Arquivado'),
        ('transitado_julgado', 'Transitado em Julgado'),
        ('concluido', 'Concluído'),
    ]
    
    TIPO_PROCESSO_CHOICES = [
        ('judicial', 'Processo Judicial'),
        ('administrativo', 'Processo Administrativo'),
    ]
    
    TIPO_ACAO_CHOICES = [
        ('civil', 'Ação Civil'),
        ('trabalhista', 'Ação Trabalhista'),
        ('previdenciaria', 'Ação Previdenciária'),
        ('criminal', 'Ação Criminal'),
        ('administrativa', 'Ação Administrativa'),
        ('familiar', 'Ação de Família'),
        ('sucessao', 'Inventário e Sucessão'),
        ('outro', 'Outro'),
    ]
    
    TIPO_PROCESSO_ADMINISTRATIVO_CHOICES = [
        ('sindicancia', 'Sindicância'),
        ('inquerito_policial_militar', 'Inquérito Policial Militar'),
        ('processo_administrativo_ordinario', 'Processo Administrativo Ordinário'),
        ('processo_administrativo_sumario', 'Processo Administrativo Sumário'),
        ('inquerito_tecnico', 'Inquérito Técnico'),
        ('conselho_justificacao', 'Conselho de Justificação'),
        ('conselho_disciplina', 'Conselho de Disciplina'),
    ]
    
    # Dados básicos do processo
    tipo_processo = models.CharField(
        max_length=20,
        choices=TIPO_PROCESSO_CHOICES,
        default='judicial',
        verbose_name='Tipo de Processo'
    )
    numero_processo = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número do Processo',
        help_text='Para processos judiciais: formato CNJ (0001234-56.2024.8.26.0001). Para administrativos: qualquer formato.'
    )
    vara_tribunal = models.CharField(
        max_length=200,
        verbose_name='Vara/Tribunal',
        blank=True,
        null=True
    )
    tipo_acao = models.CharField(
        max_length=20,
        choices=TIPO_ACAO_CHOICES,
        verbose_name='Tipo de Ação',
        blank=True,
        null=True
    )
    tipo_processo_administrativo = models.CharField(
        max_length=50,
        choices=TIPO_PROCESSO_ADMINISTRATIVO_CHOICES,
        verbose_name='Tipo de Processo Administrativo',
        blank=True,
        null=True
    )
    unidade_militar_apuracao = models.CharField(
        max_length=200,
        verbose_name='Unidade Militar que está Apurando',
        blank=True,
        null=True,
        help_text='Nome da unidade militar responsável pela apuração do processo administrativo'
    )
    
    # Partes envolvidas
    parte_cliente = models.ForeignKey(
        'associados.Associado',
        on_delete=models.CASCADE,
        related_name='processos_como_cliente',
        verbose_name='Parte Cliente'
    )
    parte_contraria = models.CharField(
        max_length=200,
        verbose_name='Parte Contrária'
    )
    advogado_parte_contraria = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Advogado/Procurador da Parte Contrária',
        help_text='Nome do advogado ou procurador que representa a parte contrária'
    )
    
    # Advogado responsável
    advogado_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_responsavel',
        verbose_name='Advogado Responsável'
    )
    
    # Situação atual
    situacao_atual = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='andamento',
        verbose_name='Situação Atual'
    )
    
    # Metadados
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes_gerais = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações Gerais'
    )
    
    class Meta:
        verbose_name = 'Processo Jurídico'
        verbose_name_plural = 'Processos Jurídicos'
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"{self.numero_processo} - {self.parte_cliente.nome}"


class ProcuracaoAdJudicia(models.Model):
    TIPO_PODERES_CHOICES = [
        ('gerais', 'Poderes Gerais'),
        ('especificos', 'Poderes Específicos'),
        ('ambos', 'Poderes Gerais e Específicos'),
    ]
    
    # Dados do outorgante (associado)
    outorgante = models.ForeignKey(
        'associados.Associado',
        on_delete=models.CASCADE,
        related_name='procuracaoes_outorgante',
        verbose_name='Outorgante (Associado)'
    )
    
    # Dados dos outorgados (advogados)
    outorgados = models.ManyToManyField(
        'assejus.Advogado',
        related_name='procuracaoes_outorgado',
        verbose_name='Outorgado(s) (Advogado(s))'
    )
    
    # Tipo de poderes
    tipo_poderes = models.CharField(
        max_length=20,
        choices=TIPO_PODERES_CHOICES,
        default='gerais',
        verbose_name='Tipo de Poderes'
    )
    
    # Processo específico (se poderes específicos)
    processo_especifico = models.ForeignKey(
        'assejus.ProcessoJuridico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='procuracaoes_especificas',
        verbose_name='Processo Específico (Cadastrado)',
        help_text='Processo cadastrado no sistema (opcional)'
    )
    numero_processo_especifico = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número do Processo Específico',
        help_text='Número do processo para poderes específicos (pode ser digitado livremente)'
    )
    
    # Dados adicionais do outorgante (preenchidos automaticamente, mas editáveis)
    cargo_militar = models.CharField(
        max_length=100,
        verbose_name='Cargo Militar',
        help_text='Ex: 1º Sargento Policial Militar'
    )
    matricula_funcional = models.CharField(
        max_length=50,
        verbose_name='Matrícula Funcional',
        help_text='Ex: 079966-1'
    )
    rgpmpi = models.CharField(
        max_length=50,
        verbose_name='RGPMPI',
        help_text='Ex: 1010528-92'
    )
    endereco_completo = models.TextField(
        verbose_name='Endereço Completo',
        help_text='Endereço completo do outorgante'
    )
    telefone_contato = models.CharField(
        max_length=20,
        verbose_name='Telefone de Contato',
        help_text='Ex: 86 99472-1952'
    )
    email_contato = models.EmailField(
        verbose_name='E-mail de Contato',
        help_text='E-mail do outorgante'
    )
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    usuario_criacao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='procuracaoes_criadas',
        verbose_name='Usuário que Criou'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações Adicionais'
    )
    
    # Texto personalizado da procuração
    texto_personalizado = models.TextField(
        blank=True,
        null=True,
        verbose_name='Texto Personalizado da Procuração',
        help_text='Deixe em branco para usar o texto padrão. Use as variáveis: {outorgante_nome}, {outorgante_cpf}, {outorgante_cargo}, {outorgante_matricula}, {outorgante_rgpmpi}, {outorgante_endereco}, {outorgante_telefone}, {outorgante_email}, {outorgados_nomes}, {outorgados_oab}, {processo_numero}, {processo_vara}, {data_atual}'
    )
    
    class Meta:
        verbose_name = 'Procuração Ad Judicia'
        verbose_name_plural = 'Procurações Ad Judicia'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Procuração - {self.outorgante.nome} para {', '.join([adv.nome for adv in self.outorgados.all()])}"
    
    @property
    def outorgados_nomes(self):
        """Retorna os nomes dos advogados outorgados"""
        return ', '.join([adv.nome for adv in self.outorgados.all()])
    
    @property
    def outorgados_oab(self):
        """Retorna as OABs dos advogados outorgados"""
        return ', '.join([f"{adv.oab}/{adv.uf_oab}" for adv in self.outorgados.all()])
    
    def get_texto_procuracao(self):
        """Retorna o texto da procuração, personalizado ou padrão"""
        if self.texto_personalizado:
            return self.texto_personalizado
        
        # Texto padrão da procuração
        from datetime import datetime
        
        # Dados do outorgante (usar dados do associado se campos estiverem vazios)
        outorgante_nome = self.outorgante.nome
        outorgante_cpf = self.outorgante.cpf
        outorgante_cargo = self.cargo_militar or getattr(self.outorgante, 'cargo_militar', '')
        outorgante_matricula = self.matricula_funcional or getattr(self.outorgante, 'matricula_funcional', '')
        outorgante_rgpmpi = self.rgpmpi or getattr(self.outorgante, 'rgpmpi', '')
        outorgante_endereco = self.endereco_completo or f"{self.outorgante.endereco}, {self.outorgante.bairro}, {self.outorgante.cidade} - {self.outorgante.estado}, CEP: {self.outorgante.cep}"
        outorgante_telefone = self.telefone_contato or self.outorgante.telefone
        outorgante_email = self.email_contato or self.outorgante.email
        
        # Dados dos outorgados
        outorgados_nomes = self.outorgados_nomes
        outorgados_oab = self.outorgados_oab
        outorgados_lista = list(self.outorgados.all())
        
        # Dados do processo (se específico)
        if self.processo_especifico:
            processo_numero = self.processo_especifico.numero_processo
            processo_vara = self.processo_especifico.vara_tribunal
        elif self.numero_processo_especifico:
            processo_numero = self.numero_processo_especifico
            processo_vara = "Vara competente"  # Texto genérico
        else:
            processo_numero = ""
            processo_vara = ""
        
        # Data atual
        data_atual = datetime.now().strftime("%d de %B de %Y")
        
        # Texto padrão
        # Obter naturalidade do associado (usar campo naturalidade se disponível)
        naturalidade = self.outorgante.naturalidade or 'não informado'
        
        texto_padrao = f"""<b>OUTORGANTE:</b> <b>{outorgante_nome}</b>, brasileiro, casado, natural de {naturalidade}, lotado no cargo de {outorgante_cargo}, matrícula funcional nº {outorgante_matricula}, portador do RGPMPI nº. {outorgante_rgpmpi} e CPF nº {outorgante_cpf}, com endereço eletrônico: {outorgante_email} e contato telefônico: {outorgante_telefone}, residente e domiciliado na {outorgante_endereco}.

<b>OUTORGADO(S):</b>"""
        
        # Adicionar dados de cada outorgado individualmente
        for i, advogado in enumerate(outorgados_lista):
            if i > 0:
                texto_padrao += "\n\n"
            
            # Dados do advogado
            advogado_nome = advogado.nome
            advogado_oab = f"{advogado.oab}/{advogado.uf_oab}"
            advogado_endereco = advogado.endereco or "endereço não informado"
            advogado_telefone = advogado.telefone or "telefone não informado"
            advogado_email = advogado.email or "e-mail não informado"
            
            texto_padrao += f""" <b>{advogado_nome}</b>, brasileiro, advogado, inscrito na OAB, sob o nº {advogado_oab}, com escritório profissional na {advogado_endereco}, telefone: {advogado_telefone}, e-mail: {advogado_email}."""

        # Adicionar poderes gerais
        texto_padrao += """

<b>PODERES GERAIS:</b> poderes, in solidum ou separadamente, para receber citações iniciais, confessar, reconhecer a procedência do(s) pedido(s), renunciar ao(s) direito(s) sobre que se funda(m) a(s) ação(ões), acionar, desistir, transigir, transacionar, passar recibos e dar quitação, em juízo ou extrajudicialmente, sobre o(s) negócio(s) do(s) outorgante(s) no que lhes for incumbido, podendo requerer, alegar, defender todo(s) seu(s) direito(s) e justiça, em quaisquer demandas ou causas cíveis ou criminais, movidas ou por mover contra o(s) outorgante(s), em que seja(m) autor(es) ou réu(s), fazendo citar, oferecer ações, libelos, exceções, embargos, suspeição ou outros quaisquer artigos, contrariar, produzir, inquirir testemunhas, assistir aos termos de inventários e partilhas, assinando termo de inventariante, partilhas amigáveis, concordar com avaliações, cálculos e descrições de bens, ou impugná-los, assinar autos, requerimento, protestos, contra protestos e termos, ainda os de confissão, negação, louvação, desistência, apelar, agravar, ou embargar qualquer sentença ou despacho e seguir destes recursos até maior alçada; fazer extrair sentenças, requerer a execução delas, sequestros, pedir precatórias, tomar posse, vir com embargos de terceiros senhor e possuidor, fazer representações criminais e queixas crimes, enfim, tudo fazer para fiel desempenho deste mandato, no que for de interesse do(s) outorgante(s) mesmo com cláusulas que não estejam expressas neste instrumento, que adota(m) e ratifica(m), para todos os efeitos de direito, inclusive substabelecer."""

        # Adicionar poderes específicos se necessário
        if self.tipo_poderes in ['especificos', 'ambos'] and (self.processo_especifico or self.numero_processo_especifico):
            texto_padrao += f"""

<b>PODERES ESPECÍFICOS:</b> para defender seus direitos e interesses perante o Processo nº. {processo_numero} que ora tramita na {processo_vara}."""


        return texto_padrao
    
    @property
    def ultimo_andamento(self):
        """Retorna o último andamento do processo"""
        return self.andamentos.first()
    
    @property
    def total_andamentos(self):
        """Retorna o total de andamentos do processo"""
        return self.andamentos.count()


class Andamento(models.Model):
    TIPO_ANDAMENTO_CHOICES = [
        ('audiencia', 'Audiência'),
        ('despacho', 'Despacho'),
        ('prazo', 'Prazo'),
        ('sentenca', 'Sentença'),
        ('recurso', 'Recurso'),
        ('contato', 'Contato'),
        ('documento', 'Documento'),
        ('outro', 'Outro'),
    ]
    
    # Relacionamento com o processo
    processo = models.ForeignKey(
        ProcessoJuridico,
        on_delete=models.CASCADE,
        related_name='andamentos',
        null=True,
        blank=True
    )
    
    # Dados do andamento
    data_andamento = models.DateTimeField(
        verbose_name='Data do Andamento'
    )
    descricao_detalhada = models.TextField(
        verbose_name='Descrição Detalhada',
        help_text='Descrição completa do que aconteceu (ex.: audiência realizada, prazo protocolado, sentença publicada)'
    )
    tipo_andamento = models.CharField(
        max_length=20,
        choices=TIPO_ANDAMENTO_CHOICES,
        verbose_name='Tipo de Andamento'
    )
    
    # Anexos
    anexos = models.ManyToManyField(
        'DocumentoJuridico',
        blank=True,
        related_name='andamentos',
        verbose_name='Anexos'
    )
    
    # Usuário que registrou
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='andamentos_registrados',
        verbose_name='Usuário que Registrou'
    )
    
    # Observações para o cliente
    observacoes_cliente = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações para o Cliente',
        help_text='Explicação simplificada do ocorrido em linguagem acessível'
    )
    
    # Controle de visualização
    cliente_visualizou = models.BooleanField(
        default=False,
        verbose_name='Cliente Visualizou'
    )
    data_visualizacao_cliente = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Visualização pelo Cliente'
    )
    
    # Metadados
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Andamento'
        verbose_name_plural = 'Andamentos'
        ordering = ['-data_andamento']
    
    def __str__(self):
        return f"{self.processo.numero_processo} - {self.get_tipo_andamento_display()} - {self.data_andamento.strftime('%d/%m/%Y')}"
    
    def marcar_como_visualizado(self):
        """Marca o andamento como visualizado pelo cliente"""
        from django.utils import timezone
        self.cliente_visualizou = True
        self.data_visualizacao_cliente = timezone.now()
        self.save(update_fields=['cliente_visualizou', 'data_visualizacao_cliente'])


class DocumentoJuridico(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('peticao', 'Petição'),
        ('sentenca', 'Sentença'),
        ('despacho', 'Despacho'),
        ('certidao', 'Certidão'),
        ('contrato', 'Contrato'),
        ('comprovante', 'Comprovante'),
        ('outro', 'Outro'),
    ]
    
    # Dados do documento
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título do Documento'
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name='Tipo de Documento'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    # Arquivo
    arquivo = models.FileField(
        upload_to='documentos_juridicos/%Y/%m/',
        verbose_name='Arquivo',
        help_text='Formatos aceitos: PDF, DOC, DOCX, JPG, PNG (máx. 10MB)'
    )
    
    # Relacionamentos
    processo = models.ForeignKey(
        ProcessoJuridico,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Processo',
        null=True,
        blank=True
    )
    
    # Metadados
    data_upload = models.DateTimeField(auto_now_add=True)
    usuario_upload = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_upload',
        verbose_name='Usuário que Fez Upload'
    )
    
    class Meta:
        verbose_name = 'Documento Jurídico'
        verbose_name_plural = 'Documentos Jurídicos'
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.titulo} - {self.processo.numero_processo}"
    
    @property
    def tamanho_arquivo(self):
        """Retorna o tamanho do arquivo em formato legível"""
        if self.arquivo:
            size = self.arquivo.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "0 B"


class ConsultaJuridica(models.Model):
    associado = models.ForeignKey(
        'associados.Associado', on_delete=models.CASCADE,
        related_name='consultas_juridicas',
        verbose_name='Associado'
    )
    tipo = models.CharField(max_length=30, choices=TIPOS_CONSULTA, verbose_name='Tipo de Consulta')
    pergunta = models.TextField()
    resposta = models.TextField(blank=True)
    data_consulta = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    advogado_responsavel = models.ForeignKey(
        'Advogado', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='consultas_responsavel',
        verbose_name='Advogado Responsável'
    )
    usuario_resposta = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='consultas_respondidas'
    )
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pendente', 'Pendente'),
            ('em_analise', 'Em Análise'),
            ('respondida', 'Respondida'),
            ('arquivada', 'Arquivada')
        ],
        default='pendente',
        verbose_name='Status'
    )
    prioridade = models.CharField(
        max_length=20,
        choices=[
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente')
        ],
        default='media',
        verbose_name='Prioridade'
    )
    resolvida = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Consulta Juridica'
        verbose_name_plural = 'Consultas Juridicas'
        ordering = ['-data_consulta']
    
    def __str__(self):
        return f"{self.associado.nome} - {self.tipo}"
    
    def marcar_como_respondida(self):
        """Marca a consulta como respondida"""
        self.status = 'respondida'
        self.resolvida = True
        self.data_resposta = timezone.now()
        self.save()


class RelatorioJuridico(models.Model):
    tipo = models.CharField(max_length=30, choices=TIPOS_RELATORIO, verbose_name='Tipo de Relatório')
    escopo = models.CharField(max_length=20, choices=ESCOPO_RELATORIO, default='total', verbose_name='Escopo do Relatório')
    advogado = models.ForeignKey(
        'Advogado', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='relatorios_por_advogado', verbose_name='Advogado Específico'
    )
    periodo_inicio = models.DateField(verbose_name='Data de Início')
    periodo_fim = models.DateField(verbose_name='Data de Fim')
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Geração')
    usuario_geracao = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='relatorios_gerados', verbose_name='Usuário de Geração'
    )
    
    class Meta:
        verbose_name = 'Relatorio Juridico'
        verbose_name_plural = 'Relatorios Juridicos'
        ordering = ['-data_geracao']
    
    def __str__(self):
        if self.escopo == 'por_advogado' and self.advogado:
            return f"{self.tipo} - {self.advogado.nome} - {self.periodo_inicio} a {self.periodo_fim}"
        return f"{self.tipo} - {self.periodo_inicio} a {self.periodo_fim}"
    
    def get_escopo_display(self):
        """Retorna o nome do escopo do relatório"""
        if self.escopo == 'por_advogado' and self.advogado:
            return f"Por Advogado: {self.advogado.nome}"
        return "Total Geral"
