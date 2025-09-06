from django.core.management.base import BaseCommand
from assejus.models import Advogado
from datetime import date


class Command(BaseCommand):
    help = 'Cria advogados de teste para o sistema ASEJUS'

    def handle(self, *args, **options):
        # Dados dos advogados de teste
        advogados_teste = [
            {
                'nome': 'Dr. João Silva Santos',
                'cpf': '123.456.789-01',
                'oab': '123456',
                'uf_oab': 'SP',
                'email': 'joao.silva@advocacia.com',
                'telefone': '(11) 9999-8888',
                'celular': '(11) 98888-7777',
                'endereco': 'Rua das Flores, 123 - Centro',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567',
                'especialidades': 'Civil, Trabalhista, Previdenciário',
                'data_inscricao_oab': date(2015, 3, 15),
                'experiencia_anos': 8,
                'ativo': True,
                'observacoes': 'Advogado especializado em direito civil e trabalhista'
            },
            {
                'nome': 'Dra. Maria Oliveira Costa',
                'cpf': '987.654.321-09',
                'oab': '654321',
                'uf_oab': 'RJ',
                'email': 'maria.oliveira@advocacia.com',
                'telefone': '(21) 8888-7777',
                'celular': '(21) 97777-6666',
                'endereco': 'Av. Copacabana, 456 - Copacabana',
                'cidade': 'Rio de Janeiro',
                'estado': 'RJ',
                'cep': '22070-001',
                'especialidades': 'Penal, Administrativo, Tributário',
                'data_inscricao_oab': date(2012, 7, 20),
                'experiencia_anos': 11,
                'ativo': True,
                'observacoes': 'Especialista em direito penal e administrativo'
            },
            {
                'nome': 'Dr. Carlos Ferreira Lima',
                'cpf': '456.789.123-45',
                'oab': '789123',
                'uf_oab': 'MG',
                'email': 'carlos.ferreira@advocacia.com',
                'telefone': '(31) 7777-6666',
                'celular': '(31) 96666-5555',
                'endereco': 'Rua da Liberdade, 789 - Savassi',
                'cidade': 'Belo Horizonte',
                'estado': 'MG',
                'cep': '30112-000',
                'especialidades': 'Ambiental, Consumidor, Família',
                'data_inscricao_oab': date(2018, 11, 10),
                'experiencia_anos': 5,
                'ativo': True,
                'observacoes': 'Advogado com foco em direito ambiental e do consumidor'
            }
        ]

        # Criar advogados
        for dados in advogados_teste:
            advogado, created = Advogado.objects.get_or_create(
                cpf=dados['cpf'],
                defaults=dados
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Advogado "{advogado.nome}" criado com sucesso!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Advogado "{advogado.nome}" já existe no sistema.'
                    )
                )

        # Mostrar estatísticas
        total_advogados = Advogado.objects.count()
        advogados_ativos = Advogado.objects.filter(ativo=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal de advogados no sistema: {total_advogados}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Advogados ativos: {advogados_ativos}'
            )
        )
