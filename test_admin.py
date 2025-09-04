#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.models import Usuario
from asejus.views import advogado_modal_create

# Pegar usuário administrador
admin = Usuario.objects.filter(tipo_usuario='administrador_sistema').first()
print(f'Admin: {admin.username} ({admin.tipo_usuario})')

# Criar request
factory = RequestFactory()
request = factory.get('/assejus/advogados/modal/novo/')
request.user = admin
request.META['HTTP_ACCEPT'] = 'application/json'

# Chamar view
print('🔧 Testando view advogado_modal_create...')
response = advogado_modal_create(request)

print(f'✅ Status: {response.status_code}')
print(f'✅ Content-Type: {response.get("Content-Type", "N/A")}')

# Verificar conteúdo
content = response.content.decode('utf-8')
print(f'✅ Content (primeiros 200 chars): {content[:200]}')
print(f'✅ form_html presente: {"form_html" in content}')

if 'form_html' in content:
    print('🎉 SUCESSO! A view está retornando form_html corretamente!')
else:
    print('❌ PROBLEMA: form_html não encontrado na resposta')
    print(f'Conteúdo completo: {content}')
