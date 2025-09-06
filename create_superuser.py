#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# CPF no formato correto XXX.XXX.XXX-XX
cpf = '490.083.823-34'

# Criar superusuário se não existir
if not User.objects.filter(username=cpf).exists():
    user = User.objects.create_superuser(
        username=cpf,
        email='admin@abmepi.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        tipo_usuario='administrador_sistema'
    )
    print('Superusuário criado com sucesso!')
    print(f'CPF: {cpf}')
    print('Email: admin@abmepi.com')
    print('Senha: admin123')
    print('Tipo: Administrador')
else:
    print(f'Superusuário com CPF {cpf} já existe!')
