from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import (
    Advogado, AtendimentoJuridico, DocumentoJuridico,
    Andamento, ConsultaJuridica, RelatorioJuridico,
    ProcessoJuridico, ProcuracaoAdJudicia
)

User = get_user_model()


class AdvogadoSearchForm(forms.Form):
    """
    Formulário de busca para advogados
    """
    nome = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome'
        })
    )
    
    cpf = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX.XXX.XXX-XX'
        })
    )
    
    oab = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número OAB'
        })
    )
    
    uf_oab = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas as UFs')] + [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
            ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
            ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    situacao = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas as situações'),
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('suspenso', 'Suspenso'),
            ('aposentado', 'Aposentado'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os estados')] + [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
            ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
            ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    ativo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('true', 'Ativo'),
            ('false', 'Inativo')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class AdvogadoForm(forms.ModelForm):
    # Lista de UFs dos estados brasileiros
    UF_CHOICES = [
        ('', '---------'),
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]
    
    # Redefinir campos para usar choices
    uf_oab = forms.ChoiceField(
        choices=UF_CHOICES,
        label='UF OAB',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'style': 'pointer-events: auto !important; cursor: pointer !important;',
            'data-placeholder': 'Selecione a UF'
        })
    )
    
    estado = forms.ChoiceField(
        choices=UF_CHOICES,
        label='Estado',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'style': 'pointer-events: auto !important; cursor: pointer !important;',
            'data-placeholder': 'Selecione o Estado'
        })
    )
    
    # Usar choices do modelo
    situacao = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('suspenso', 'Suspenso'),
            ('aposentado', 'Aposentado'),
        ],
        label='Situação',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'style': 'pointer-events: auto !important; cursor: pointer !important;',
            'data-placeholder': 'Selecione a Situação'
        })
    )
    
    # Tornar especialidades opcional
    especialidades = forms.CharField(
        label='Especialidades',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Direito Civil, Trabalhista...'
        })
    )
    
    class Meta:
        model = Advogado
        fields = [
            'nome', 'cpf', 'oab', 'uf_oab', 'email', 'telefone', 'celular',
            'endereco', 'cidade', 'estado', 'cep', 'foto', 'especialidades',
            'data_inscricao_oab', 'experiencia_anos', 'situacao', 'ativo', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX.XXX.XXX-XX'}),
            'oab': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o número da OAB'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 9999-9999'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'especialidades': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Separadas por vírgula'}),
            'data_inscricao_oab': forms.DateInput(
                attrs={
                    'class': 'form-control', 
                    'type': 'date',
                    'placeholder': 'DD/MM/AAAA'
                },
                format='%Y-%m-%d'
            ),
            'experiencia_anos': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 100,
                'placeholder': 'Ex: 5'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurações adicionais podem ser adicionadas aqui se necessário
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome or nome.strip() == '':
            raise forms.ValidationError('Nome é obrigatório. Digite o nome completo do advogado.')
        if len(nome.strip()) < 3:
            raise forms.ValidationError('Nome deve ter pelo menos 3 caracteres. Digite o nome completo.')
        return nome.strip()
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf or cpf.strip() == '':
            raise forms.ValidationError('CPF é obrigatório. Digite um CPF válido no formato XXX.XXX.XXX-XX.')
        
        # Remove caracteres não numéricos
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos numéricos. Use o formato XXX.XXX.XXX-XX.')
        
        # Verificar se todos os dígitos são iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            raise forms.ValidationError('CPF inválido. Todos os dígitos não podem ser iguais.')
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        if resto < 2:
            dv1 = 0
        else:
            dv1 = 11 - resto
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        if resto < 2:
            dv2 = 0
        else:
            dv2 = 11 - resto
        
        # Verifica se os dígitos verificadores estão corretos
        if cpf_limpo[9] != str(dv1) or cpf_limpo[10] != str(dv2):
            raise forms.ValidationError('CPF inválido. Verifique os dígitos verificadores.')
        
        # Verificar se o CPF já existe
        from .models import Advogado
        if self.instance.pk:  # Se for edição
            existing = Advogado.objects.filter(cpf=cpf).exclude(pk=self.instance.pk)
        else:  # Se for criação
            existing = Advogado.objects.filter(cpf=cpf)
        
        if existing.exists():
            raise forms.ValidationError('Já existe um advogado cadastrado com este CPF.')
        
        # Formata o CPF
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_formatado
    
    def clean_oab(self):
        oab = self.cleaned_data.get('oab')
        if not oab or oab.strip() == '':
            raise forms.ValidationError('OAB é obrigatória. Digite o número da OAB.')
        if len(oab.strip()) < 3:
            raise forms.ValidationError('OAB deve ter pelo menos 3 caracteres.')
        return oab.strip()
    
    def clean_uf_oab(self):
        uf_oab = self.cleaned_data.get('uf_oab')
        if not uf_oab or uf_oab == '':
            raise forms.ValidationError('UF OAB é obrigatória. Selecione o estado da OAB.')
        return uf_oab
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or email.strip() == '':
            raise forms.ValidationError('E-mail é obrigatório. Digite um endereço de e-mail válido.')
        
        # Verificar formato básico de email
        if '@' not in email or '.' not in email:
            raise forms.ValidationError('E-mail deve ter formato válido. Exemplo: exemplo@dominio.com')
        
        # Verificar se o email já existe
        from .models import Advogado
        if self.instance.pk:  # Se for edição
            existing = Advogado.objects.filter(email=email).exclude(pk=self.instance.pk)
        else:  # Se for criação
            existing = Advogado.objects.filter(email=email)
        
        if existing.exists():
            raise forms.ValidationError('Já existe um advogado cadastrado com este e-mail.')
        return email.strip()
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone or telefone.strip() == '':
            raise forms.ValidationError('Telefone é obrigatório. Digite um número de telefone válido.')
        if len(telefone.strip()) < 10:
            raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos. Use o formato (11) 9999-9999')
        return telefone.strip()
    
    def clean_endereco(self):
        endereco = self.cleaned_data.get('endereco')
        if not endereco or endereco.strip() == '':
            raise forms.ValidationError('Endereço é obrigatório. Digite o endereço completo incluindo rua, número e bairro.')
        if len(endereco.strip()) < 10:
            raise forms.ValidationError('Endereço deve ter pelo menos 10 caracteres. Digite o endereço completo incluindo rua, número e bairro.')
        return endereco.strip()
    
    def clean_cidade(self):
        cidade = self.cleaned_data.get('cidade')
        if not cidade or cidade.strip() == '':
            raise forms.ValidationError('Cidade é obrigatória. Digite o nome completo da cidade.')
        if len(cidade.strip()) < 2:
            raise forms.ValidationError('Cidade deve ter pelo menos 2 caracteres. Digite o nome completo da cidade.')
        return cidade.strip()
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if not estado or estado == '':
            raise forms.ValidationError('Estado é obrigatório. Selecione o estado da lista.')
        return estado
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep or cep.strip() == '':
            raise forms.ValidationError('CEP é obrigatório. Digite um CEP válido no formato XXXXX-XXX.')
        
        # Remove caracteres não numéricos
        cep_limpo = ''.join(filter(str.isdigit, cep))
        if len(cep_limpo) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos numéricos. Use o formato XXXXX-XXX.')
        
        # Formata o CEP
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_formatado
    
    def clean_data_inscricao_oab(self):
        data_inscricao = self.cleaned_data.get('data_inscricao_oab')
        if not data_inscricao:
            raise forms.ValidationError('Data de inscrição na OAB é obrigatória. Selecione a data de inscrição.')
        
        # Verificar se a data não é no futuro
        from django.utils import timezone
        if data_inscricao > timezone.now().date():
            raise forms.ValidationError('Data de inscrição não pode ser no futuro. Selecione uma data válida.')
        
        # Verificar se a data não é muito antiga (mais de 100 anos atrás)
        from datetime import date
        data_minima = date.today().replace(year=date.today().year - 100)
        if data_inscricao < data_minima:
            raise forms.ValidationError('Data de inscrição não pode ser há mais de 100 anos. Verifique a data informada.')
        
        return data_inscricao
    
    def clean_experiencia_anos(self):
        experiencia = self.cleaned_data.get('experiencia_anos')
        if experiencia is None or experiencia == '':
            raise forms.ValidationError('Anos de experiência é obrigatório. Digite o número de anos de experiência.')
        
        try:
            experiencia = int(experiencia)
        except (ValueError, TypeError):
            raise forms.ValidationError('Anos de experiência deve ser um número válido. Digite apenas números.')
        
        if experiencia < 0:
            raise forms.ValidationError('Anos de experiência não pode ser negativo. Digite um valor válido.')
        if experiencia > 100:
            raise forms.ValidationError('Anos de experiência não pode ser maior que 100. Verifique o valor informado.')
        
        return experiencia
    
    def clean_situacao(self):
        situacao = self.cleaned_data.get('situacao')
        if not situacao or situacao == '':
            raise forms.ValidationError('Situação é obrigatória. Selecione a situação da lista.')
        return situacao
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validações adicionais que dependem de múltiplos campos
        cpf = cleaned_data.get('cpf')
        oab = cleaned_data.get('oab')
        uf_oab = cleaned_data.get('uf_oab')
        
        if cpf and oab and uf_oab:
            # Verificar se a combinação OAB + UF já existe
            from .models import Advogado
            if self.instance.pk:  # Se for edição
                existing = Advogado.objects.filter(oab=oab, uf_oab=uf_oab).exclude(pk=self.instance.pk)
            else:  # Se for criação
                existing = Advogado.objects.filter(oab=oab, uf_oab=uf_oab)
            
            if existing.exists():
                raise forms.ValidationError('Já existe um advogado cadastrado com esta OAB nesta UF.')
        
        # Validação adicional para telefone e celular
        telefone = cleaned_data.get('telefone')
        celular = cleaned_data.get('celular')
        
        if telefone and celular and telefone == celular:
            raise forms.ValidationError('Telefone e celular não podem ser iguais.')
        
        # Validação para CEP e estado (removida para simplificar)
        # Esta validação estava causando problemas e não é essencial
        
        return cleaned_data


class AtendimentoJuridicoForm(forms.ModelForm):
    class Meta:
        model = AtendimentoJuridico
        fields = [
            'associado', 'tipo_demanda', 'titulo', 'descricao', 'status',
            'prioridade', 'numero_processo', 'comarca', 'vara', 'data_limite', 
            'advogado_responsavel', 'resultado', 'observacoes'
        ]
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'tipo_demanda': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'numero_processo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 0001234-12.2023.8.26.0100'
            }),
            'comarca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: São Paulo'
            }),
            'vara': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1ª Vara Cível'
            }),
            'data_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'format': '%Y-%m-%d'}),
            'advogado_responsavel': forms.Select(attrs={'class': 'form-control'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas advogados ativos
        self.fields['advogado_responsavel'].queryset = Advogado.objects.filter(ativo=True)
        
        # Carrega a lista de associados ativos
        try:
            from associados.models import Associado
            self.fields['associado'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
        except ImportError:
            # Se o app associados não estiver disponível, mantém o campo como está
            pass
        
        # Adiciona choices para os campos
        from .models import TIPOS_DEMANDA, STATUS_ATENDIMENTO, PRIORIDADES
        self.fields['tipo_demanda'].choices = [('', '---------')] + list(TIPOS_DEMANDA)
        self.fields['status'].choices = [('', '---------')] + list(STATUS_ATENDIMENTO)
        self.fields['prioridade'].choices = [('', '---------')] + list(PRIORIDADES)





class ProcessoJuridicoForm(forms.ModelForm):
    class Meta:
        model = ProcessoJuridico
        fields = [
            'tipo_processo', 'numero_processo', 'vara_tribunal', 'tipo_acao',
            'tipo_processo_administrativo', 'unidade_militar_apuracao',
            'parte_cliente', 'parte_contraria', 'advogado_parte_contraria',
            'advogado_responsavel', 'situacao_atual', 'observacoes_gerais'
        ]
        widgets = {
            'tipo_processo': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleProcessoFields()'
            }),
            'numero_processo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0001234-56.2024.8.26.0001',
                'id': 'id_numero_processo'
            }),
            'vara_tribunal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1ª Vara Cível de São Paulo'
            }),
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'tipo_processo_administrativo': forms.Select(attrs={'class': 'form-select'}),
            'unidade_militar_apuracao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1º Batalhão de Polícia Militar'
            }),
            'parte_cliente': forms.Select(attrs={'class': 'form-select'}),
            'parte_contraria': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_parte_contraria'
            }),
            'advogado_parte_contraria': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_advogado_parte_contraria',
                'placeholder': 'Nome do advogado/procurador da parte contrária'
            }),
            'advogado_responsavel': forms.Select(attrs={'class': 'form-select'}),
            'situacao_atual': forms.Select(attrs={'class': 'form-select'}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar advogados responsáveis (usuários com tipo 'advogado')
        self.fields['advogado_responsavel'].queryset = User.objects.filter(
            tipo_usuario='advogado'
        ).order_by('first_name', 'last_name')
        
        # Adicionar classes CSS aos campos
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_numero_processo(self):
        numero_processo = self.cleaned_data.get('numero_processo')
        tipo_processo = self.cleaned_data.get('tipo_processo')
        
        if not numero_processo:
            raise forms.ValidationError('Número do processo é obrigatório.')
        
        # Validação específica para processos judiciais (formato CNJ)
        if tipo_processo == 'judicial':
            # Remove espaços e converte para maiúsculo
            numero_limpo = numero_processo.strip().upper()
            
            # Validação do formato CNJ
            import re
            pattern_cnj = r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$'
            if not re.match(pattern_cnj, numero_limpo):
                raise forms.ValidationError(
                    'Para processos judiciais, o número deve seguir o formato CNJ: 0001234-56.2024.8.26.0001'
                )
            
            return numero_limpo
        
        # Para processos administrativos, aceita qualquer formato
        elif tipo_processo == 'administrativo':
            return numero_processo.strip()
        
        return numero_processo.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_processo = cleaned_data.get('tipo_processo')
        vara_tribunal = cleaned_data.get('vara_tribunal')
        tipo_acao = cleaned_data.get('tipo_acao')
        tipo_processo_administrativo = cleaned_data.get('tipo_processo_administrativo')
        unidade_militar_apuracao = cleaned_data.get('unidade_militar_apuracao')
        
        # Validações para processos judiciais
        if tipo_processo == 'judicial':
            if not vara_tribunal:
                self.add_error('vara_tribunal', 'Vara/Tribunal é obrigatório para processos judiciais.')
            if not tipo_acao:
                self.add_error('tipo_acao', 'Tipo de Ação é obrigatório para processos judiciais.')
        
        # Validações para processos administrativos
        elif tipo_processo == 'administrativo':
            if not tipo_processo_administrativo:
                self.add_error('tipo_processo_administrativo', 'Tipo de Processo Administrativo é obrigatório.')
            if not unidade_militar_apuracao:
                self.add_error('unidade_militar_apuracao', 'Unidade Militar que está Apurando é obrigatória.')
        
        return cleaned_data
    



class AndamentoForm(forms.ModelForm):
    class Meta:
        model = Andamento
        fields = [
            'processo', 'data_andamento', 'descricao_detalhada', 'tipo_andamento',
            'observacoes_cliente'
        ]
        widgets = {
            'processo': forms.Select(attrs={'class': 'form-select'}),
            'data_andamento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'descricao_detalhada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descreva detalhadamente o que aconteceu (ex.: audiência realizada, prazo protocolado, sentença publicada)'
            }),
            'tipo_andamento': forms.Select(attrs={'class': 'form-select'}),
            'observacoes_cliente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explicação simplificada do ocorrido em linguagem acessível para o cliente'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class DocumentoJuridicoForm(forms.ModelForm):
    class Meta:
        model = DocumentoJuridico
        fields = ['titulo', 'tipo_documento', 'descricao', 'arquivo', 'processo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'processo': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair atendimento_id e processo_id se fornecidos
        atendimento_id = kwargs.pop('atendimento_id', None)
        processo_id = kwargs.pop('processo_id', None)
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Se processo_id foi fornecido, pré-selecionar o processo
        if processo_id:
            try:
                from .models import ProcessoJuridico
                processo = ProcessoJuridico.objects.get(pk=processo_id)
                self.fields['processo'].queryset = ProcessoJuridico.objects.filter(pk=processo_id)
                self.fields['processo'].initial = processo_id
                self.processo_info = processo
            except ProcessoJuridico.DoesNotExist:
                pass
        
        # Se atendimento_id foi fornecido, filtrar processos relacionados
        elif atendimento_id:
            try:
                from .models import AtendimentoJuridico, ProcessoJuridico
                atendimento = AtendimentoJuridico.objects.get(pk=atendimento_id)
                
                # Buscar processos relacionados ao associado do atendimento
                processos_relacionados = ProcessoJuridico.objects.filter(
                    parte_cliente=atendimento.associado
                )
                
                self.fields['processo'].queryset = processos_relacionados
                
                # Adicionar informações do associado para exibição
                self.associado_info = atendimento.associado
                
            except AtendimentoJuridico.DoesNotExist:
                pass
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Validar tamanho do arquivo (10MB)
            if arquivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('O arquivo deve ter no máximo 10MB.')
            
            # Validar tipo do arquivo
            extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            import os
            extensao = os.path.splitext(arquivo.name)[1].lower()
            if extensao not in extensoes_permitidas:
                raise forms.ValidationError(
                    f'Formato não permitido. Use: {", ".join(extensoes_permitidas)}'
                )
        return arquivo


class ConsultaJuridicaForm(forms.ModelForm):
    class Meta:
        model = ConsultaJuridica
        fields = [
            'associado', 'tipo', 'pergunta', 'advogado_responsavel', 
            'status', 'prioridade', 'resposta', 'resolvida'
        ]
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'pergunta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'advogado_responsavel': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'resposta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resolvida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carrega a lista de associados ativos
        try:
            from associados.models import Associado
            self.fields['associado'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
        except ImportError:
            # Se o app associados não estiver disponível, mantém o campo como está
            pass
        
        # Filtra apenas advogados ativos
        self.fields['advogado_responsavel'].queryset = Advogado.objects.filter(ativo=True).order_by('nome')
        
        # Adiciona choices para os campos
        from .models import TIPOS_CONSULTA
        self.fields['tipo'].choices = [('', '---------')] + list(TIPOS_CONSULTA)
        
        # Configura as choices para status e prioridade
        self.fields['status'].choices = [
            ('', '---------'),
            ('pendente', 'Pendente'),
            ('em_analise', 'Em Análise'),
            ('respondida', 'Respondida'),
            ('arquivada', 'Arquivada')
        ]
        
        self.fields['prioridade'].choices = [
            ('', '---------'),
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente')
        ]


class RelatorioJuridicoForm(forms.ModelForm):
    class Meta:
        model = RelatorioJuridico
        fields = ['tipo', 'escopo', 'advogado', 'periodo_inicio', 'periodo_fim']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'escopo': forms.Select(attrs={'class': 'form-control'}),
            'advogado': forms.Select(attrs={'class': 'form-control'}),
            'periodo_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona choices para o campo tipo
        from .models import TIPOS_RELATORIO, ESCOPO_RELATORIO
        self.fields['tipo'].choices = [('', '---------')] + list(TIPOS_RELATORIO)
        self.fields['escopo'].choices = [('', '---------')] + list(ESCOPO_RELATORIO)
        
        # Filtra apenas advogados ativos
        from .models import Advogado
        self.fields['advogado'].queryset = Advogado.objects.filter(ativo=True).order_by('nome')
        self.fields['advogado'].choices = [('', '---------')] + list(self.fields['advogado'].queryset.values_list('id', 'nome'))
        
        # Adiciona JavaScript para mostrar/ocultar campo advogado baseado no escopo
        self.fields['escopo'].widget.attrs.update({
            'onchange': 'toggleAdvogadoField()',
            'class': 'form-control'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        periodo_inicio = cleaned_data.get('periodo_inicio')
        periodo_fim = cleaned_data.get('periodo_fim')
        escopo = cleaned_data.get('escopo')
        advogado = cleaned_data.get('advogado')
        
        if periodo_inicio and periodo_fim:
            if periodo_inicio > periodo_fim:
                raise forms.ValidationError('A data de início deve ser anterior à data de fim')
        
        if escopo == 'por_advogado' and not advogado:
            raise forms.ValidationError('Quando o escopo for "Por Advogado Específico", é obrigatório selecionar um advogado.')
        
        return cleaned_data


class ProcuracaoAdJudiciaForm(forms.ModelForm):
    class Meta:
        model = ProcuracaoAdJudicia
        fields = [
            'outorgante', 'outorgados', 'tipo_poderes', 'processo_especifico',
            'numero_processo_especifico', 'cargo_militar', 'matricula_funcional', 'rgpmpi', 'endereco_completo',
            'telefone_contato', 'email_contato', 'texto_personalizado', 'observacoes'
        ]
        widgets = {
            'outorgante': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'preencherDadosOutorgante()'
            }),
            'outorgados': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'tipo_poderes': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleProcessoEspecifico()'
            }),
            'processo_especifico': forms.Select(attrs={'class': 'form-select'}),
            'numero_processo_especifico': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_numero_processo_especifico',
                'placeholder': 'Ex: 0001234-56.2024.8.22.0001'
            }),
            'cargo_militar': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_cargo_militar',
                'placeholder': 'Ex: 1º Sargento Policial Militar'
            }),
            'matricula_funcional': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_matricula_funcional',
                'placeholder': 'Ex: 079966-1'
            }),
            'rgpmpi': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_rgpmpi',
                'placeholder': 'Ex: 1010528-92'
            }),
            'endereco_completo': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_endereco_completo',
                'rows': 3,
                'placeholder': 'Ex: Rua Vereador Joel Loureiro, nº. 7906, Bairro Cidade Jardim, CEP: 64066-050 em Teresina– PI'
            }),
            'telefone_contato': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_telefone_contato',
                'placeholder': 'Ex: 86 99472-1952'
            }),
            'email_contato': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'id_email_contato',
                'placeholder': 'Ex: 94721952aristeu@gmail.com'
            }),
            'texto_personalizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Deixe em branco para usar o texto padrão. Use as variáveis disponíveis.'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre a procuração'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar associados ativos
        try:
            from associados.models import Associado
            self.fields['outorgante'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
        except ImportError:
            pass
        
        # Filtrar advogados ativos
        self.fields['outorgados'].queryset = Advogado.objects.filter(ativo=True).order_by('nome')
        
        # Filtrar processos ativos para poderes específicos
        self.fields['processo_especifico'].queryset = ProcessoJuridico.objects.filter(
            situacao_atual__in=['andamento', 'suspenso']
        ).order_by('-data_cadastro')
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_poderes = cleaned_data.get('tipo_poderes')
        processo_especifico = cleaned_data.get('processo_especifico')
        numero_processo_especifico = cleaned_data.get('numero_processo_especifico')
        outorgados = cleaned_data.get('outorgados')
        
        # Validação: pelo menos um advogado deve ser selecionado
        if not outorgados:
            self.add_error('outorgados', 'É obrigatório selecionar pelo menos um advogado.')
        
        # Validação: processo específico é obrigatório para poderes específicos
        if tipo_poderes in ['especificos', 'ambos']:
            if not processo_especifico and not numero_processo_especifico:
                self.add_error('numero_processo_especifico', 'É obrigatório informar o número do processo para poderes específicos.')
        
        return cleaned_data
