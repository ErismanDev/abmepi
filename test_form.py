#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.forms import InstitucionalConfigForm
from core.models import InstitucionalConfig

def test_form():
    print("=== Teste do Formulário ===")
    
    # Obter configuração atual
    config = InstitucionalConfig.get_config()
    print(f"Config no banco - ID: {config.id}")
    print(f"Config no banco - Telefone: {config.telefone}")
    print(f"Config no banco - Email: {config.email}")
    print(f"Config no banco - Endereço: {config.endereco}")
    
    # Criar formulário com dados da instância
    form = InstitucionalConfigForm(instance=config)
    
    # Verificar dados do formulário
    print(f"\nFormulário - Telefone: {form['telefone'].value()}")
    print(f"Formulário - Email: {form['email'].value()}")
    print(f"Formulário - Endereço: {form['endereco'].value()}")
    
    # Verificar se os valores são iguais
    print(f"\nTelefone igual? {config.telefone == form['telefone'].value()}")
    print(f"Email igual? {config.email == form['email'].value()}")
    print(f"Endereço igual? {config.endereco == form['endereco'].value()}")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_form()
