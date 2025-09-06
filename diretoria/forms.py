from django import forms
from django.contrib.auth import get_user_model
from .models import CargoDiretoria, MembroDiretoria, AtaReuniao, ResolucaoDiretoria, ModeloAtaUnificado

User = get_user_model()


class CargoDiretoriaForm(forms.ModelForm):
    class Meta:
        model = CargoDiretoria
        fields = ['nome', 'descricao', 'ordem_hierarquica', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ordem_hierarquica': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MembroDiretoriaForm(forms.ModelForm):
    class Meta:
        model = MembroDiretoria
        fields = ['associado', 'cargo', 'data_inicio', 'data_fim', 'ativo']
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'cargo': forms.Select(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AtaReuniaoForm(forms.ModelForm):
    class Meta:
        model = AtaReuniao
        fields = ['numero_sequencial', 'titulo', 'data_reuniao', 'local', 'tipo_reuniao', 'presidente', 'secretario', 'membros_presentes', 'associados_presentes', 'pauta', 'deliberacoes', 'observacoes']
        widgets = {
            'numero_sequencial': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_reuniao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_reuniao': forms.Select(attrs={'class': 'form-control'}),
            'presidente': forms.Select(attrs={'class': 'form-control'}),
            'secretario': forms.Select(attrs={'class': 'form-control'}),
            'membros_presentes': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'associados_presentes': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'pauta': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'deliberacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ResolucaoDiretoriaForm(forms.ModelForm):
    class Meta:
        model = ResolucaoDiretoria
        fields = ['numero', 'titulo', 'ementa', 'texto_integral', 'data_resolucao', 'data_publicacao', 'data_vigencia', 'status', 'ata_reuniao', 'arquivo_resolucao', 'observacoes']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'ementa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'texto_integral': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'data_resolucao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_publicacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vigencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'ata_reuniao': forms.Select(attrs={'class': 'form-control'}),
            'arquivo_resolucao': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ModeloAtaUnificadoForm(forms.ModelForm):
    class Meta:
        model = ModeloAtaUnificado
        fields = ['nome', 'descricao', 'categoria', 'tipo_conteudo', 'conteudo', 'conteudo_html', 'titulo_original', 'tags', 'publico']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do modelo'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do modelo'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'tipo_conteudo': forms.Select(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'placeholder': 'Conteúdo principal do modelo'}),
            'conteudo_html': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'placeholder': 'Versão HTML do conteúdo (opcional)'}),
            'titulo_original': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da ata original (opcional)'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags separadas por vírgula'}),
            'publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS aos labels
        for field_name, field in self.fields.items():
            if field_name != 'publico':
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            # Limpar e validar tags
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tags_list) > 10:
                raise forms.ValidationError('Máximo de 10 tags permitidas.')
            return ', '.join(tags_list)
        return tags
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_conteudo = cleaned_data.get('tipo_conteudo')
        conteudo_html = cleaned_data.get('conteudo_html')
        
        # Se tipo é HTML, conteudo_html é obrigatório
        if tipo_conteudo == 'html' and not conteudo_html:
            self.add_error('conteudo_html', 'Conteúdo HTML é obrigatório quando o tipo é HTML.')
        
        return cleaned_data