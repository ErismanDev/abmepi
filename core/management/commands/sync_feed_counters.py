from django.core.management.base import BaseCommand
from core.models import FeedPost


class Command(BaseCommand):
    help = 'Sincroniza os contadores de likes e comentários dos posts do feed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--post-id',
            type=int,
            help='ID específico de um post para sincronizar',
        )

    def handle(self, *args, **options):
        post_id = options.get('post_id')
        
        if post_id:
            try:
                post = FeedPost.objects.get(id=post_id)
                counters = post.sync_counters()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Post "{post.titulo}" sincronizado: '
                        f'{counters["likes"]} likes, {counters["comentarios"]} comentários'
                    )
                )
            except FeedPost.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Post com ID {post_id} não encontrado')
                )
        else:
            # Sincronizar todos os posts
            posts = FeedPost.objects.all()
            total_posts = posts.count()
            
            self.stdout.write(f'Sincronizando {total_posts} posts...')
            
            for i, post in enumerate(posts, 1):
                counters = post.sync_counters()
                self.stdout.write(
                    f'[{i}/{total_posts}] {post.titulo}: '
                    f'{counters["likes"]} likes, {counters["comentarios"]} comentários'
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Sincronização concluída para {total_posts} posts!')
            )
