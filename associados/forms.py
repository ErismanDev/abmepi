from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import Associado, Documento, Dependente
from .models import PreCadastroAssociado


class AssociadoForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de associados
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popular as opções do campo usuario
        from core.models import Usuario
        self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True)
        self.fields['usuario'].empty_label = "Selecione um usuário (opcional)"
        self.fields['usuario'].required = False
        
        # Configurar campos de data para garantir que funcionem corretamente
        if self.instance and self.instance.pk:
            # Se estamos editando, garantir que as datas sejam formatadas corretamente
            if self.instance.data_nascimento:
                self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%Y-%m-%d')
            if self.instance.data_ingresso:
                self.initial['data_ingresso'] = self.instance.data_ingresso.strftime('%Y-%m-%d')
    
    class Meta:
        model = Associado
        fields = [
            'nome', 'cpf', 'rg', 'data_nascimento', 'sexo', 'foto', 'estado_civil',
            'naturalidade', 'nacionalidade', 'email', 'telefone', 'celular', 'cep', 'rua', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'nome_pai', 'nome_mae', 'tipo_socio', 'tipo_profissional', 'matricula_militar', 'posto_graduacao',
            'nome_civil', 'unidade_lotacao', 'data_ingresso', 'situacao', 'tipo_documento', 'usuario', 'ativo', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX.XXX.XXX-XX',
                'data-mask': '000.000.000-00'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o RG'
            }),
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'dd/mm/aaaa'
                }
            ),
            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o e-mail'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(XX) XXXX-XXXX',
                'data-mask': '(00) 0000-0000'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(XX) XXXXX-XXXX',
                'data-mask': '(00) 00000-0000'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXX-XXX',
                'data-mask': '00000-000'
            }),
            'rua': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da rua'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartamento, bloco, etc.'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_socio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_profissional': forms.Select(attrs={
                'class': 'form-select'
            }),
            'matricula_militar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o número da matrícula militar'
            }),
            'posto_graduacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome_civil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome civil (se diferente do nome militar)'
            }),
            'unidade_lotacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a unidade de lotação'
            }),
            'data_ingresso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'dd/mm/aaaa'
                }
            ),
            'situacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais'
            }),
            'usuario': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecione um usuário'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do pai'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da mãe'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove pontos e traços para validação
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Verifica se tem 11 dígitos
            if len(cpf_limpo) != 11:
                raise forms.ValidationError('CPF deve ter 11 dígitos.')
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                raise forms.ValidationError('CPF inválido.')
            
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
                raise forms.ValidationError('CPF inválido.')
        
        return cpf

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            # Remove traços para validação
            cep_limpo = cep.replace('-', '')
            if len(cep_limpo) != 8 or not cep_limpo.isdigit():
                raise forms.ValidationError('CEP deve ter 8 dígitos numéricos.')
        return cep

    def clean_ativo(self):
        """
        Limpeza específica para o campo ativo
        """
        ativo = self.cleaned_data.get('ativo')
        print(f"DEBUG: Campo ativo recebido: {ativo}")
        print(f"DEBUG: Tipo do campo ativo: {type(ativo)}")
        
        # Se o campo não foi enviado, definir como False
        if ativo is None:
            print("DEBUG: Campo ativo é None, definindo como False")
            return False
        
        # Se o campo foi enviado como string vazia, definir como False
        if ativo == '':
            print("DEBUG: Campo ativo é string vazia, definindo como False")
            return False
        
        # Se o campo foi enviado como 'on' (checkbox marcado), definir como True
        if ativo == 'on':
            print("DEBUG: Campo ativo é 'on', definindo como True")
            return True
        
        # Se o campo foi enviado como True/False, manter o valor
        print(f"DEBUG: Campo ativo mantido como: {ativo}")
        return ativo


