#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.views import InstitucionalView

def test_view():
    print("=== Teste da View Institucional ===")
    
    # Criar uma requisição fake com sessão
    factory = RequestFactory()
    request = factory.get('/')
    request.session = {}
    
    # Criar a view
    view = InstitucionalView()
    view.request = request
    
    # Obter o contexto
    context = view.get_context_data()
    
    # Verificar os dados
    print(f"Telefone no contexto: {context.get('telefone')}")
    print(f"Email no contexto: {context.get('email')}")
    print(f"Endereço no contexto: {context.get('endereco')}")
    
    # Verificar se config está no contexto
    if 'config' in context:
        config = context['config']
        print(f"Config ID: {config.id}")
        print(f"Config Telefone: {config.telefone}")
        print(f"Config Email: {config.email}")
        print(f"Config Endereço: {config.endereco}")
    
    print("=== Fim do Teste da View ===")

if __name__ == '__main__':
    test_view()
