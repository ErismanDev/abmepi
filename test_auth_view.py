#!/usr/bin/env python
"""
Script para testar a view advogado_modal_create com autenticação
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from asejus.views import advogado_modal_create

def test_view_with_auth():
    """Testa a view com usuário autenticado"""
    
    # Criar usuário de teste
    User = get_user_model()
    
    # Autenticar usuário
    user = authenticate(username='123.456.789-00', password='teste123')
    if not user:
        print("❌ Falha na autenticação")
        return
    
    print(f"✅ Usuário autenticado: {user.username} ({user.tipo_usuario})")
    
    # Criar request factory
    factory = RequestFactory()
    
    # Criar requisição GET
    request = factory.get('/assejus/advogados/modal/novo/')
    request.user = user
    
    # Simular headers AJAX
    request.META['HTTP_ACCEPT'] = 'application/json'
    
    print("🔧 Testando view advogado_modal_create...")
    
    try:
        # Chamar a view
        response = advogado_modal_create(request)
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Content-Type: {response.get('Content-Type', 'N/A')}")
        
        # Verificar se é JSON
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"✅ Conteúdo (primeiros 200 chars): {content[:200]}")
            
            # Verificar se contém form_html
            if 'form_html' in content:
                print("✅ ✅ form_html encontrado na resposta!")
            else:
                print("❌ form_html NÃO encontrado na resposta")
        else:
            print("❌ Resposta não tem content")
            
    except Exception as e:
        print(f"❌ Erro ao chamar view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_view_with_auth()
