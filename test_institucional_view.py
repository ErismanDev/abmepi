#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.views import InstitucionalView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_institucional_view():
    print("=== Teste da View Institucional ===")
    
    # Criar uma requisição fake
    factory = RequestFactory()
    request = factory.get('/')
    
    # Criar um usuário fake para o teste
    user, created = User.objects.get_or_create(
        username='111.111.111-11',
        defaults={
            'first_name': 'Teste',
            'last_name': 'Usuário',
            'email': 'teste@teste.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Simular usuário autenticado
    request.user = user
    
    # Simular sessão
    request.session = {}
    
    # Criar a view
    view = InstitucionalView()
    view.request = request
    
    # Obter o contexto
    context = view.get_context_data()
    
    print(f"Contexto obtido com sucesso: {len(context)} variáveis")
    
    # Verificar se a configuração está no contexto
    if 'config' in context:
        config = context['config']
        print(f"Config no contexto:")
        print(f"  - ID: {config.id}")
        print(f"  - Telefone: {config.telefone}")
        print(f"  - Email: {config.email}")
        print(f"  - Endereço: {config.endereco}")
        print(f"  - Data de atualização: {config.data_atualizacao}")
    else:
        print("❌ Configuração não encontrada no contexto")
    
    # Verificar outras variáveis importantes
    print(f"\nOutras variáveis no contexto:")
    for key, value in context.items():
        if key != 'config':
            print(f"  - {key}: {type(value).__name__}")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_institucional_view()
