from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Usuario


class Command(BaseCommand):
    help = 'Limpa senhas temporárias expiradas dos usuários'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria limpo sem executar a limpeza',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar usuários com senhas temporárias expiradas
        usuarios_com_senhas_expiradas = Usuario.objects.filter(
            senha_temporaria__isnull=False,
            senha_temporaria_expira__lt=timezone.now()
        )
        
        if not usuarios_com_senhas_expiradas.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ Nenhuma senha temporária expirada encontrada.')
            )
            return
        
        self.stdout.write(
            f'🔍 Encontradas {usuarios_com_senhas_expiradas.count()} senhas temporárias expiradas:'
        )
        
        for usuario in usuarios_com_senhas_expiradas:
            self.stdout.write(
                f'   - {usuario.username} ({usuario.get_full_name()}) - '
                f'Expirou em {usuario.senha_temporaria_expira.strftime("%d/%m/%Y %H:%M")}'
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 Modo DRY-RUN: Nenhuma alteração foi feita.')
            )
            return
        
        # Limpar senhas temporárias expiradas
        usuarios_afetados = usuarios_com_senhas_expiradas.update(
            senha_temporaria=None,
            senha_temporaria_expira=None
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {usuarios_afetados} senhas temporárias expiradas foram limpas com sucesso!'
            )
        )
