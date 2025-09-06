from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Psicologo, Paciente, Sessao, Prontuario, Evolucao, Documento, Agenda, PacientePsicologo


class PsicologoForm(forms.ModelForm):
    """Formulário para cadastro de psicólogos"""
    
    def clean_crp(self):
        """Valida se o CRP já não está em uso"""
        crp = self.cleaned_data.get('crp')
        if crp:
            # Verificar se já existe um psicólogo com este CRP
            queryset = Psicologo.objects.filter(crp=crp)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    f"Já existe um psicólogo cadastrado com o CRP {crp}."
                )
        return crp
    
    def clean_cpf(self):
        """Valida o CPF"""
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
            
            # Verificar se já existe um psicólogo com este CPF
            queryset = Psicologo.objects.filter(cpf=cpf)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    f"Já existe um psicólogo cadastrado com este CPF."
                )
        
        return cpf
    
    def clean_telefone(self):
        """Valida e formata o telefone"""
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remover caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Validar se tem pelo menos 10 dígitos
            if len(telefone_limpo) < 10:
                raise forms.ValidationError("Telefone deve ter pelo menos 10 dígitos.")
            
            # Formatar telefone se tiver 11 dígitos (celular)
            if len(telefone_limpo) == 11:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            # Formatar telefone se tiver 10 dígitos (fixo)
            elif len(telefone_limpo) == 10:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
            
            return telefone_limpo
        return telefone
    
    def clean_telefone_secundario(self):
        """Valida e formata o telefone secundário"""
        telefone = self.cleaned_data.get('telefone_secundario')
        if telefone:
            # Remover caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Validar se tem pelo menos 10 dígitos
            if len(telefone_limpo) < 10:
                raise forms.ValidationError("Telefone secundário deve ter pelo menos 10 dígitos.")
            
            # Formatar telefone se tiver 11 dígitos (celular)
            if len(telefone_limpo) == 11:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            # Formatar telefone se tiver 10 dígitos (fixo)
            elif len(telefone_limpo) == 10:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
            
            return telefone_limpo
        return telefone
    
    def save(self, commit=True):
        """Salvar psicólogo criando usuário automaticamente se necessário"""
        psicologo = super().save(commit=False)
        
        # Se não tem usuário associado, criar um
        if not psicologo.user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Criar username respeitando o limite de 14 caracteres
            if psicologo.cpf:
                # Usar CPF se disponível (já está no formato correto)
                username = psicologo.cpf
            else:
                # Usar CRP truncado se necessário
                crp_base = psicologo.crp.replace('/', '').replace('-', '')[:8]  # Máximo 8 caracteres
                username = f"psic_{crp_base}"[:14]  # Garantir que não exceda 14 caracteres
                
                # Se ainda assim for muito longo, usar um ID único
                if len(username) > 14:
                    import uuid
                    username = f"psic_{str(uuid.uuid4())[:8]}"[:14]
            
            password = User.objects.make_random_password()
            
            user = User.objects.create_user(
                username=username,
                email=psicologo.email,
                password=password,
                tipo_usuario='psicologo',
                is_active=True
            )
            psicologo.user = user
        
        if commit:
            psicologo.save()
        return psicologo
    
    class Meta:
        model = Psicologo
        fields = [
            'nome_completo', 'crp', 'uf_crp', 'data_nascimento', 'cpf', 'rg', 'orgao_emissor',
            'telefone', 'telefone_secundario', 'email', 'email_secundario',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'especialidades', 'formacao_academica', 'cursos_complementares', 
            'experiencia_profissional', 'areas_atuacao', 'horario_atendimento',
            'valor_consulta', 'aceita_planos_saude', 'planos_aceitos',
            'foto', 'curriculo', 'documentos_complementares', 'ativo', 'observacoes'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'crp': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_crp': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione...'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
                ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
                ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
                ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
                ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
                ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
                ('TO', 'Tocantins')
            ]),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'orgao_emissor': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'telefone_secundario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_secundario': forms.EmailInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione...'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
                ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
                ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
                ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
                ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
                ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
                ('TO', 'Tocantins')
            ]),
            'especialidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'formacao_academica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cursos_complementares': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experiencia_profissional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'areas_atuacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'horario_atendimento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_consulta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'aceita_planos_saude': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'planos_aceitos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'curriculo': forms.FileInput(attrs={'class': 'form-control'}),
            'documentos_complementares': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PacienteForm(forms.ModelForm):
    """Formulário para cadastro de pacientes"""
    
    def clean_associado(self):
        """Valida se o associado já não é paciente"""
        associado = self.cleaned_data.get('associado')
        if associado:
            # Verificar se já existe um paciente para este associado
            if Paciente.objects.filter(associado=associado).exists():
                # Se estiver editando, permitir (verificar se é o mesmo paciente)
                if self.instance and self.instance.pk:
                    paciente_existente = Paciente.objects.get(associado=associado)
                    if paciente_existente.id == self.instance.id:
                        return associado  # É o mesmo paciente, permitir
                
                # Se for novo paciente, não permitir
                raise forms.ValidationError(
                    f"O associado {associado.nome} já é paciente no sistema. "
                    "Não é possível cadastrar o mesmo associado duas vezes."
                )
        return associado
    
    class Meta:
        model = Paciente
        fields = [
            'associado', 'psicologo_responsavel', 'data_primeira_consulta', 
            'observacoes_iniciais', 'ativo'
        ]
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-select'}),
            'psicologo_responsavel': forms.Select(attrs={'class': 'form-select'}),
            'data_primeira_consulta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacoes_iniciais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SessaoForm(forms.ModelForm):
    """Formulário para agendamento de sessões"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatação especial para datetime-local quando editando
        if self.instance and self.instance.pk and self.instance.data_hora:
            # Converter para formato datetime-local (YYYY-MM-DDTHH:MM)
            formatted_datetime = self.instance.data_hora.strftime('%Y-%m-%dT%H:%M')
            self.fields['data_hora'].initial = self.instance.data_hora
            self.fields['data_hora'].widget.attrs['value'] = formatted_datetime
        
        # Definir valores padrão para novos registros
        if not self.instance.pk:
            self.fields['status'].initial = 'agendada'
            self.fields['tipo_sessao'].initial = 'terapia'
            self.fields['duracao'].initial = 50
    
    class Meta:
        model = Sessao
        fields = ['paciente', 'psicologo', 'data_hora', 'duracao', 'tipo_sessao', 'status', 'observacoes', 'valor']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'psicologo': forms.Select(attrs={'class': 'form-select'}),
            'data_hora': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'placeholder': 'Selecione data e hora',
                    'min': '2025-01-01T00:00',
                    'required': True
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'duracao': forms.NumberInput(attrs={'class': 'form-control', 'min': '30', 'max': '120', 'required': True}),
            'tipo_sessao': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'status': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SessaoFromPacienteForm(forms.ModelForm):
    """Formulário para criação de sessão a partir da ficha do paciente"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatação especial para datetime-local quando editando
        if self.instance and self.instance.pk and self.instance.data_hora:
            # Converter para formato datetime-local (YYYY-MM-DDTHH:MM)
            formatted_datetime = self.instance.data_hora.strftime('%Y-%m-%dT%H:%M')
            self.fields['data_hora'].widget.attrs['value'] = formatted_datetime
        
        # Definir valores padrão para novos registros
        if not self.instance.pk:
            self.fields['status'].initial = 'agendada'
            self.fields['tipo_sessao'].initial = 'terapia'
            self.fields['duracao'].initial = 50
    
    class Meta:
        model = Sessao
        fields = ['data_hora', 'duracao', 'tipo_sessao', 'status', 'observacoes', 'valor']
        widgets = {
            'data_hora': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'placeholder': 'Selecione data e hora',
                    'min': '2025-01-01T00:00',
                    'required': True
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'duracao': forms.NumberInput(attrs={'class': 'form-control', 'min': '30', 'max': '120', 'required': True}),
            'tipo_sessao': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'status': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ProntuarioForm(forms.ModelForm):
    """Formulário para prontuário eletrônico"""
    class Meta:
        model = Prontuario
        fields = [
            'queixa_principal', 'queixas_secundarias', 'expectativas_tratamento',
            'historico_familiar', 'historico_pessoal', 'historico_medico', 'historico_psicologico',
            'hipotese_diagnostica', 'sintomas_principais', 'fatores_estressores', 'recursos_coping',
            'plano_terapeutico', 'objetivos_tratamento', 'tecnicas_intervencao', 'prazo_estimado',
            'observacoes_gerais', 'consideracoes_especiais', 'recomendacoes'
        ]
        widgets = {
            'queixa_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'queixas_secundarias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expectativas_tratamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_familiar': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historico_pessoal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historico_medico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_psicologico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hipotese_diagnostica': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sintomas_principais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fatores_estressores': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recursos_coping': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plano_terapeutico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objetivos_tratamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tecnicas_intervencao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prazo_estimado': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'consideracoes_especiais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProntuarioFromPacienteForm(forms.ModelForm):
    """Formulário para criação de prontuário a partir da ficha do paciente"""
    class Meta:
        model = Prontuario
        fields = [
            'queixa_principal', 'queixas_secundarias', 'expectativas_tratamento',
            'historico_familiar', 'historico_pessoal', 'historico_medico', 'historico_psicologico',
            'hipotese_diagnostica', 'sintomas_principais', 'fatores_estressores', 'recursos_coping',
            'plano_terapeutico', 'objetivos_tratamento', 'tecnicas_intervencao', 'prazo_estimado',
            'observacoes_gerais', 'consideracoes_especiais', 'recomendacoes'
        ]
        widgets = {
            'queixa_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'queixas_secundarias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expectativas_tratamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_familiar': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historico_pessoal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historico_medico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historico_psicologico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hipotese_diagnostica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sintomas_principais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fatores_estressores': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recursos_coping': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plano_terapeutico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objetivos_tratamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tecnicas_intervencao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prazo_estimado': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'consideracoes_especiais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EvolucaoForm(forms.ModelForm):
    """Formulário para evoluções das sessões"""
    class Meta:
        model = Evolucao
        fields = ['sessao', 'conteudo', 'observacoes_terapeuta', 'proximos_passos']
        widgets = {
            'sessao': forms.Select(attrs={'class': 'form-select'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'observacoes_terapeuta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'proximos_passos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DocumentoForm(forms.ModelForm):
    """Formulário para documentos do paciente"""
    class Meta:
        model = Documento
        fields = ['tipo', 'titulo', 'descricao', 'arquivo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DocumentoFromPacienteForm(forms.ModelForm):
    """Formulário para criação de documento a partir da ficha do paciente"""
    class Meta:
        model = Documento
        fields = ['tipo', 'titulo', 'descricao', 'arquivo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AgendaForm(forms.ModelForm):
    """Formulário para agenda de horários"""
    
    def __init__(self, *args, **kwargs):
        # Extrair request dos kwargs antes de chamar super()
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Se for psicólogo, definir automaticamente o psicólogo da agenda
        if self.request and self.request.user.tipo_usuario == 'psicologo' and hasattr(self.request.user, 'psicologo'):
            self.fields['psicologo'].initial = self.request.user.psicologo
        
        # Configurar widgets com valores iniciais corretos
        if self.instance and self.instance.pk:
            # Para edição, garantir que os valores sejam formatados corretamente
            if self.instance.data:
                self.fields['data'].initial = self.instance.data
                self.fields['data'].widget.attrs['value'] = self.instance.data.strftime('%Y-%m-%d')
            if self.instance.hora_inicio:
                self.fields['hora_inicio'].initial = self.instance.hora_inicio
                self.fields['hora_inicio'].widget.attrs['value'] = self.instance.hora_inicio.strftime('%H:%M')
            if self.instance.hora_fim:
                self.fields['hora_fim'].initial = self.instance.hora_fim
                self.fields['hora_fim'].widget.attrs['value'] = self.instance.hora_fim.strftime('%H:%M')
    
    class Meta:
        model = Agenda
        fields = ['psicologo', 'data', 'hora_inicio', 'hora_fim', 'disponivel', 'observacoes']
        widgets = {
            'psicologo': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': 'Selecione uma data'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time',
                'placeholder': 'Selecione a hora de início'
            }),
            'hora_fim': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time',
                'placeholder': 'Selecione a hora de fim'
            }),
            'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Observações sobre o horário...'
            }),
        }


class SessaoFilterForm(forms.Form):
    """Formulário para filtros de sessões"""
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os pacientes",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Paciente'
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data de Início'
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Data de Fim'
    )
    psicologo = forms.ModelChoiceField(
        queryset=Psicologo.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os psicólogos",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Psicólogo'
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Sessao.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status'
    )
    tipo_sessao = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Sessao.TIPO_SESSAO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Sessão'
    )


