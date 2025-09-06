from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from .models import (
    Quarto, Hospede, Reserva, Hospedagem, 
    ServicoAdicional, ServicoUtilizado
)
from datetime import timedelta


class QuartoForm(ModelForm):
    """Formulário para cadastro e edição de quartos"""
    
    class Meta:
        model = Quarto
        fields = [
            'numero', 'tipo', 'capacidade', 'valor_diaria', 'status',
            'ar_condicionado', 'tv', 'wifi', 'banheiro_privativo', 'frigobar',
            'observacoes', 'ativo'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'capacidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_diaria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if self.instance.pk:  # Se for edição
            if Quarto.objects.filter(numero=numero).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Já existe um quarto com este número.')
        else:  # Se for criação
            if Quarto.objects.filter(numero=numero).exists():
                raise ValidationError('Já existe um quarto com este número.')
        return numero


class HospedeForm(ModelForm):
    """Formulário para cadastro e edição de hóspedes"""
    
    class Meta:
        model = Hospede
        fields = [
            'tipo_hospede', 'associado', 'nome_completo', 'data_nascimento', 'foto',
            'tipo_documento', 'numero_documento', 'orgao_emissor', 'uf_emissor',
            'telefone', 'telefone_secundario', 'email',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'profissao', 'empresa', 'observacoes', 'ativo'
        ]
        widgets = {
            'tipo_hospede': forms.Select(attrs={'class': 'form-control'}),
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'orgao_emissor': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_emissor': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_secundario': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'profissao': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campo associado obrigatório apenas se for associado
        if self.instance.pk and self.instance.tipo_hospede == 'associado':
            self.fields['associado'].required = True
        else:
            self.fields['associado'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_hospede = cleaned_data.get('tipo_hospede')
        associado = cleaned_data.get('associado')
        
        if tipo_hospede == 'associado' and not associado:
            raise ValidationError('Para hóspedes associados, é obrigatório selecionar um associado.')
        
        return cleaned_data


class ReservaForm(ModelForm):
    """Formulário para cadastro e edição de reservas"""
    
    class Meta:
        model = Reserva
        fields = [
            'quarto', 'hospede', 'data_entrada', 'data_saida',
            'hora_entrada', 'hora_saida', 'valor_diaria', 'observacoes'
        ]
        widgets = {
            'quarto': forms.Select(attrs={'class': 'form-control'}),
            'hospede': forms.Select(attrs={'class': 'form-control'}),
            'data_entrada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_saida': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_saida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'valor_diaria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas quartos disponíveis
        self.fields['quarto'].queryset = Quarto.objects.filter(
            Q(status='disponivel') | Q(status='reservado')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        data_entrada = cleaned_data.get('data_entrada')
        data_saida = cleaned_data.get('data_saida')
        quarto = cleaned_data.get('quarto')
        
        if data_entrada and data_saida:
            if data_entrada >= data_saida:
                raise ValidationError('A data de saída deve ser posterior à data de entrada.')
            
            if data_entrada < timezone.now().date():
                raise ValidationError('A data de entrada não pode ser anterior à data atual.')
        
        # Verificar disponibilidade do quarto
        if quarto and data_entrada and data_saida:
            # Verificar se há conflitos de reserva
            conflitos = Reserva.objects.filter(
                quarto=quarto,
                status__in=['pendente', 'confirmada'],
                data_entrada__lt=data_saida,
                data_saida__gt=data_entrada
            )
            
            if self.instance.pk:
                conflitos = conflitos.exclude(pk=self.instance.pk)
            
            if conflitos.exists():
                raise ValidationError('Este quarto já possui reserva para o período selecionado.')
        
        return cleaned_data


class HospedagemForm(ModelForm):
    """Formulário para cadastro e edição de hospedagens"""
    
    class Meta:
        model = Hospedagem
        fields = [
            'reserva', 'quarto', 'hospede', 'data_entrada_real',
            'data_saida_real', 'valor_diaria_real', 'observacoes'
        ]
        widgets = {
            'reserva': forms.Select(attrs={'class': 'form-control'}),
            'quarto': forms.Select(attrs={'class': 'form-control'}),
            'hospede': forms.Select(attrs={'class': 'form-control'}),
            'data_entrada_real': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_saida_real': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valor_diaria_real': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas quartos disponíveis ou em manutenção
        self.fields['quarto'].queryset = Quarto.objects.filter(
            ativo=True,
            status__in=['disponivel', 'manutencao']
        ).order_by('numero')
        
        # Filtrar apenas hóspedes ativos
        self.fields['hospede'].queryset = Hospede.objects.filter(ativo=True).order_by('nome_completo')
        
        # Filtrar apenas reservas pendentes ou confirmadas
        self.fields['reserva'].queryset = Reserva.objects.filter(
            status__in=['pendente', 'confirmada']
        ).order_by('-data_reserva')
        
        # Tornar o campo reserva opcional
        self.fields['reserva'].required = False
        self.fields['reserva'].empty_label = "Selecione uma reserva (opcional)"
        
        # Tornar o campo data_saida_real opcional
        self.fields['data_saida_real'].required = False
        
        # Adicionar labels mais descritivos
        self.fields['quarto'].label = "Quarto"
        self.fields['hospede'].label = "Hóspede"
        self.fields['reserva'].label = "Reserva (opcional)"
        self.fields['data_entrada_real'].label = "Data e Hora de Entrada"
        self.fields['data_saida_real'].label = "Data e Hora de Saída (opcional)"
        self.fields['valor_diaria_real'].label = "Valor da Diária"
        self.fields['observacoes'].label = "Observações"
        
        # Adicionar help_text
        self.fields['quarto'].help_text = "Selecione um quarto disponível"
        self.fields['hospede'].help_text = "Selecione o hóspede para esta hospedagem"
        self.fields['reserva'].help_text = "Selecione uma reserva existente ou deixe em branco para hospedagem direta"
        self.fields['data_entrada_real'].help_text = "Data e hora do check-in"
        self.fields['data_saida_real'].help_text = "Data e hora do check-out (opcional - pode ser preenchida posteriormente)"
        self.fields['valor_diaria_real'].help_text = "Valor cobrado por diária"
        self.fields['observacoes'].help_text = "Observações adicionais sobre a hospedagem"
    
    def clean(self):
        cleaned_data = super().clean()
        data_entrada_real = cleaned_data.get('data_entrada_real')
        data_saida_real = cleaned_data.get('data_saida_real')
        quarto = cleaned_data.get('quarto')
        
        if data_entrada_real and data_saida_real:
            if data_entrada_real >= data_saida_real:
                raise ValidationError('A data/hora de saída deve ser posterior à data/hora de entrada.')
        
        # Verificar se o quarto está disponível para o período
        if quarto and data_entrada_real:
            # Verificar se há conflitos de hospedagem
            conflitos = Hospedagem.objects.filter(
                quarto=quarto,
                status='ativa'
            )
            
            # Se há data de saída, verificar conflitos no período
            if data_saida_real:
                conflitos = conflitos.filter(
                    data_entrada_real__lt=data_saida_real,
                    data_saida_real__gt=data_entrada_real
                )
            else:
                # Se não há data de saída, verificar se há hospedagens ativas que começaram antes
                conflitos = conflitos.filter(
                    data_entrada_real__lt=data_entrada_real + timedelta(days=1)
                )
            
            if self.instance.pk:
                conflitos = conflitos.exclude(pk=self.instance.pk)
            
            if conflitos.exists():
                raise ValidationError('Este quarto já possui hospedagem ativa para o período selecionado.')
        
        return cleaned_data


class ServicoAdicionalForm(ModelForm):
    """Formulário para cadastro e edição de serviços adicionais"""
    
    class Meta:
        model = ServicoAdicional
        fields = ['nome', 'tipo', 'descricao', 'valor', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ServicoUtilizadoForm(ModelForm):
    """Formulário para cadastro e edição de serviços utilizados"""
    
    class Meta:
        model = ServicoUtilizado
        fields = ['hospedagem', 'servico', 'quantidade', 'valor_unitario', 'observacoes']
        widgets = {
            'hospedagem': forms.Select(attrs={'class': 'form-control'}),
            'servico': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas hospedagens ativas
        self.fields['hospedagem'].queryset = Hospedagem.objects.filter(status='ativa')
        # Filtrar apenas serviços ativos
        self.fields['servico'].queryset = ServicoAdicional.objects.filter(ativo=True)


# Formset para serviços utilizados
ServicoUtilizadoFormSet = inlineformset_factory(
    Hospedagem, 
    ServicoUtilizado, 
    form=ServicoUtilizadoForm,
    extra=1,
    can_delete=True
)


class BuscaQuartoForm(forms.Form):
    """Formulário para busca de quartos disponíveis"""
    
    data_entrada = forms.DateField(
        label="Data de Entrada",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_saida = forms.DateField(
        label="Data de Saída",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tipo_quarto = forms.ChoiceField(
        label="Tipo de Quarto",
        choices=[('', 'Todos')] + Quarto.TIPO_QUARTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    capacidade_minima = forms.IntegerField(
        label="Capacidade Mínima",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        data_entrada = cleaned_data.get('data_entrada')
        data_saida = cleaned_data.get('data_saida')
        
        if data_entrada and data_saida:
            if data_entrada >= data_saida:
                raise ValidationError('A data de saída deve ser posterior à data de entrada.')
            
            if data_entrada < timezone.now().date():
                raise ValidationError('A data de entrada não pode ser anterior à data atual.')
        
        return cleaned_data


class RelatorioHospedagemForm(forms.Form):
    """Formulário para geração de relatórios de hospedagem"""
    
    PERIODO_CHOICES = [
        ('hoje', 'Hoje'),
        ('semana', 'Esta Semana'),
        ('mes', 'Este Mês'),
        ('trimestre', 'Este Trimestre'),
        ('ano', 'Este Ano'),
        ('personalizado', 'Período Personalizado'),
    ]
    
    periodo = forms.ChoiceField(
        label="Período",
        choices=PERIODO_CHOICES,
        initial='mes',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_inicio = forms.DateField(
        label="Data Início",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        label="Data Fim",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tipo_hospede = forms.ChoiceField(
        label="Tipo de Hóspede",
        choices=[('', 'Todos')] + Hospede.TIPO_HOSPEDE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label="Status",
        choices=[('', 'Todos')] + Hospedagem.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
