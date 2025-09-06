#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig

def update_phone():
    print("=== Atualizando Telefone ===")
    
    # Obter configuração atual
    config = InstitucionalConfig.get_config()
    print(f"Telefone ANTES: {config.telefone}")
    
    # Atualizar telefone
    config.telefone = "(11) 1234-5678"
    config.save()
    
    # Recarregar do banco
    config.refresh_from_db()
    print(f"Telefone DEPOIS: {config.telefone}")
    
    # Verificar se foi salvo
    config_check = InstitucionalConfig.objects.get(pk=config.pk)
    print(f"Telefone no banco: {config_check.telefone}")
    
    print("=== Telefone Atualizado ===")

if __name__ == '__main__':
    update_phone()
