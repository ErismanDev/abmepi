"""
Comando para testar as funcionalidades avançadas de email (anexos e usuários específicos)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.services.email_service import email_batch_service
import io

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa as funcionalidades avançadas de email (anexos e usuários específicos)'

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
            self.style.SUCCESS('=== Teste de Funcionalidades Avançadas de Email ===')
        )
        
        # Teste 1: Email com anexo
        self.stdout.write('\n1. Testando envio de email com anexo...')
        try:
            # Criar um anexo de teste (arquivo de texto)
            test_content = "Este é um arquivo de teste para anexo de email.\nSistema ABMEPI - Teste de funcionalidade."
            test_attachment = {
                'filename': 'teste_anexo.txt',
                'content': test_content.encode('utf-8'),
                'mimetype': 'text/plain'
            }
            
            result = email_batch_service.send_to_custom_list(
                email_list=[test_email],
                subject='Teste de Email com Anexo - ABMEPI',
                message='Este email contém um anexo de teste.',
                attachments=[test_attachment]
            )
            
            if result['successful_sends'] > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ Email com anexo enviado com sucesso para {test_email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Falha no envio de email com anexo')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro no teste de anexo: {str(e)}')
            )
        
        # Teste 2: Email para usuários específicos
        self.stdout.write('\n2. Testando envio para usuários específicos...')
        try:
            # Buscar alguns usuários para teste
            users = User.objects.filter(email__isnull=False).exclude(email='')[:2]
            
            if users.exists():
                user_ids = list(users.values_list('id', flat=True))
                user_emails = list(users.values_list('email', flat=True))
                
                result = email_batch_service.send_to_specific_users(
                    user_ids=user_ids,
                    subject='Teste de Email para Usuários Específicos - ABMEPI',
                    message='Este é um teste de envio para usuários específicos do sistema.'
                )
                
                if result['successful_sends'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✓ Email enviado para {result["successful_sends"]} usuário(s) específico(s)')
                    )
                    self.stdout.write(f'   Emails: {", ".join(user_emails)}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'   ✗ Falha no envio para usuários específicos')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('   ⚠ Nenhum usuário com email encontrado para teste')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro no teste de usuários específicos: {str(e)}')
            )
        
        # Teste 3: Email com múltiplos anexos
        self.stdout.write('\n3. Testando envio com múltiplos anexos...')
        try:
            # Criar múltiplos anexos de teste
            attachments = [
                {
                    'filename': 'documento1.txt',
                    'content': 'Conteúdo do primeiro documento de teste.'.encode('utf-8'),
                    'mimetype': 'text/plain'
                },
                {
                    'filename': 'documento2.txt',
                    'content': 'Conteúdo do segundo documento de teste.'.encode('utf-8'),
                    'mimetype': 'text/plain'
                }
            ]
            
            result = email_batch_service.send_to_custom_list(
                email_list=[test_email],
                subject='Teste de Email com Múltiplos Anexos - ABMEPI',
                message='Este email contém múltiplos anexos de teste.',
                attachments=attachments
            )
            
            if result['successful_sends'] > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ Email com múltiplos anexos enviado com sucesso para {test_email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Falha no envio de email com múltiplos anexos')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro no teste de múltiplos anexos: {str(e)}')
            )
        
        # Estatísticas finais
        self.stdout.write('\n4. Estatísticas do sistema...')
        try:
            total_users = User.objects.filter(email__isnull=False).exclude(email='').count()
            active_users = User.objects.filter(
                email__isnull=False, 
                email__gt='', 
                is_active=True
            ).count()
            
            self.stdout.write(f'   Total de Usuários com Email: {total_users}')
            self.stdout.write(f'   Usuários Ativos com Email: {active_users}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Erro ao obter estatísticas: {str(e)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Teste de Funcionalidades Avançadas Concluído ===')
        )
