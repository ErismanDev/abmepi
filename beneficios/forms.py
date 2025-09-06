from django import forms
from .models import EmpresaParceira, Convenio, Beneficio, CategoriaBeneficio
from django.db import models


class EmpresaParceiraForm(forms.ModelForm):
    class Meta:
        model = EmpresaParceira
        fields = [
            'nome', 'cnpj', 'razao_social', 'endereco', 'cidade', 'estado', 'cep',
            'telefone', 'email', 'website', 'contato_principal', 'telefone_contato',
            'email_contato', 'observacoes', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '---------'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemplo.com'}),
            'contato_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email_contato': forms.EmailInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConvenioForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = [
            'empresa', 'titulo', 'descricao', 'categoria', 'status', 'data_inicio',
            'data_fim', 'desconto', 'condicoes', 'documentos_necessarios',
            'usuario_responsavel', 'arquivos_anexados', 'observacoes', 'ativo'
        ]
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'desconto': forms.TextInput(attrs={'class': 'form-control'}),
            'condicoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documentos_necessarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'usuario_responsavel': forms.Select(attrs={'class': 'form-control'}),
            'arquivos_anexados': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BeneficioForm(forms.ModelForm):
    class Meta:
        model = Beneficio
        fields = [
            'associado', 'convenio', 'status', 'valor_beneficio', 'desconto_aplicado',
            'data_aprovacao', 'data_utilizacao', 'usuario_aprovacao', 'observacoes', 'comprovante'
        ]
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'convenio': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'valor_beneficio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto_aplicado': forms.TextInput(attrs={'class': 'form-control'}),
            'data_aprovacao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_utilizacao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'usuario_aprovacao': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CategoriaBeneficioForm(forms.ModelForm):
    class Meta:
        model = CategoriaBeneficio
        fields = ['nome', 'descricao', 'icone', 'cor', 'ativo', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-heart'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class BeneficioSolicitacaoForm(forms.ModelForm):
    """Formulário para solicitação de benefício pelo associado"""
    class Meta:
        model = Beneficio
        fields = ['convenio', 'observacoes']
        widgets = {
            'convenio': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva sua solicitação...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas convênios ativos e válidos
        from datetime import date
        self.fields['convenio'].queryset = self.fields['convenio'].queryset.filter(
            ativo=True,
            status='ativo'
        ).filter(
            models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=date.today())
        )


class ConvenioBuscaForm(forms.Form):
    """Formulário para busca de convênios"""
    categoria = forms.ChoiceField(
        choices=[('', 'Todas as Categorias')] + Convenio.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    cidade = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a cidade...'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos os Estados')] + [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
            ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    termo_busca = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por título, empresa ou descrição...'})
    )
