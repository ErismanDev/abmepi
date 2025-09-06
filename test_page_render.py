#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory
from core.views import InstitucionalView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_page_render():
    print("=== Teste de Renderização da Página Institucional ===")
    
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
    print(f"Telefone no contexto: {context.get('telefone')}")
    
    # Tentar renderizar o template
    try:
        html = render_to_string('core/institucional.html', context)
        print("✅ Template renderizado com sucesso!")
        
        # Verificar se o telefone está no HTML renderizado
        telefone_atual = context['telefone']
        if telefone_atual in html:
            print(f"✅ Valor do telefone '{telefone_atual}' encontrado no HTML")
        else:
            print(f"❌ Valor do telefone '{telefone_atual}' NÃO encontrado no HTML")
            
        # Verificar se há algum problema com o template
        if '{{ telefone }}' in html:
            print("❌ Template não foi processado - ainda tem variáveis Django")
        else:
            print("✅ Template foi processado corretamente")
            
    except Exception as e:
        print(f"❌ Erro ao renderizar template: {e}")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_page_render()
