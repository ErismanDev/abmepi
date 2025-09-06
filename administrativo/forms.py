from django import forms
from .models import Evento, Comunicado, ParticipanteEvento, ListaPresenca, Presenca
from django.utils import timezone


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'titulo', 'descricao', 'tipo', 'status', 'data_inicio', 'data_fim',
            'local', 'endereco', 'capacidade_maxima', 'valor_inscricao',
            'responsavel', 'imagem', 'arquivos_anexados', 'observacoes', 'ativo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacidade_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_inscricao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'arquivos_anexados': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona choices para os campos
        self.fields['tipo'].choices = [
            ('', '---------'),
            ('reuniao', 'Reunião'),
            ('palestra', 'Palestra'),
            ('workshop', 'Workshop'),
            ('congresso', 'Congresso'),
            ('seminario', 'Seminário'),
            ('treinamento', 'Treinamento'),
            ('outro', 'Outro'),
        ]
        self.fields['status'].choices = [
            ('', '---------'),
            ('agendado', 'Agendado'),
            ('em_andamento', 'Em Andamento'),
            ('concluido', 'Concluído'),
            ('cancelado', 'Cancelado'),
            ('adiado', 'Adiado'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim:
            if data_inicio >= data_fim:
                raise forms.ValidationError('A data de início deve ser anterior à data de fim')
        
        return cleaned_data


class ComunicadoForm(forms.ModelForm):
    class Meta:
        model = Comunicado
        fields = [
            'titulo', 'conteudo', 'tipo', 'prioridade', 'data_expiracao',
            'tipo_destinatarios', 'associados_especificos', 'advogados_especificos', 'psicologos_especificos',
            'destinatarios', 'enviar_email', 'enviar_sms', 'enviar_notificacao', 'arquivos_anexados', 'ativo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'data_expiracao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tipo_destinatarios': forms.Select(attrs={'class': 'form-control'}),
            'associados_especificos': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
            'advogados_especificos': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
            'psicologos_especificos': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
            'destinatarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite destinatários adicionais ou deixe em branco'}),
            'enviar_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enviar_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enviar_notificacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'arquivos_anexados': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configura querysets para os campos de seleção
        from associados.models import Associado
        from assejus.models import Advogado
        from psicologia.models import Psicologo
        
        # Filtra apenas associados ativos e ordena por nome
        self.fields['associados_especificos'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
        
        # Filtra apenas advogados ativos e ordena por nome
        self.fields['advogados_especificos'].queryset = Advogado.objects.all().order_by('nome')
        
        # Filtra apenas psicólogos ativos e ordena por nome
        self.fields['psicologos_especificos'].queryset = Psicologo.objects.filter(ativo=True).order_by('nome_completo')
        
        # As choices já estão definidas no modelo, não precisamos redefinir aqui
        pass
    
    def clean(self):
        cleaned_data = super().clean()
        data_expiracao = cleaned_data.get('data_expiracao')
        
        if data_expiracao and data_expiracao <= timezone.now():
            raise forms.ValidationError('A data de expiração deve ser futura')
        
        return cleaned_data


class ParticipanteEventoForm(forms.ModelForm):
    class Meta:
        model = ParticipanteEvento
        fields = ['associado', 'status', 'observacoes']
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas associados ativos e ordena por nome
        from associados.models import Associado
        self.fields['associado'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
        
        # Adiciona choices para o campo status
        self.fields['status'].choices = [
            ('', '---------'),
            ('pendente', 'Pendente'),
            ('confirmado', 'Confirmado'),
            ('presente', 'Presente'),
            ('ausente', 'Ausente'),
            ('cancelado', 'Cancelado'),
        ]


class ListaPresencaForm(forms.ModelForm):
    class Meta:
        model = ListaPresenca
        fields = ['evento', 'observacoes']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas eventos ativos
        self.fields['evento'].queryset = Evento.objects.filter(ativo=True).order_by('titulo')


class PresencaForm(forms.ModelForm):
    class Meta:
        model = Presenca
        fields = ['associado', 'presente', 'horario_chegada', 'horario_saida', 'observacoes']
        widgets = {
            'associado': forms.Select(attrs={'class': 'form-control'}),
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'horario_chegada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_saida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas associados ativos e ordena por nome
        from associados.models import Associado
        self.fields['associado'].queryset = Associado.objects.filter(ativo=True).order_by('nome')
    
    def clean(self):
        cleaned_data = super().clean()
        presente = cleaned_data.get('presente')
        horario_chegada = cleaned_data.get('horario_chegada')
        horario_saida = cleaned_data.get('horario_saida')
        
        if presente and not horario_chegada:
            raise forms.ValidationError('Para marcar presença, é necessário informar o horário de chegada')
        
        if horario_chegada and horario_saida and horario_chegada >= horario_saida:
            raise forms.ValidationError('O horário de chegada deve ser anterior ao horário de saída')
        
        return cleaned_data
