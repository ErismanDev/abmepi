"""
Comando para processar a fila de emails pendentes
"""
from django.core.management.base import BaseCommand
from core.services.email_service import email_batch_service


class Command(BaseCommand):
    help = 'Processa a fila de emails pendentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa a fila de emails sem processar',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostra apenas o status da fila',
        )
        parser.add_argument(
            '--reset-counter',
            action='store_true',
            help='Reseta o contador de emails diários (CUIDADO: use apenas em emergências)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força o processamento da fila ignorando limites (CUIDADO: pode exceder limites do Gmail)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            success = email_batch_service.clear_email_queue()
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Fila de emails limpa com sucesso')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Erro ao limpar fila de emails')
                )
            return

        if options['reset_counter']:
            self.stdout.write(
                self.style.WARNING('⚠️ ATENÇÃO: Resetando contador de emails diários...')
            )
            success = email_batch_service.reset_daily_email_count()
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Contador de emails resetado com sucesso')
                )
                self.stdout.write(
                    self.style.WARNING('⚠️ Lembre-se: O Gmail ainda pode ter limites ativos!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Erro ao resetar contador de emails')
                )
            return

        if options['status']:
            self._show_status()
            return

        # Processar fila
        if options['force']:
            self.stdout.write(
                self.style.WARNING('⚠️ ATENÇÃO: Processando fila com envio forçado (ignorando limites)')
            )
            result = self._process_queue_forced()
        else:
            self.stdout.write(
                self.style.SUCCESS('=== Processando Fila de Emails ===')
            )
            result = email_batch_service.process_email_queue()
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f"✅ {result['message']}")
            )
            if result.get('processed', 0) > 0:
                self.stdout.write(f"   📧 Emails processados: {result['processed']}")
            if result.get('failed', 0) > 0:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️ Emails que falharam: {result['failed']}")
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ {result['message']}")
            )

    def _show_status(self):
        """Mostra o status da fila e estatísticas de email"""
        self.stdout.write(
            self.style.SUCCESS('=== Status do Sistema de Emails ===')
        )
        
        # Estatísticas diárias
        stats = email_batch_service.get_daily_email_stats()
        self.stdout.write(f"\n📊 Estatísticas Diárias:")
        self.stdout.write(f"   Emails enviados hoje: {stats['emails_sent_today']}")
        self.stdout.write(f"   Limite diário: {stats['daily_limit']}")
        self.stdout.write(f"   Restantes: {stats['remaining_today']}")
        
        percentage_used = (stats['emails_sent_today'] / stats['daily_limit'] * 100) if stats['daily_limit'] > 0 else 0
        self.stdout.write(f"   Percentual usado: {percentage_used:.1f}%")
        
        # Status da fila
        self.stdout.write(f"\n📬 Status da Fila:")
        self.stdout.write(f"   Lotes na fila: {stats['queue_items']}")
        self.stdout.write(f"   Total de emails na fila: {stats['queued_emails']}")
        
        if stats['queued_emails'] > 0:
            self.stdout.write(
                self.style.WARNING("   ⚠️ Há emails na fila aguardando processamento")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("   ✅ Nenhum email na fila")
            )
    
    def _process_queue_forced(self):
        """Processa a fila de emails com envio forçado"""
        from django.core.cache import cache
        from datetime import date
        
        queue_key = f"email_queue_{date.today().isoformat()}"
        current_queue = cache.get(queue_key, [])
        
        if not current_queue:
            return {
                'success': True,
                'message': 'Nenhum email na fila para processar',
                'processed': 0
            }
        
        processed_count = 0
        failed_count = 0
        
        for email_data in current_queue:
            try:
                result = email_batch_service.send_batch_emails(
                    recipients=email_data['recipients'],
                    subject=email_data['subject'],
                    message=email_data['message'],
                    html_message=email_data.get('html_message'),
                    template_name=email_data.get('template_name'),
                    context=email_data.get('context'),
                    attachments=email_data.get('attachments'),
                    force=True  # Forçar envio ignorando limites
                )
                
                if result.get('successful_sends', 0) > 0:
                    processed_count += result['successful_sends']
                else:
                    failed_count += len(email_data['recipients'])
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao processar email da fila: {e}")
                )
                failed_count += len(email_data['recipients'])
        
        # Limpar fila processada
        cache.delete(queue_key)
        
        return {
            'success': True,
            'message': f'Fila processada com envio forçado: {processed_count} emails enviados, {failed_count} falharam',
            'processed': processed_count,
            'failed': failed_count
        }
