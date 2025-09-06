#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig

def test_config():
    print("=== Teste de Configuração Institucional ===")
    
    # Obter configuração atual
    config = InstitucionalConfig.get_config()
    print(f"ID da configuração: {config.id}")
    print(f"Telefone atual: {config.telefone}")
    print(f"Email atual: {config.email}")
    print(f"Endereço atual: {config.endereco}")
    print(f"Data de atualização: {config.data_atualizacao}")
    
    # Verificar se existe apenas uma instância
    total_configs = InstitucionalConfig.objects.count()
    print(f"Total de configurações no banco: {total_configs}")
    
    # Listar todas as configurações
    all_configs = InstitucionalConfig.objects.all()
    for cfg in all_configs:
        print(f"  - Config ID {cfg.id}: {cfg.telefone} | {cfg.email} | {cfg.endereco}")
    
    print("\n=== Fim do Teste ===")

if __name__ == '__main__':
    test_config()
