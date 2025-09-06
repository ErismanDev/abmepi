"""
Comando para testar especificamente a configuração do Gmail
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Command(BaseCommand):
    help = 'Testa especificamente a configuração do Gmail'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email para envio do teste',
            default='siteabmepi@gmail.com'
        )
        parser.add_argument(
            '--test-smtp',
            action='store_true',
            help='Testa conexão SMTP diretamente',
        )
        parser.add_argument(
            '--test-app-password',
            action='store_true',
            help='Testa se a senha de aplicativo está correta',
        )

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write(
            self.style.SUCCESS('=== Teste Específico do Gmail ===')
        )
        
        # Verificar configurações
        self.stdout.write('\n1. Verificando configurações do Gmail...')
        self.stdout.write(f'   EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Não configurado")}')
        self.stdout.write(f'   EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Não configurado")}')
        self.stdout.write(f'   EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "Não configurado")}')
        self.stdout.write(f'   EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Não configurado")}')
        self.stdout.write(f'   EMAIL_HOST_PASSWORD: {"***" if getattr(settings, "EMAIL_HOST_PASSWORD", None) else "Não configurado"}')
        
        # Teste de conexão SMTP
        if options['test_smtp']:
            self.stdout.write('\n2. Testando conexão SMTP...')
            self._test_smtp_connection()
        
        # Teste de senha de aplicativo
        if options['test_app_password']:
            self.stdout.write('\n3. Testando senha de aplicativo...')
            self._test_app_password()
        
        # Teste de envio básico
        self.stdout.write('\n4. Testando envio básico...')
        self._test_basic_send(test_email)
        
        # Teste com backend de console
        self.stdout.write('\n5. Testando backend de console...')
        self._test_console_backend(test_email)
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Teste Concluído ===')
        )

    def _test_smtp_connection(self):
        """Testa conexão SMTP diretamente"""
        try:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.quit()
            self.stdout.write(
                self.style.SUCCESS('   ✅ Conexão SMTP bem-sucedida')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro na conexão SMTP: {str(e)}')
            )

    def _test_app_password(self):
        """Testa se a senha de aplicativo está correta"""
        try:
            # Tentar autenticar
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.quit()
            self.stdout.write(
                self.style.SUCCESS('   ✅ Senha de aplicativo válida')
            )
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro de autenticação: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('   💡 Verifique se a senha de aplicativo está correta')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro inesperado: {str(e)}')
            )

    def _test_basic_send(self, test_email):
        """Testa envio básico"""
        try:
            send_mail(
                subject='Teste Gmail - ABMEPI',
                message='Este é um teste específico do Gmail.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False
            )
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ Email enviado com sucesso para {test_email}')
            )
        except Exception as e:
            error_msg = str(e)
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro no envio: {error_msg}')
            )
            
            if "Daily user sending limit exceeded" in error_msg:
                self.stdout.write(
                    self.style.WARNING('   ⚠️ Limite diário do Gmail excedido')
                )
            elif "Authentication failed" in error_msg:
                self.stdout.write(
                    self.style.WARNING('   ⚠️ Problema de autenticação - verifique senha de aplicativo')
                )

    def _test_console_backend(self, test_email):
        """Testa backend de console"""
        try:
            connection = get_connection('django.core.mail.backends.console.EmailBackend')
            send_mail(
                subject='Teste Console - ABMEPI',
                message='Este é um teste usando backend de console.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                connection=connection,
                fail_silently=False
            )
            self.stdout.write(
                self.style.SUCCESS('   ✅ Backend de console funcionando')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro no backend de console: {str(e)}')
            )