class AssociadoSearchForm(forms.Form):
    """
    Formulário de busca para associados
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
    
    matricula_militar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matrícula militar'
        })
    )
    
    situacao = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas as situações')] + Associado.SITUACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os estados')] + Associado.ESTADOS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tipo_socio = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + Associado.TIPO_SOCIO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tipo_profissional = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os profissionais')] + Associado.TIPO_PROFISSIONAL_CHOICES,
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
    
    nome_pai = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome do pai'
        })
    )
    
    nome_mae = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome da mãe'
        })
    )
    
    tipo_documento = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + Associado.TIPO_DOCUMENTO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class DocumentoForm(forms.ModelForm):
    """
    Formulário para upload de documentos
    """
    class Meta:
        model = Documento
        fields = ['tipo', 'arquivo', 'descricao', 'tipo_personalizado']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do documento'
            }),
            'tipo_personalizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o tipo de documento',
                'id': 'id_tipo_personalizado'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair associado_id e dependente_id se fornecidos
        associado_id = kwargs.pop('associado_id', None)
        dependente_id = kwargs.pop('dependente_id', None)
        
        super().__init__(*args, **kwargs)
        
        # Se um associado específico foi fornecido, configurar o campo
        if associado_id:
            try:
                associado = Associado.objects.get(pk=associado_id)
                # Armazenar o associado para uso posterior
                self.associado = associado
                # Adicionar informação sobre o associado
                self.associado_info = associado
                # Remover o campo associado completamente - é intrínseco
                if 'associado' in self.fields:
                    del self.fields['associado']
                if 'dependente' in self.fields:
                    del self.fields['dependente']
            except Associado.DoesNotExist:
                pass
        
        # Se um dependente específico foi fornecido, configurar o campo
        elif dependente_id:
            try:
                dependente = Dependente.objects.get(pk=dependente_id)
                # Armazenar o dependente para uso posterior
                self.dependente = dependente
                # Adicionar informação sobre o dependente
                self.dependente_info = dependente
                # Remover os campos associado/dependente completamente - são intrínsecos
                if 'associado' in self.fields:
                    del self.fields['associado']
                if 'dependente' in self.fields:
                    del self.fields['dependente']
            except Dependente.DoesNotExist:
                pass
        
        # Se nenhum contexto específico foi fornecido, manter campos ocultos
        else:
            self.fields['associado'] = forms.ModelChoiceField(
                queryset=Associado.objects.all(),
                required=False,
                widget=forms.HiddenInput()
            )
            self.fields['dependente'] = forms.ModelChoiceField(
                queryset=Dependente.objects.all(),
                required=False,
                widget=forms.HiddenInput()
            )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        tipo_personalizado = cleaned_data.get('tipo_personalizado')
        
        # Se o tipo for "outro", o campo tipo_personalizado é obrigatório
        if tipo == 'outro' and not tipo_personalizado:
            raise forms.ValidationError({
                'tipo_personalizado': 'Por favor, especifique o tipo de documento.'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Salvar o documento com o associado/dependente correto"""
        documento = super().save(commit=False)
        
        # Se o associado foi definido no __init__, usar ele
        if hasattr(self, 'associado'):
            documento.associado = self.associado
            documento.dependente = None
        
        # Se o dependente foi definido no __init__, usar ele
        elif hasattr(self, 'dependente'):
            documento.dependente = self.dependente
            documento.associado = self.dependente.associado
        
        if commit:
            documento.save()
        
        return documento

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Verifica o tamanho do arquivo (máximo 10MB)
            if arquivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('O arquivo deve ter no máximo 10MB.')
            
            # Verifica a extensão do arquivo
            extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            import os
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError('Formato de arquivo não suportado. Use PDF, DOC, DOCX, JPG ou PNG.')
        
        return arquivo


class DependenteForm(forms.ModelForm):
    """
    Formulário para cadastro de dependentes
    """
    class Meta:
        model = Dependente
        fields = ['nome', 'parentesco', 'data_nascimento', 'foto', 'cpf', 'email', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do dependente'
            }),
            'parentesco': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'dd/mm/aaaa'
                }
            ),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX.XXX.XXX-XX (opcional)',
                'data-mask': '000.000.000-00'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-mail do dependente (opcional)'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações sobre o dependente'
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove pontos e traços para validação
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Verifica se tem 11 dígitos
            if len(cpf_limpo) != 11:
                raise forms.ValidationError('CPF deve ter 11 dígitos.')
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                raise forms.ValidationError('CPF inválido.')
            
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
                raise forms.ValidationError('CPF inválido.')
        
        return cpf


