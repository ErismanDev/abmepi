"""
Comando para testar a configuração de email
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from core.services.email_service import email_batch_service


class Command(BaseCommand):
    help = 'Testa a configuração de email do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email para envio do teste',
            default='siteabmepi@gmail.com'
        )

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write(
            self.style.SUCCESS('=== Teste de Configuração de Email ===')
        )
        
        # Verificar configurações
        self.stdout.write('\n1. Verificando configurações...')
        self.stdout.write(f'   EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Não configurado")}')
        self.stdout.write(f'   EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Não configurado")}')
        self.stdout.write(f'   EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "Não configurado")}')
        self.stdout.write(f'   EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Não configurado")}')
        self.stdout.write(f'   DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "Não configurado")}')
        
        # Teste básico de envio
        self.stdout.write('\n2. Testando envio básico...')
        try:
            send_mail(
                subject='Teste de Configuração - ABMEPI',
                message='Este é um email de teste para verificar a configuração.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False
            )
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ Email básico enviado com sucesso para {test_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro no envio básico: {str(e)}')
            )
        
        # Teste do serviço de email em lote
        self.stdout.write('\n3. Testando serviço de email em lote...')
        try:
            success = email_batch_service.send_test_email(test_email)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ Email de teste do serviço enviado com sucesso para {test_email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Falha no envio do email de teste do serviço')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro no serviço de email: {str(e)}')
            )
        
        # Estatísticas
        self.stdout.write('\n4. Estatísticas do sistema...')
        try:
            from associados.models import Associado
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            total_associados = Associado.objects.filter(email__isnull=False).exclude(email='').count()
            associados_ativos = Associado.objects.filter(
                email__isnull=False, 
                email__gt='', 
                situacao='ativo'
            ).count()
            total_usuarios = User.objects.filter(email__isnull=False).exclude(email='').count()
            usuarios_ativos = User.objects.filter(
                email__isnull=False, 
                email__gt='', 
                is_active=True
            ).count()
            
            self.stdout.write(f'   Total de Associados: {total_associados}')
            self.stdout.write(f'   Associados Ativos: {associados_ativos}')
            self.stdout.write(f'   Total de Usuários: {total_usuarios}')
            self.stdout.write(f'   Usuários Ativos: {usuarios_ativos}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro ao obter estatísticas: {str(e)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Teste Concluído ===')
        )