class PacientePsicologoForm(forms.ModelForm):
    """Formulário para gerenciar relacionamento paciente-psicólogo"""
    
    class Meta:
        model = PacientePsicologo
        fields = ['psicologo', 'data_inicio', 'principal', 'especialidade_foco', 'motivo_inicio', 'observacoes']
        widgets = {
            'psicologo': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'especialidade_foco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Terapia Cognitivo-Comportamental'}),
            'motivo_inicio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo do início do atendimento...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações adicionais...'}),
        }
        
        help_texts = {
            'principal': 'Marque se este é o psicólogo principal do paciente',
            'especialidade_foco': 'Especialidade ou foco específico deste atendimento',
            'motivo_inicio': 'Descreva o motivo do início deste atendimento',
        }


class GerenciarPsicologosForm(forms.Form):
    """Formulário para gerenciar múltiplos psicólogos de um paciente"""
    
    def __init__(self, paciente=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paciente = paciente
        
        if paciente:
            # Campo para adicionar novo psicólogo
            psicologos_disponiveis = Psicologo.objects.filter(ativo=True).exclude(
                id__in=paciente.get_psicologos_ativos().values_list('id', flat=True)
            )
            
            self.fields['novo_psicologo'] = forms.ModelChoiceField(
                queryset=psicologos_disponiveis,
                required=False,
                empty_label="Selecione um psicólogo para adicionar...",
                widget=forms.Select(attrs={'class': 'form-select'}),
                label='Adicionar Psicólogo'
            )
            
            self.fields['principal_novo'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                label='Definir como principal'
            )
            
            self.fields['especialidade_novo'] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especialidade/Foco'}),
                label='Especialidade/Foco'
            )
            
            self.fields['motivo_novo'] = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motivo do atendimento...'}),
                label='Motivo do Atendimento'
            )
    
    def save(self, commit=True):
        """Adiciona o novo psicólogo ao paciente"""
        if not self.paciente:
            return False, "Paciente não informado"
        
        novo_psicologo = self.cleaned_data.get('novo_psicologo')
        if not novo_psicologo:
            return False, "Nenhum psicólogo selecionado"
        
        return self.paciente.adicionar_psicologo(
            psicologo=novo_psicologo,
            principal=self.cleaned_data.get('principal_novo', False),
            especialidade_foco=self.cleaned_data.get('especialidade_novo', ''),
            motivo_inicio=self.cleaned_data.get('motivo_novo', '')
        )
