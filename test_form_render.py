#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory
from core.views import InstitucionalConfigEditView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_form_render():
    print("=== Teste de Renderização do Formulário ===")
    
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
    
    # Criar a view
    view = InstitucionalConfigEditView()
    view.request = request
    view.object = view.get_object()
    
    # Obter o contexto
    context = view.get_context_data()
    
    print(f"Contexto obtido com sucesso: {len(context)} variáveis")
    print(f"Objeto no contexto: {context.get('object')}")
    print(f"Formulário no contexto: {context.get('form')}")
    
    # Verificar se o formulário está sendo renderizado corretamente
    form = context['form']
    print(f"\nCampo telefone:")
    print(f"  - ID: {form['telefone'].id_for_label}")
    print(f"  - Valor: {form['telefone'].value()}")
    print(f"  - HTML: {form['telefone']}")
    
    # Tentar renderizar apenas o campo telefone
    try:
        telefone_html = form['telefone'].as_widget()
        print(f"\nHTML do campo telefone:")
        print(telefone_html)
        
        # Verificar se o valor está no HTML
        if str(form['telefone'].value()) in str(telefone_html):
            print("✅ Valor do telefone encontrado no HTML do campo")
        else:
            print("❌ Valor do telefone NÃO encontrado no HTML do campo")
            
    except Exception as e:
        print(f"❌ Erro ao renderizar campo telefone: {e}")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_form_render()