class AssociadoBulkActionForm(forms.Form):
    """
    Formulário para ações em lote
    """
    ACTION_CHOICES = [
        ('ativar', 'Ativar selecionados'),
        ('desativar', 'Desativar selecionados'),
        ('exportar', 'Exportar selecionados'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    associados = forms.CharField(
        widget=forms.HiddenInput()
    )


class PreCadastroAssociadoForm(forms.ModelForm):
    """
    Formulário para pré-cadastro de associados
    """
    class Meta:
        model = PreCadastroAssociado
        fields = [
            'nome', 'cpf', 'rg', 'data_nascimento', 'sexo', 'foto',
            'estado_civil', 'naturalidade', 'nacionalidade', 'email', 'telefone', 'celular',
            'cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'tipo_profissao', 'posto_graduacao', 'orgao', 'matricula', 
            'nome_pai', 'nome_mae', 'situacao', 'tipo_documento', 'observacoes',
            'copia_rg', 'copia_cpf', 'comprovante_residencia'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX.XXX.XXX-XX',
                'data-mask': '000.000.000-00'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu RG'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 9999-9999',
                'data-mask': '(00) 00000-0000'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'data-mask': '(00) 00000-0000'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXX-XXX',
                'data-mask': '00000-000'
            }),
            'rua': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rua'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartamento, bloco, etc.'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
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
            ]),
            'nacionalidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Brasileira',
                'value': 'Brasileira'
            }),
            'tipo_profissao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'posto_graduacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Soldado, Cabo, Sargento, etc.'
            }),
            'orgao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Corpo de Bombeiros, Polícia Militar'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sua matrícula funcional'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do pai'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da mãe'
            }),
            'situacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            }),
            'copia_rg': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'copia_cpf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'comprovante_residencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Bootstrap para campos obrigatórios
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' required'
        
        # Tornar campos de documentos obrigatórios
        self.fields['copia_rg'].required = True
        self.fields['copia_cpf'].required = True
        self.fields['comprovante_residencia'].required = True
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remover caracteres especiais para validação
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            
            # Verificar se já existe um associado com este CPF
            if Associado.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError('Já existe um associado cadastrado com este CPF.')
            
            # Verificar se já existe um pré-cadastro com este CPF
            if PreCadastroAssociado.objects.filter(cpf=cpf).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('Já existe um pré-cadastro com este CPF.')
        
        return cpf
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se já existe um associado com este email
            if Associado.objects.filter(email=email).exists():
                raise forms.ValidationError('Já existe um associado cadastrado com este email.')
            
            # Verificar se já existe um pré-cadastro com este email
            if PreCadastroAssociado.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('Já existe um pré-cadastro com este email.')
        
        return email
    
    def clean_copia_rg(self):
        arquivo = self.cleaned_data.get('copia_rg')
        if arquivo:
            # Verificar tamanho do arquivo (5MB máximo)
            if arquivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('O arquivo do RG deve ter no máximo 5MB.')
            
            # Verificar extensão do arquivo
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError('Formato de arquivo não permitido. Use PDF, JPG, JPEG, PNG, DOC ou DOCX.')
        
        return arquivo
    
    def clean_copia_cpf(self):
        arquivo = self.cleaned_data.get('copia_cpf')
        if arquivo:
            # Verificar tamanho do arquivo (5MB máximo)
            if arquivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('O arquivo do CPF deve ter no máximo 5MB.')
            
            # Verificar extensão do arquivo
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError('Formato de arquivo não permitido. Use PDF, JPG, JPEG, PNG, DOC ou DOCX.')
        
        return arquivo
    
    def clean_comprovante_residencia(self):
        arquivo = self.cleaned_data.get('comprovante_residencia')
        if arquivo:
            # Verificar tamanho do arquivo (5MB máximo)
            if arquivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('O comprovante de residência deve ter no máximo 5MB.')
            
            # Verificar extensão do arquivo
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            if not any(arquivo.name.lower().endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError('Formato de arquivo não permitido. Use PDF, JPG, JPEG, PNG, DOC ou DOCX.')
        
        return arquivo
