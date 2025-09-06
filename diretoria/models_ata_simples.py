from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import os

User = get_user_model()

def upload_ata_path(instance, filename):
    """Gera o caminho para upload do arquivo da ata"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{instance.titulo_slug}.{ext}"
    return os.path.join('atas', filename)

class AtaSimples(models.Model):
    """
    Modelo simplificado para atas de reunião
    """
    TIPO_REUNIAO_CHOICES = [
        ('ordinaria', 'Reunião Ordinária'),
        ('extraordinaria', 'Reunião Extraordinária'),
        ('emergencia', 'Reunião de Emergência'),
        ('especial', 'Reunião Especial'),
    ]
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('finalizada', 'Finalizada'),
        ('assinada', 'Assinada'),
    ]
    
    # Identificação única
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_sequencial = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Número Sequencial',
        help_text='Número sequencial da ata por tipo de reunião'
    )
    titulo = models.CharField('Título da Ata', max_length=200)
    titulo_slug = models.SlugField('Slug do Título', max_length=200, blank=True)
    
    # Informações básicas
    tipo_reuniao = models.CharField('Tipo de Reunião', max_length=20, choices=TIPO_REUNIAO_CHOICES, default='ordinaria')
    data_reuniao = models.DateTimeField('Data e Hora da Reunião', default=timezone.now)
    local = models.CharField('Local da Reunião', max_length=200, default='Sede da ABMEPI')
    
    # Participantes
    presidente = models.CharField('Presidente', max_length=200, blank=True)
    secretario = models.CharField('Secretário', max_length=200, blank=True)
    membros_presentes = models.TextField('Membros Presentes', blank=True, help_text='Lista os membros presentes, um por linha')
    membros_ausentes = models.TextField('Membros Ausentes', blank=True, help_text='Lista os membros ausentes, um por linha')
    
    # Conteúdo
    pauta = models.TextField('Pauta', blank=True, help_text='Itens da pauta da reunião')
    deliberacoes = models.TextField('Deliberações', blank=True, help_text='Decisões tomadas na reunião')
    observacoes = models.TextField('Observações', blank=True, help_text='Observações adicionais')
    
    # Conteúdo HTML gerado
    conteudo_html = models.TextField('Conteúdo HTML', blank=True, help_text='Conteúdo HTML da ata')
    arquivo_html = models.FileField('Arquivo HTML', upload_to=upload_ata_path, blank=True, null=True)
    
    # Metadados
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='rascunho')
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='atas_criadas')
    
    class Meta:
        verbose_name = 'Ata Simples'
        verbose_name_plural = 'Atas Simples'
        ordering = ['-data_reuniao']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_reuniao.strftime('%d/%m/%Y')}"
    
    def gerar_numero_sequencial(self):
        """
        Gera o próximo número sequencial para o tipo de reunião
        """
        if self.numero_sequencial:
            return self.numero_sequencial
            
        # Busca o último número para este tipo de reunião no mesmo ano
        ano_atual = self.data_reuniao.year
        ultima_ata = AtaSimples.objects.filter(
            tipo_reuniao=self.tipo_reuniao,
            data_reuniao__year=ano_atual,
            numero_sequencial__isnull=False
        ).order_by('-numero_sequencial').first()
        
        if ultima_ata and ultima_ata.numero_sequencial:
            return ultima_ata.numero_sequencial + 1
        else:
            return 1
    
    def get_numero_formatado(self):
        """
        Retorna o número formatado da ata (ex: ORD-001/2024)
        """
        if not self.numero_sequencial:
            return "N/A"
        
        ano = self.data_reuniao.year
        prefixo = {
            'ordinaria': 'ORD',
            'extraordinaria': 'EXT',
            'emergencia': 'EMG',
            'especial': 'ESP'
        }.get(self.tipo_reuniao, 'ATA')
        
        return f"{prefixo}-{self.numero_sequencial:03d}/{ano}"
    
    def save(self, *args, **kwargs):
        if not self.titulo_slug:
            self.titulo_slug = self.titulo.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c')
        
        # Gera o número sequencial se não existir
        if not self.numero_sequencial:
            self.numero_sequencial = self.gerar_numero_sequencial()
            
        super().save(*args, **kwargs)
    
    def gerar_html(self):
        """Gera o conteúdo HTML da ata"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.titulo}</title>
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #333;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    font-size: 24px;
                    margin: 0;
                    text-transform: uppercase;
                }}
                .info {{
                    margin-bottom: 20px;
                }}
                .info p {{
                    margin: 5px 0;
                }}
                .section {{
                    margin-bottom: 25px;
                }}
                .section h3 {{
                    font-size: 16px;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }}
                .participants {{
                    display: flex;
                    gap: 20px;
                }}
                .participants > div {{
                    flex: 1;
                }}
                .participants ul {{
                    list-style: none;
                    padding: 0;
                }}
                .participants li {{
                    padding: 2px 0;
                    border-bottom: 1px dotted #ccc;
                }}
                .pauta ol {{
                    padding-left: 20px;
                }}
                .pauta li {{
                    margin-bottom: 5px;
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-style: italic;
                }}
                @media print {{
                    body {{
                        margin: 0;
                        padding: 15px;
                    }}
                    .no-print {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.titulo}</h1>
            </div>
            
            <div class="info">
                <p><strong>Tipo:</strong> {self.get_tipo_reuniao_display()}</p>
                <p><strong>Data:</strong> {self.data_reuniao.strftime('%d/%m/%Y às %H:%M')}</p>
                <p><strong>Local:</strong> {self.local}</p>
                <p><strong>Presidente:</strong> {self.presidente or 'Não informado'}</p>
                <p><strong>Secretário:</strong> {self.secretario or 'Não informado'}</p>
            </div>
            
            <div class="participants">
                <div class="section">
                    <h3>Presentes</h3>
                    <ul>
                        {self._formatar_lista(self.membros_presentes)}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>Ausentes</h3>
                    <ul>
                        {self._formatar_lista(self.membros_ausentes)}
                    </ul>
                </div>
            </div>
            
            {self._formatar_secao('Pauta', self.pauta, 'ol')}
            {self._formatar_secao('Deliberações', self.deliberacoes)}
            {self._formatar_secao('Observações', self.observacoes)}
            
            <div class="footer">
                <p>Esta ata foi aprovada pelos presentes em {self.data_reuniao.strftime('%d/%m/%Y')}.</p>
                <p>Status: {self.get_status_display()}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _formatar_lista(self, texto):
        """Formata uma lista de texto em HTML"""
        if not texto:
            return '<li>Nenhum membro informado</li>'
        
        itens = [item.strip() for item in texto.split('\n') if item.strip()]
        if not itens:
            return '<li>Nenhum membro informado</li>'
        
        return ''.join([f'<li>{item}</li>' for item in itens])
    
    def _formatar_secao(self, titulo, conteudo, tipo_lista='ul'):
        """Formata uma seção da ata"""
        if not conteudo:
            return ''
        
        if tipo_lista == 'ol':
            itens = [item.strip() for item in conteudo.split('\n') if item.strip()]
            if itens:
                lista_html = ''.join([f'<li>{item}</li>' for item in itens])
                return f'''
                <div class="section">
                    <h3>{titulo}</h3>
                    <ol>{lista_html}</ol>
                </div>
                '''
        
        return f'''
        <div class="section">
            <h3>{titulo}</h3>
            <p>{conteudo.replace(chr(10), '<br>')}</p>
        </div>
        '''
