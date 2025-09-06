from django import forms
from .models import DependentePreCadastro


class DependentePreCadastroForm(forms.ModelForm):
    """
    Formulário para cadastro de dependentes do pré-cadastro
    """
    class Meta:
        model = DependentePreCadastro
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
            # Remover formatação
            cpf = cpf.replace('.', '').replace('-', '')
            
            # Verificar se tem 11 dígitos
            if len(cpf) != 11 or not cpf.isdigit():
                raise forms.ValidationError('CPF deve ter 11 dígitos.')
            
            # Validar CPF
            if not self.validar_cpf(cpf):
                raise forms.ValidationError('CPF inválido.')
            
            # Reformatar
            cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        return cpf

    def validar_cpf(self, cpf):
        """Valida CPF usando algoritmo padrão"""
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcular segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificar se os dígitos calculados coincidem com os fornecidos
        return int(cpf[9]) == digito1 and int(cpf[10]) == digito2
