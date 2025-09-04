from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.permissions import (
    get_user_permissions, has_permission, can_access_assejus, 
    can_access_psicologia, can_access_paciente_ficha
)

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Testa as permissões do sistema baseadas nos tipos de usuário'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Testando Sistema de Permissões ===\n')
        )
        
        # Testar com diferentes tipos de usuário
        test_users = [
            'administrador_sistema',
            'advogado', 
            'psicologo',
            'atendente_advogado',
            'atendente_psicologo',
            'atendente_geral',
            'associado'
        ]
        
        for tipo in test_users:
            self.stdout.write(f'\n--- Testando usuário tipo: {tipo} ---')
            
            # Criar usuário de teste
            user, created = Usuario.objects.get_or_create(
                username=f'test_{tipo}',
                defaults={
                    'email': f'test_{tipo}@example.com',
                    'tipo_usuario': tipo,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('test123')
                user.save()
                self.stdout.write(f'  ✓ Usuário criado: {user.username}')
            else:
                user.tipo_usuario = tipo
                user.save()
                self.stdout.write(f'  ✓ Usuário existente: {user.username}')
            
            # Testar permissões
            permissions = get_user_permissions(user)
            self.stdout.write(f'  Permissões: {permissions}')
            
            # Testar funcionalidades específicas
            self.stdout.write(f'  Acesso ASEJUS: {can_access_assejus(user)}')
            self.stdout.write(f'  Acesso Psicologia: {can_access_psicologia(user)}')
            self.stdout.write(f'  Acesso Ficha Paciente: {can_access_paciente_ficha(user)}')
            
            # Testar permissões específicas
            if has_permission(user, 'assejus_access'):
                self.stdout.write('  ✓ Tem acesso ao módulo ASEJUS')
            if has_permission(user, 'psicologia_access'):
                self.stdout.write('  ✓ Tem acesso ao módulo Psicologia')
            if has_permission(user, 'paciente_ficha_access'):
                self.stdout.write('  ✓ Tem acesso às fichas de pacientes')
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Teste de Permissões Concluído ===')
        )
        
        # Mostrar resumo
        self.stdout.write('\n--- Resumo das Permissões ---')
        for tipo in test_users:
            count = Usuario.objects.filter(tipo_usuario=tipo).count()
            self.stdout.write(f'{tipo}: {count} usuário(s)')
