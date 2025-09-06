from django import forms
from .models_ata_simples import AtaSimples
from django.utils import timezone

class AtaSimplesForm(forms.ModelForm):
    """
    Formulário simplificado para criação de atas
    """
    
    class Meta:
        model = AtaSimples
        fields = [
            'titulo', 'tipo_reuniao', 'data_reuniao', 'local',
            'presidente', 'secretario', 'membros_presentes', 'membros_ausentes',
            'pauta', 'deliberacoes', 'observacoes'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ata da Reunião Ordinária de Janeiro/2025'
            }),
            'tipo_reuniao': forms.Select(attrs={'class': 'form-select'}),
            'data_reuniao': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sede da ABMEPI'
            }),
            'presidente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do presidente'
            }),
            'secretario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do secretário'
            }),
            'membros_presentes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Liste os membros presentes, um por linha:\nJoão Silva\nMaria Santos\nPedro Oliveira'
            }),
            'membros_ausentes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Liste os membros ausentes, um por linha:\nAna Costa\nCarlos Lima'
            }),
            'pauta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Liste os itens da pauta, um por linha:\n1. Aprovação da ata anterior\n2. Relatório financeiro\n3. Propostas para o próximo mês'
            }),
            'deliberacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva as decisões tomadas na reunião...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações adicionais...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir data padrão como agora
        if not self.instance.pk:
            self.fields['data_reuniao'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo', '').strip()
        if not titulo:
            raise forms.ValidationError('Título é obrigatório.')
        return titulo
    
    def clean_membros_presentes(self):
        membros = self.cleaned_data.get('membros_presentes', '').strip()
        if not membros:
            raise forms.ValidationError('Pelo menos um membro presente deve ser informado.')
        return membros

class AtaEditorForm(forms.ModelForm):
    """
    Formulário para edição do conteúdo em texto da ata
    """
    
    class Meta:
        model = AtaSimples
        fields = ['pauta', 'deliberacoes', 'observacoes']
        widgets = {
            'pauta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Lista dos assuntos a serem tratados na reunião'
            }),
            'deliberacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Decisões tomadas na reunião'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Observações adicionais'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se não há conteúdo HTML, gerar automaticamente
        if self.instance and not self.instance.conteudo_html:
            self.instance.conteudo_html = self.instance.gerar_html()
            self.instance.save()


class AtaEditorAvancadoForm(forms.ModelForm):
    """
    Formulário para edição avançada do conteúdo HTML da ata (estilo SEI)
    """
    
    class Meta:
        model = AtaSimples
        fields = ['conteudo_html']
        widgets = {
            'conteudo_html': forms.Textarea(attrs={
                'id': 'editor-html',
                'style': 'display: none;'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se não há conteúdo HTML, gerar automaticamente
        if self.instance and not self.instance.conteudo_html:
            self.instance.conteudo_html = self.instance.gerar_html()
            self.instance.save()
