from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import AssejurNews
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria notícias de exemplo para a assessoria jurídica'

    def handle(self, *args, **options):
        # Verificar se já existem notícias
        if AssejurNews.objects.exists():
            self.stdout.write(
                self.style.WARNING('Já existem notícias no sistema. Pulando criação.')
            )
            return

        # Criar usuário admin se não existir
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@abmepi.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'tipo_usuario': 'administrador_sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuário admin criado: {admin_user.username}')
            )

        # Notícias de exemplo
        sample_news = [
            {
                'titulo': 'Nova Lei de Benefícios Previdenciários',
                'resumo': 'Atualizações importantes sobre a legislação previdenciária para militares e policiais em 2025.',
                'conteudo': 'A nova legislação previdenciária traz mudanças significativas para os militares e policiais. Entre as principais alterações estão:\n\n• Aumento do percentual de contribuição\n• Novos critérios para aposentadoria especial\n• Melhorias no sistema de benefícios por invalidez\n• Revisão dos valores de pensão por morte\n\nÉ fundamental que todos os associados estejam atentos a essas mudanças para garantir seus direitos.',
                'categoria': 'previdenciario',
                'icone': 'fas fa-gavel',
                'prioridade': 'alta',
                'destaque': True,
                'ordem_exibicao': 1,
                'ativo': True,
                'tags': 'previdenciário,benefícios,legislação,2025'
            },
            {
                'titulo': 'Processos Disciplinares: Orientações Importantes',
                'resumo': 'Guia completo sobre procedimentos e defesa em processos administrativos disciplinares.',
                'conteudo': 'Os processos disciplinares são uma realidade na carreira militar e policial. Este guia oferece orientações essenciais:\n\n• Direitos e deveres do acusado\n• Procedimentos administrativos\n• Prazos para defesa\n• Recursos disponíveis\n• Consequências das penalidades\n\nA assessoria jurídica está disponível para orientar associados em todas as etapas do processo.',
                'categoria': 'administrativo',
                'icone': 'fas fa-balance-scale',
                'prioridade': 'media',
                'destaque': False,
                'ordem_exibicao': 2,
                'ativo': True,
                'tags': 'processo,disciplinar,administrativo,defesa'
            },
            {
                'titulo': 'Promoções e Progressões na Carreira Militar',
                'resumo': 'Informações sobre critérios e procedimentos para promoções na carreira militar.',
                'conteudo': 'A progressão na carreira militar é um objetivo de muitos profissionais. Conheça os principais aspectos:\n\n• Critérios de avaliação\n• Tempo de serviço necessário\n• Cursos de formação\n• Avaliação de desempenho\n• Recursos contra indeferimento\n\nMantenha-se atualizado sobre as oportunidades de crescimento em sua carreira.',
                'categoria': 'militar',
                'icone': 'fas fa-shield-alt',
                'prioridade': 'media',
                'destaque': False,
                'ordem_exibicao': 3,
                'ativo': True,
                'tags': 'promoção,carreira,militar,progressão'
            },
            {
                'titulo': 'Direitos Trabalhistas dos Militares',
                'resumo': 'Conheça seus direitos trabalhistas e como a assessoria jurídica pode ajudar.',
                'conteudo': 'Os militares possuem direitos trabalhistas específicos que devem ser respeitados:\n\n• Jornada de trabalho\n• Adicional noturno\n• Férias e licenças\n• Benefícios sociais\n• Proteção contra assédio\n\nNossa assessoria jurídica especializada está pronta para defender seus direitos.',
                'categoria': 'trabalhista',
                'icone': 'fas fa-briefcase',
                'prioridade': 'baixa',
                'destaque': False,
                'ordem_exibicao': 4,
                'ativo': True,
                'tags': 'trabalhista,direitos,militar,assédio'
            },
            {
                'titulo': 'Reforma da Previdência: Impactos para Militares',
                'resumo': 'Análise dos impactos da reforma previdenciária na carreira militar.',
                'conteudo': 'A reforma da previdência trouxe mudanças significativas para todos os brasileiros, incluindo militares:\n\n• Idade mínima para aposentadoria\n• Tempo de contribuição\n• Cálculo do benefício\n• Transição para as novas regras\n\nEntenda como essas mudanças afetam seu planejamento de aposentadoria.',
                'categoria': 'previdenciario',
                'icone': 'fas fa-chart-line',
                'prioridade': 'alta',
                'destaque': True,
                'ordem_exibicao': 5,
                'ativo': True,
                'tags': 'reforma,previdência,aposentadoria,militar'
            }
        ]

        # Criar as notícias
        created_count = 0
        for i, news_data in enumerate(sample_news):
            # Calcular data de publicação (mais recente primeiro)
            days_ago = i
            data_publicacao = datetime.now() - timedelta(days=days_ago)
            
            news = AssejurNews.objects.create(
                titulo=news_data['titulo'],
                resumo=news_data['resumo'],
                conteudo=news_data['conteudo'],
                categoria=news_data['categoria'],
                icone=news_data['icone'],
                prioridade=news_data['prioridade'],
                destaque=news_data['destaque'],
                ordem_exibicao=news_data['ordem_exibicao'],
                ativo=news_data['ativo'],
                tags=news_data['tags'],
                data_publicacao=data_publicacao,
                autor=admin_user
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Notícia criada: {news.titulo}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Total de {created_count} notícias criadas com sucesso!')
        )
