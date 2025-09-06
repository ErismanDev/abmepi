from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from .models import TipoMensalidade, Mensalidade, Pagamento, Despesa, ConfiguracaoCobranca


class TipoMensalidadeForm(forms.ModelForm):
    """
    Formulário para tipos de mensalidade
    """
    class Meta:
        model = TipoMensalidade
        fields = ['nome', 'descricao', 'valor', 'recorrente', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do tipo de mensalidade'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'inputmode': 'decimal'
            }),
            'recorrente': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_valor(self):
        """
        Limpa e valida o campo valor
        """
        valor = self.cleaned_data.get('valor')
        
        if valor:
            # Se for string, converter do formato brasileiro
            if isinstance(valor, str):
                # Remover espaços e converter vírgula para ponto
                valor_limpo = valor.strip().replace('.', '').replace(',', '.')
                
                try:
                    valor = float(valor_limpo)
                except ValueError:
                    raise forms.ValidationError('Valor inválido. Use o formato: 1.000,00')
            
            # Garantir que o valor seja positivo
            if valor <= 0:
                raise forms.ValidationError('O valor deve ser maior que zero.')
            
            # Arredondar para 2 casas decimais
            valor = round(valor, 2)
        else:
            raise forms.ValidationError('Este campo é obrigatório.')
        
        return valor
    
    def save(self, commit=True):
        """
        Sobrescreve o método save para definir a categoria automaticamente
        """
        instance = super().save(commit=False)
        # Definir categoria como 'mensalidade' automaticamente
        instance.categoria = 'mensalidade'
        
        if commit:
            instance.save()
        return instance


class MensalidadeForm(forms.ModelForm):
    """
    Formulário para recebíveis
    """
    FORMA_PAGAMENTO_CHOICES = [
        ('', 'Selecione uma forma de pagamento'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('transferencia', 'Transferência Bancária'),
        ('boleto', 'Boleto Bancário'),
        ('cheque', 'Cheque'),
        ('outros', 'Outros'),
    ]

    forma_pagamento = forms.ChoiceField(
        choices=FORMA_PAGAMENTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Forma de pagamento'
        })
    )

    class Meta:
        model = Mensalidade
        fields = ['associado', 'tipo', 'valor', 'data_vencimento', 'status', 'forma_pagamento', 'observacoes']
        widgets = {
            'associado': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'inputmode': 'decimal'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'format': '%Y-%m-%d'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a mensalidade'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas tipos de mensalidade ativos
        self.fields['tipo'].queryset = TipoMensalidade.objects.filter(ativo=True).order_by('categoria', 'nome')
        # Filtrar apenas associados ativos
        self.fields['associado'].queryset = self.fields['associado'].queryset.filter(ativo=True).order_by('nome')
        
        # Adicionar classes CSS para melhorar a aparência
        self.fields['associado'].widget.attrs.update({
            'class': 'form-select select2',
            'data-placeholder': 'Selecione um associado'
        })
        
        self.fields['tipo'].widget.attrs.update({
            'class': 'form-select select2',
            'data-placeholder': 'Selecione um tipo de recebimento'
        })
        
        # Definir data atual como padrão para data de vencimento (apenas para criação)
        if not self.instance.pk:  # Se não é uma edição (nova mensalidade)
            from datetime import date
            self.fields['data_vencimento'].initial = date.today()
        
        # Para edição, garantir que os campos sejam preenchidos corretamente
        if self.instance.pk and self.instance.tipo:
            # Preencher o valor baseado no tipo selecionado
            self.fields['valor'].initial = self.instance.tipo.valor
            
        # Para edição, garantir que a data de vencimento seja formatada corretamente
        if self.instance.pk and self.instance.data_vencimento:
            # Garantir que a data seja formatada como YYYY-MM-DD para input type="date"
            if hasattr(self.instance.data_vencimento, 'strftime'):
                data_formatada = self.instance.data_vencimento.strftime('%Y-%m-%d')
                self.fields['data_vencimento'].initial = data_formatada
            elif isinstance(self.instance.data_vencimento, str):
                # Se for string, tentar converter para o formato correto
                try:
                    from datetime import datetime
                    data_obj = datetime.strptime(self.instance.data_vencimento, '%Y-%m-%d').date()
                    data_formatada = data_obj.strftime('%Y-%m-%d')
                    self.fields['data_vencimento'].initial = data_formatada
                except ValueError:
                    # Tentar outros formatos de data comuns
                    for formato in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                        try:
                            data_obj = datetime.strptime(self.instance.data_vencimento, formato).date()
                            data_formatada = data_obj.strftime('%Y-%m-%d')
                            self.fields['data_vencimento'].initial = data_formatada
                            break
                        except ValueError:
                            continue
                    else:
                        self.fields['data_vencimento'].initial = self.instance.data_vencimento
            else:
                self.fields['data_vencimento'].initial = self.instance.data_vencimento
            
            # Forçar a atualização do widget com o valor inicial
            if hasattr(self.fields['data_vencimento'].widget, 'attrs'):
                self.fields['data_vencimento'].widget.attrs['value'] = self.fields['data_vencimento'].initial


class PagamentoForm(forms.ModelForm):
    """
    Formulário para pagamentos
    """
    class Meta:
        model = Pagamento
        fields = ['mensalidade', 'valor_pago', 'data_pagamento', 'forma_pagamento', 'comprovante', 'observacoes']
        widgets = {
            'mensalidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor_pago': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'data_pagamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'format': '%Y-%m-%d'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comprovante': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o pagamento'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas mensalidades pendentes
        self.fields['mensalidade'].queryset = self.fields['mensalidade'].queryset.filter(status='pendente')

    def clean_valor_pago(self):
        valor_pago = self.cleaned_data.get('valor_pago')
        mensalidade = self.cleaned_data.get('mensalidade')
        
        if mensalidade and valor_pago:
            valor_esperado = mensalidade.get_valor_com_multa()
            if valor_pago < valor_esperado:
                raise forms.ValidationError(
                    f'O valor pago deve ser pelo menos R$ {valor_esperado:.2f} (incluindo multas e juros)'
                )
        
        return valor_pago


class DespesaForm(forms.ModelForm):
    """
    Formulário para despesas
    """
    class Meta:
        model = Despesa
        fields = ['descricao', 'categoria', 'valor', 'data_despesa', 'data_vencimento', 'pago', 'fornecedor', 'nota_fiscal', 'comprovante', 'observacoes']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da despesa'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'data_despesa': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'format': '%Y-%m-%d'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'format': '%Y-%m-%d'
            }),
            'pago': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor'
            }),
            'nota_fiscal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da nota fiscal'
            }),
            'comprovante': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a despesa'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantir que as datas sejam formatadas corretamente para o HTML5 date input
        if self.instance and self.instance.pk:
            if self.instance.data_despesa:
                self.initial['data_despesa'] = self.instance.data_despesa.strftime('%Y-%m-%d')
            if self.instance.data_vencimento:
                self.initial['data_vencimento'] = self.instance.data_vencimento.strftime('%Y-%m-%d')


