from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FeedPost
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Cria posts de exemplo para o feed social'

    def handle(self, *args, **options):
        # Limpar posts existentes de teste
        FeedPost.objects.filter(titulo__icontains='Post de Teste').delete()
        
        # Dados de exemplo para os posts
        sample_posts = [
            {
                'titulo': 'Post de Teste 1 - Evento da ABMEPI',
                'conteudo': 'Estamos muito felizes em anunciar nosso próximo evento! Será uma oportunidade incrível para networking e aprendizado.',
                'tipo_post': 'evento',
                'ativo': True,
                'destaque': True,
                'ordem_exibicao': 1,
                'data_publicacao': timezone.now() - timedelta(days=1)
            },
            {
                'titulo': 'Post de Teste 2 - Novidades da Associação',
                'conteudo': 'Temos novidades importantes para compartilhar com todos os associados. Fiquem atentos às próximas atualizações!',
                'tipo_post': 'noticia',
                'ativo': True,
                'destaque': True,
                'ordem_exibicao': 2,
                'data_publicacao': timezone.now() - timedelta(days=2)
            },
            {
                'titulo': 'Post de Teste 3 - Dicas para Associados',
                'conteudo': 'Aqui estão algumas dicas valiosas para aproveitar ao máximo sua associação na ABMEPI. Confira!',
                'tipo_post': 'dica',
                'ativo': True,
                'destaque': False,
                'ordem_exibicao': 3,
                'data_publicacao': timezone.now() - timedelta(days=3)
            },
            {
                'titulo': 'Post de Teste 4 - Comunidade Ativa',
                'conteudo': 'Nossa comunidade está cada vez mais ativa e engajada. Obrigado a todos que participam e contribuem!',
                'tipo_post': 'comunidade',
                'ativo': True,
                'destaque': False,
                'ordem_exibicao': 4,
                'data_publicacao': timezone.now() - timedelta(days=4)
            },
            {
                'titulo': 'Post de Teste 5 - Recursos Disponíveis',
                'conteudo': 'Descubra todos os recursos e benefícios disponíveis para nossos associados. Há muito mais do que você imagina!',
                'tipo_post': 'recurso',
                'ativo': True,
                'destaque': False,
                'ordem_exibicao': 5,
                'data_publicacao': timezone.now() - timedelta(days=5)
            }
        ]
        
        created_posts = []
        for post_data in sample_posts:
            post = FeedPost.objects.create(**post_data)
            created_posts.append(post)
            self.stdout.write(
                self.style.SUCCESS(f'Post criado: {post.titulo}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de {len(created_posts)} posts de teste criados com sucesso!')
        )
        
        # Mostrar estatísticas
        total_posts = FeedPost.objects.filter(ativo=True).count()
        self.stdout.write(f'Total de posts ativos no sistema: {total_posts}')
