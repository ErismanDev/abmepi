from django.core.management.base import BaseCommand
from diretoria.models import TemplateAta


class Command(BaseCommand):
    help = 'Criar templates padrão de atas'

    def handle(self, *args, **options):
        templates = [
            {
                'nome': 'Modelo Básico',
                'descricao': 'Template básico para atas de reunião',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO</h2>
                    <p><strong>Tipo:</strong> [TIPO_REUNIAO]</p>
                    <p><strong>Data:</strong> [DATA] às [HORA]</p>
                    <p><strong>Local:</strong> [LOCAL]</p>
                    <p><strong>Presidente:</strong> [PRESIDENTE]</p>
                    <p><strong>Secretário:</strong> [SECRETARIO]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[PRESENTES]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[AUSENTES]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>Leitura e aprovação da ata anterior</li>
                        <li>Assuntos gerais</li>
                        <li>Outros assuntos</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>Nesta reunião foram tratados os seguintes assuntos:</p>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                        <li>Item 3</li>
                    </ul>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>Nenhuma observação a registrar.</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes em [DATA].</em></p>
                '''
            },
            {
                'nome': 'Reunião Ordinária',
                'descricao': 'Template para reuniões ordinárias da diretoria',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO ORDINÁRIA</h2>
                    <p><strong>Data:</strong> [DATA] às [HORA]</p>
                    <p><strong>Local:</strong> [LOCAL]</p>
                    <p><strong>Presidente:</strong> [PRESIDENTE]</p>
                    <p><strong>Secretário:</strong> [SECRETARIO]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[PRESENTES]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[AUSENTES]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>Leitura e aprovação da ata anterior</li>
                        <li>Prestação de contas</li>
                        <li>Relatórios de atividades</li>
                        <li>Assuntos administrativos</li>
                        <li>Assuntos gerais</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>Foram deliberados os seguintes assuntos:</p>
                    <ul>
                        <li><strong>Item 1:</strong> Descrição da deliberação</li>
                        <li><strong>Item 2:</strong> Descrição da deliberação</li>
                        <li><strong>Item 3:</strong> Descrição da deliberação</li>
                    </ul>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>Nenhuma observação a registrar.</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes em [DATA].</em></p>
                '''
            },
            {
                'nome': 'Reunião Extraordinária',
                'descricao': 'Template para reuniões extraordinárias',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO EXTRAORDINÁRIA</h2>
                    <p><strong>Data:</strong> [DATA] às [HORA]</p>
                    <p><strong>Local:</strong> [LOCAL]</p>
                    <p><strong>Presidente:</strong> [PRESIDENTE]</p>
                    <p><strong>Secretário:</strong> [SECRETARIO]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[PRESENTES]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[AUSENTES]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>Leitura e aprovação da ata anterior</li>
                        <li>Assunto extraordinário 1</li>
                        <li>Assunto extraordinário 2</li>
                        <li>Outros assuntos</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>Foram deliberados os seguintes assuntos extraordinários:</p>
                    <ul>
                        <li><strong>Assunto 1:</strong> Descrição da deliberação</li>
                        <li><strong>Assunto 2:</strong> Descrição da deliberação</li>
                    </ul>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>Reunião convocada extraordinariamente para tratar de assuntos urgentes.</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes em [DATA].</em></p>
                '''
            },
            {
                'nome': 'Reunião de Emergência',
                'descricao': 'Template para reuniões de emergência',
                'conteudo': '''
                    <h2>ATA DE REUNIÃO DE EMERGÊNCIA</h2>
                    <p><strong>Data:</strong> [DATA] às [HORA]</p>
                    <p><strong>Local:</strong> [LOCAL]</p>
                    <p><strong>Presidente:</strong> [PRESIDENTE]</p>
                    <p><strong>Secretário:</strong> [SECRETARIO]</p>
                    
                    <h3>PRESENTES:</h3>
                    <ul>
                        <li>[PRESENTES]</li>
                    </ul>
                    
                    <h3>AUSENTES:</h3>
                    <ul>
                        <li>[AUSENTES]</li>
                    </ul>
                    
                    <h3>PAUTA:</h3>
                    <ol>
                        <li>Leitura e aprovação da ata anterior</li>
                        <li>Assunto de emergência</li>
                        <li>Medidas a serem tomadas</li>
                    </ol>
                    
                    <h3>DELIBERAÇÕES:</h3>
                    <p>Em virtude da situação de emergência, foram deliberadas as seguintes medidas:</p>
                    <ul>
                        <li><strong>Medida 1:</strong> Descrição da medida</li>
                        <li><strong>Medida 2:</strong> Descrição da medida</li>
                    </ul>
                    
                    <h3>OBSERVAÇÕES:</h3>
                    <p>Reunião de emergência convocada para tratar de situação excepcional.</p>
                    
                    <p><em>Esta ata foi aprovada pelos presentes em [DATA].</em></p>
                '''
            }
        ]

        for template_data in templates:
            template, created = TemplateAta.objects.get_or_create(
                nome=template_data['nome'],
                defaults={
                    'descricao': template_data['descricao'],
                    'conteudo': template_data['conteudo'],
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Template "{template.nome}" criado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template "{template.nome}" já existe.')
                )

        self.stdout.write(
            self.style.SUCCESS('Templates de ata criados com sucesso!')
        )
