from django.core.management.base import BaseCommand
from financeiro.models import TipoMensalidade


class Command(BaseCommand):
    help = 'Cria tipos de recebimentos padrão para o sistema'

    def handle(self, *args, **options):
        tipos_padrao = [
            # MENSALIDADES DE ASSOCIADOS (Recorrentes)
            {
                'nome': 'Mensalidade Básica',
                'descricao': 'Mensalidade padrão para associados ativos',
                'valor': 50.00,
                'categoria': 'mensalidade',
                'recorrente': True,
                'ativo': True
            },
            {
                'nome': 'Mensalidade Premium',
                'descricao': 'Mensalidade para associados com benefícios especiais',
                'valor': 75.00,
                'categoria': 'mensalidade',
                'recorrente': True,
                'ativo': True
            },
            {
                'nome': 'Mensalidade Estudante',
                'descricao': 'Mensalidade com desconto para estudantes',
                'valor': 30.00,
                'categoria': 'mensalidade',
                'recorrente': True,
                'ativo': True
            },
            {
                'nome': 'Mensalidade Sênior',
                'descricao': 'Mensalidade com desconto para associados acima de 60 anos',
                'valor': 35.00,
                'categoria': 'mensalidade',
                'recorrente': True,
                'ativo': True
            },
            {
                'nome': 'Mensalidade Corporativa',
                'descricao': 'Mensalidade para empresas associadas',
                'valor': 150.00,
                'categoria': 'mensalidade',
                'recorrente': True,
                'ativo': True
            },
            
            # OUTROS RECEBIMENTOS (Não recorrentes)
            {
                'nome': 'Taxa de Adesão',
                'descricao': 'Taxa única para novos associados',
                'valor': 100.00,
                'categoria': 'outros',
                'recorrente': False,
                'ativo': True
            },
            {
                'nome': 'Taxa de Evento',
                'descricao': 'Taxa para participação em eventos especiais',
                'valor': 25.00,
                'categoria': 'outros',
                'recorrente': False,
                'ativo': True
            },
            {
                'nome': 'Taxa de Reemissão',
                'descricao': 'Taxa para reemissão de documentos',
                'valor': 15.00,
                'categoria': 'outros',
                'recorrente': False,
                'ativo': True
            },
            {
                'nome': 'Taxa de Certidão',
                'descricao': 'Taxa para emissão de certidões',
                'valor': 20.00,
                'categoria': 'outros',
                'recorrente': False,
                'ativo': True
            },
            {
                'nome': 'Taxa de Treinamento',
                'descricao': 'Taxa para cursos e treinamentos',
                'valor': 80.00,
                'categoria': 'outros',
                'recorrente': False,
                'ativo': True
            }
        ]

        criados = 0
        atualizados = 0

        for tipo_data in tipos_padrao:
            tipo, created = TipoMensalidade.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criado: {tipo.nome} - R$ {tipo.valor}')
                )
                criados += 1
            else:
                # Atualiza se já existir
                for key, value in tipo_data.items():
                    setattr(tipo, key, value)
                tipo.save()
                self.stdout.write(
                    self.style.WARNING(f'↻ Atualizado: {tipo.nome} - R$ {tipo.valor}')
                )
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {criados} tipos criados, {atualizados} tipos atualizados'
            )
        )
