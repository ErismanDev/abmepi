"""
Serviço de envio de emails em lote para o sistema ABMEPI
"""
import time
import logging
from typing import List, Dict, Any, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.core.cache import cache
from associados.models import Associado
from datetime import datetime, date

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailBatchService:
    """
    Serviço para envio de emails em lote
    """
    
    def __init__(self):
        self.batch_size = getattr(settings, 'EMAIL_BATCH_SIZE', 50)
        self.batch_delay = getattr(settings, 'EMAIL_BATCH_DELAY', 2)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'siteabmepi@gmail.com')
        self.daily_limit = getattr(settings, 'EMAIL_DAILY_LIMIT', 400)
        self.fallback_enabled = getattr(settings, 'EMAIL_FALLBACK_ENABLED', True)
        
    def send_batch_emails(
        self, 
        recipients: List[str], 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Envia emails em lote para uma lista de destinatários
        
        Args:
            recipients: Lista de emails dos destinatários
            subject: Assunto do email
            message: Mensagem em texto simples
            html_message: Mensagem em HTML (opcional)
            template_name: Nome do template HTML (opcional)
            context: Contexto para o template (opcional)
            attachments: Lista de anexos (opcional) - formato: [{'filename': 'nome.pdf', 'content': bytes, 'mimetype': 'application/pdf'}]
            force: Se True, ignora verificação de limites
            
        Returns:
            Dict com estatísticas do envio
        """
        total_recipients = len(recipients)
        successful_sends = 0
        failed_sends = 0
        failed_emails = []
        
        logger.info(f"Iniciando envio de {total_recipients} emails em lote")
        
        # Verificar limite diário se não for forçado
        if not force:
            limit_check = self._check_daily_limit(total_recipients)
            if not limit_check['can_send']:
                logger.warning(f"Limite diário atingido. Emails enviados hoje: {limit_check['current_count']}/{self.daily_limit}")
                
                # Adicionar à fila se habilitado
                if self.fallback_enabled:
                    queued = self._queue_emails_for_later(
                        recipients, subject, message, html_message, 
                        template_name, context, attachments
                    )
                    if queued:
                        return {
                            'total_recipients': total_recipients,
                            'successful_sends': 0,
                            'failed_sends': 0,
                            'failed_emails': [],
                            'success_rate': 0,
                            'queued': True,
                            'message': f'Emails adicionados à fila. Limite diário atingido ({limit_check["current_count"]}/{self.daily_limit})'
                        }
                
                return {
                    'total_recipients': total_recipients,
                    'successful_sends': 0,
                    'failed_sends': 0,
                    'failed_emails': [],
                    'success_rate': 0,
                    'queued': False,
                    'message': f'Limite diário atingido ({limit_check["current_count"]}/{self.daily_limit}). Emails não enviados.'
                }
        
        # Processar em lotes
        for i in range(0, total_recipients, self.batch_size):
            batch = recipients[i:i + self.batch_size]
            batch_number = (i // self.batch_size) + 1
            total_batches = (total_recipients + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processando lote {batch_number}/{total_batches} com {len(batch)} emails")
            
            # Enviar emails do lote atual
            for email in batch:
                try:
                    # Preparar mensagem
                    if template_name and context:
                        html_content = render_to_string(template_name, context)
                        text_content = strip_tags(html_content)
                    else:
                        html_content = html_message
                        text_content = message
                    
                    # Enviar email
                    if html_content:
                        msg = EmailMultiAlternatives(
                            subject=subject,
                            body=text_content,
                            from_email=self.from_email,
                            to=[email]
                        )
                        msg.attach_alternative(html_content, "text/html")
                        
                        # Adicionar anexos se existirem
                        if attachments:
                            for attachment in attachments:
                                msg.attach(
                                    attachment['filename'],
                                    attachment['content'],
                                    attachment.get('mimetype', 'application/octet-stream')
                                )
                        
                        msg.send()
                    else:
                        # Para emails simples, usar EmailMultiAlternatives para suportar anexos
                        msg = EmailMultiAlternatives(
                            subject=subject,
                            body=text_content,
                            from_email=self.from_email,
                            to=[email]
                        )
                        
                        # Adicionar anexos se existirem
                        if attachments:
                            for attachment in attachments:
                                msg.attach(
                                    attachment['filename'],
                                    attachment['content'],
                                    attachment.get('mimetype', 'application/octet-stream')
                                )
                        
                        msg.send()
                    
                    successful_sends += 1
                    logger.info(f"Email enviado com sucesso para: {email}")
                    
                except Exception as e:
                    failed_sends += 1
                    failed_emails.append(email)
                    logger.error(f"Erro ao enviar email para {email}: {str(e)}")
                    
                    # Verificar se é erro de limite do Gmail
                    if self._is_gmail_limit_error(e):
                        logger.error("Limite do Gmail atingido. Parando envio de emails.")
                        # Adicionar emails restantes à fila
                        remaining_emails = recipients[recipients.index(email):]
                        if self.fallback_enabled and remaining_emails:
                            self._queue_emails_for_later(
                                remaining_emails, subject, message, html_message,
                                template_name, context, attachments
                            )
                        break
            
            # Delay entre lotes (exceto no último lote)
            if i + self.batch_size < total_recipients:
                logger.info(f"Aguardando {self.batch_delay} segundos antes do próximo lote...")
                time.sleep(self.batch_delay)
        
        # Incrementar contador de emails enviados
        if successful_sends > 0:
            self._increment_daily_email_count(successful_sends)
        
        result = {
            'total_recipients': total_recipients,
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'failed_emails': failed_emails,
            'success_rate': (successful_sends / total_recipients * 100) if total_recipients > 0 else 0
        }
        
        logger.info(f"Envio em lote concluído: {successful_sends}/{total_recipients} emails enviados com sucesso")
        
        return result
    
    def _get_daily_email_count(self) -> int:
        """Obtém o número de emails enviados hoje"""
        today = date.today().strftime('%Y-%m-%d')
        cache_key = f'email_count_{today}'
        return cache.get(cache_key, 0)
    
    def _increment_daily_email_count(self, count: int = 1) -> int:
        """Incrementa o contador de emails diários"""
        today = date.today().strftime('%Y-%m-%d')
        cache_key = f'email_count_{today}'
        current_count = cache.get(cache_key, 0)
        new_count = current_count + count
        cache.set(cache_key, new_count, 86400)  # Expira em 24 horas
        return new_count
    
    def _check_daily_limit(self, emails_to_send: int) -> Dict[str, Any]:
        """Verifica se pode enviar a quantidade de emails solicitada"""
        current_count = self._get_daily_email_count()
        total_after_send = current_count + emails_to_send
        
        if total_after_send <= self.daily_limit:
            return {
                'can_send': True,
                'current_count': current_count,
                'emails_to_send': emails_to_send,
                'total_after': total_after_send,
                'remaining': self.daily_limit - total_after_send
            }
        else:
            return {
                'can_send': False,
                'current_count': current_count,
                'emails_to_send': emails_to_send,
                'total_after': total_after_send,
                'remaining': 0,
                'excess': total_after_send - self.daily_limit
            }
    
    def _is_gmail_limit_error(self, error: Exception) -> bool:
        """Verifica se o erro é relacionado ao limite do Gmail"""
        error_str = str(error).lower()
        return any(phrase in error_str for phrase in [
            'daily user sending limit exceeded',
            'quota exceeded',
            'rate limit exceeded',
            'too many requests'
        ])
    
    def _queue_emails_for_later(self, recipients: List[str], subject: str, 
                               message: str, html_message: Optional[str] = None,
                               template_name: Optional[str] = None,
                               context: Optional[Dict[str, Any]] = None,
                               attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Adiciona emails à fila para processamento posterior"""
        if not self.fallback_enabled:
            return False
        
        try:
            queue_key = f'email_queue_{date.today().strftime("%Y%m%d")}'
            queue_data = cache.get(queue_key, [])
            
            email_data = {
                'recipients': recipients,
                'subject': subject,
                'message': message,
                'html_message': html_message,
                'template_name': template_name,
                'context': context,
                'attachments': attachments,
                'queued_at': datetime.now().isoformat()
            }
            
            queue_data.append(email_data)
            cache.set(queue_key, queue_data, 604800)  # Expira em 7 dias
            
            logger.info(f"Adicionados {len(recipients)} emails à fila para processamento posterior")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar emails à fila: {str(e)}")
            return False
    
    def get_daily_email_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de emails do dia"""
        current_count = self._get_daily_email_count()
        queue_key = f'email_queue_{date.today().strftime("%Y%m%d")}'
        queue_data = cache.get(queue_key, [])
        
        queued_emails = sum(len(item['recipients']) for item in queue_data)
        
        return {
            'emails_sent_today': current_count,
            'daily_limit': self.daily_limit,
            'remaining_today': max(0, self.daily_limit - current_count),
            'queued_emails': queued_emails,
            'queue_items': len(queue_data),
            'can_send_more': current_count < self.daily_limit
        }
    
    def reset_daily_email_count(self) -> bool:
        """Reseta o contador de emails diários (para uso administrativo)"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            cache_key = f'email_count_{today}'
            cache.delete(cache_key)
            logger.info("Contador de emails diários resetado")
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar contador: {str(e)}")
            return False
    
    def clear_email_queue(self) -> bool:
        """Limpa a fila de emails pendentes"""
        try:
            queue_key = f'email_queue_{date.today().strftime("%Y%m%d")}'
            cache.delete(queue_key)
            logger.info("Fila de emails limpa")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar fila: {str(e)}")
            return False
    
    def process_email_queue(self, force: bool = False) -> Dict[str, Any]:
        """Processa a fila de emails pendentes"""
        queue_key = f'email_queue_{date.today().strftime("%Y%m%d")}'
        queue_data = cache.get(queue_key, [])
        
        if not queue_data:
            return {
                'success': True,
                'processed': 0,
                'message': 'Nenhum email na fila para processar'
            }
        
        processed = 0
        failed = 0
        
        for email_data in queue_data:
            try:
                # Verificar limite se não for forçado
                if not force:
                    limit_check = self._check_daily_limit(len(email_data['recipients']))
                    if not limit_check['can_send']:
                        logger.warning(f"Limite diário atingido. Parando processamento da fila.")
                        break
                
                # Enviar emails
                result = self.send_batch_emails(
                    recipients=email_data['recipients'],
                    subject=email_data['subject'],
                    message=email_data['message'],
                    html_message=email_data.get('html_message'),
                    template_name=email_data.get('template_name'),
                    context=email_data.get('context'),
                    attachments=email_data.get('attachments')
                )
                
                if result['successful_sends'] > 0:
                    processed += result['successful_sends']
                    # Remover item processado da fila
                    queue_data.remove(email_data)
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Erro ao processar item da fila: {str(e)}")
                failed += 1
        
        # Atualizar fila
        cache.set(queue_key, queue_data, 604800)
        
        return {
            'success': True,
            'processed': processed,
            'failed': failed,
            'remaining_in_queue': len(queue_data)
        }
    
    def send_to_all_associados(
        self, 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        filter_active: bool = True,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia email para todos os associados
        
        Args:
            subject: Assunto do email
            message: Mensagem em texto simples
            html_message: Mensagem em HTML (opcional)
            template_name: Nome do template HTML (opcional)
            context: Contexto para o template (opcional)
            filter_active: Se True, envia apenas para associados ativos
            
        Returns:
            Dict com estatísticas do envio
        """
        # Buscar emails dos associados
        queryset = Associado.objects.filter(email__isnull=False).exclude(email='')
        
        if filter_active:
            queryset = queryset.filter(situacao='ativo')
        
        recipients = list(queryset.values_list('email', flat=True).distinct())
        
        logger.info(f"Enviando email para {len(recipients)} associados")
        
        return self.send_batch_emails(
            recipients=recipients,
            subject=subject,
            message=message,
            html_message=html_message,
            template_name=template_name,
            context=context,
            attachments=attachments
        )
    
    def send_to_all_users(
        self, 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        filter_active: bool = True,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia email para todos os usuários do sistema
        
        Args:
            subject: Assunto do email
            message: Mensagem em texto simples
            html_message: Mensagem em HTML (opcional)
            template_name: Nome do template HTML (opcional)
            context: Contexto para o template (opcional)
            filter_active: Se True, envia apenas para usuários ativos
            
        Returns:
            Dict com estatísticas do envio
        """
        # Buscar emails dos usuários
        queryset = User.objects.filter(email__isnull=False).exclude(email='')
        
        if filter_active:
            queryset = queryset.filter(is_active=True)
        
        recipients = list(queryset.values_list('email', flat=True).distinct())
        
        logger.info(f"Enviando email para {len(recipients)} usuários")
        
        return self.send_batch_emails(
            recipients=recipients,
            subject=subject,
            message=message,
            html_message=html_message,
            template_name=template_name,
            context=context,
            attachments=attachments
        )
    
    def send_to_custom_list(
        self, 
        email_list: List[str], 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia email para uma lista customizada de emails
        
        Args:
            email_list: Lista de emails
            subject: Assunto do email
            message: Mensagem em texto simples
            html_message: Mensagem em HTML (opcional)
            template_name: Nome do template HTML (opcional)
            context: Contexto para o template (opcional)
            
        Returns:
            Dict com estatísticas do envio
        """
        # Remover emails duplicados e vazios
        recipients = list(set([email.strip() for email in email_list if email.strip()]))
        
        logger.info(f"Enviando email para {len(recipients)} emails customizados")
        
        return self.send_batch_emails(
            recipients=recipients,
            subject=subject,
            message=message,
            html_message=html_message,
            template_name=template_name,
            context=context,
            attachments=attachments
        )
    
    def send_to_specific_users(
        self, 
        user_ids: List[int], 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia email para usuários específicos do sistema
        
        Args:
            user_ids: Lista de IDs dos usuários
            subject: Assunto do email
            message: Mensagem em texto simples
            html_message: Mensagem em HTML (opcional)
            template_name: Nome do template HTML (opcional)
            context: Contexto para o template (opcional)
            attachments: Lista de anexos (opcional)
            
        Returns:
            Dict com estatísticas do envio
        """
        # Buscar emails dos usuários específicos
        queryset = User.objects.filter(
            id__in=user_ids,
            email__isnull=False
        ).exclude(email='')
        
        recipients = list(queryset.values_list('email', flat=True).distinct())
        
        logger.info(f"Enviando email para {len(recipients)} usuários específicos")
        
        return self.send_batch_emails(
            recipients=recipients,
            subject=subject,
            message=message,
            html_message=html_message,
            template_name=template_name,
            context=context,
            attachments=attachments
        )
    
    def send_test_email(self, test_email: str) -> bool:
        """
        Envia um email de teste para verificar a configuração
        
        Args:
            test_email: Email para envio do teste
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            subject = 'Teste de Configuração - ABMEPI'
            message = f"""
            Este é um email de teste enviado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.
            
            Se você recebeu este email, a configuração de envio está funcionando corretamente.
            
            Atenciosamente,
            Sistema ABMEPI
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[test_email],
                fail_silently=False
            )
            
            logger.info(f"Email de teste enviado com sucesso para: {test_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de teste para {test_email}: {str(e)}")
            return False


# Instância global do serviço
email_batch_service = EmailBatchService()
