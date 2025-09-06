#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import authenticate
from asejus.views import advogado_modal_create

# Autenticar usuário
user = authenticate(username='123.456.789-00', password='teste123')
print(f'Usuário: {user}')

# Criar request
factory = RequestFactory()
request = factory.get('/assejus/advogados/modal/novo/')
request.user = user
request.META['HTTP_ACCEPT'] = 'application/json'

# Chamar view
response = advogado_modal_create(request)
print(f'Status: {response.status_code}')
print(f'Content-Type: {response.get("Content-Type", "N/A")}')

# Verificar conteúdo
content = response.content.decode('utf-8')
print(f'Content (200 chars): {content[:200]}')
print(f'form_html presente: {"form_html" in content}')
