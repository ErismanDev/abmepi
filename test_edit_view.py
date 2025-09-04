#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.views import InstitucionalConfigEditView
from django.contrib.auth import get_user_model

User = get_user_model()

def test_edit_view():
    print("=== Teste da View de Edição ===")
    
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
    
    # Obter o objeto
    obj = view.get_object()
    print(f"Objeto obtido - ID: {obj.id}")
    print(f"Objeto obtido - Telefone: {obj.telefone}")
    print(f"Objeto obtido - Email: {obj.email}")
    print(f"Objeto obtido - Endereço: {obj.endereco}")
    
    # Simular o que a view faz
    view.object = obj
    
    # Obter o contexto
    context = view.get_context_data()
    
    # Verificar se o objeto está no contexto
    if 'object' in context:
        obj_context = context['object']
        print(f"\nObjeto no contexto - ID: {obj_context.id}")
        print(f"Objeto no contexto - Telefone: {obj_context.telefone}")
        print(f"Objeto no contexto - Email: {obj_context.email}")
        print(f"Objeto no contexto - Endereço: {obj_context.endereco}")
    
    # Verificar se o formulário está no contexto
    if 'form' in context:
        form = context['form']
        print(f"\nFormulário no contexto - Telefone: {form['telefone'].value()}")
        print(f"Formulário no contexto - Email: {form['email'].value()}")
        print(f"Formulário no contexto - Endereço: {form['endereco'].value()}")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_edit_view()
