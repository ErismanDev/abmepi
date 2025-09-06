from django.core.management.base import BaseCommand
from financeiro.models import ConfiguracaoCobranca


class Command(BaseCommand):
    help = 'Limpa configurações duplicadas de cobrança e garante que só exista uma ativa'

    def handle(self, *args, **options):
        self.stdout.write('Limpando configurações de cobrança...')
        
        # Contar configurações existentes
        total_configs = ConfiguracaoCobranca.objects.count()
        self.stdout.write(f'Total de configurações encontradas: {total_configs}')
        
        if total_configs == 0:
            # Criar configuração padrão se não existir
            config = ConfiguracaoCobranca.objects.create(
                nome="Configuração Padrão",
                ativo=True,
                chave_pix="86 988197790",
                titular="Gustavo Henrique de Araujo Sousa",
                banco="MERCADO PAGO"
            )
            self.stdout.write(
                self.style.SUCCESS(f'Configuração padrão criada com ID: {config.id}')
            )
            return
        
        # Se existir mais de uma configuração, manter apenas a primeira e desativar as outras
        if total_configs > 1:
            # Obter a primeira configuração (mais antiga)
            primeira_config = ConfiguracaoCobranca.objects.order_by('data_criacao').first()
            
            # Desativar todas as outras
            outras_configs = ConfiguracaoCobranca.objects.exclude(id=primeira_config.id)
            outras_configs.update(ativo=False)
            
            # Ativar a primeira
            primeira_config.ativo = True
            primeira_config.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Configuração {primeira_config.nome} (ID: {primeira_config.id}) mantida ativa. '
                    f'{outras_configs.count()} outras configurações foram desativadas.'
                )
            )
        else:
            # Só existe uma configuração, garantir que esteja ativa
            config = ConfiguracaoCobranca.objects.first()
            if not config.ativo:
                config.ativo = True
                config.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Configuração {config.nome} (ID: {config.id}) foi ativada.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Configuração {config.nome} (ID: {config.id}) já está ativa.')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Limpeza de configurações concluída com sucesso!')
        )