class MensalidadeSearchForm(forms.Form):
    """
    Formulário de busca para mensalidades de associados
    """
    associado = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou CPF do associado'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os Status')] + Mensalidade.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tipo = forms.ModelChoiceField(
        queryset=TipoMensalidade.objects.filter(ativo=True, categoria='mensalidade'),
        required=False,
        empty_label="Todos os Tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'format': '%Y-%m-%d'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'format': '%Y-%m-%d'
        })
    )


class DespesaSearchForm(forms.Form):
    """
    Formulário de busca para despesas
    """
    descricao = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descrição da despesa'
        })
    )
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas as Categorias')] + Despesa.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    fornecedor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do fornecedor'
        })
    )
    
    pago = forms.ChoiceField(
        choices=[('', 'Todos'), ('True', 'Pago'), ('False', 'Não Pago')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'format': '%Y-%m-%d'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'format': '%Y-%m-%d'
        })
    )


class ConfiguracaoCobrancaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoCobranca
        fields = [
            'nome', 'ativo', 'chave_pix', 'titular', 'banco',
            'mensagem', 'telefone_comprovante',
            'qr_code_ativo', 'qr_code_imagem', 'qr_code_tamanho'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chave_pix': forms.TextInput(attrs={'class': 'form-control'}),
            'titular': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite a mensagem personalizada para o carnê'}),
            'telefone_comprovante': forms.TextInput(attrs={'class': 'form-control'}),
            'qr_code_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'qr_code_imagem': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'qr_code_tamanho': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 30}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        ativo = cleaned_data.get('ativo')
        
        # Se esta configuração for ativada, desativar as outras
        if ativo:
            ConfiguracaoCobranca.objects.exclude(pk=self.instance.pk if self.instance else None).update(ativo=False)
        
        return cleaned_data
