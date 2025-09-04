#!/usr/bin/env python
"""
Script de teste para verificar se a criação de psicólogo funciona corretamente
após a correção do erro de username muito longo.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from psicologia.forms import PsicologoForm
from psicologia.models import Psicologo
from django.contrib.auth import get_user_model

def test_psicologo_creation():
    """Testa a criação de psicólogo com diferentes cenários"""
    print("🧪 Testando criação de psicólogo...")
    
    # Cenário 1: Psicólogo com CPF (deve usar CPF como username)
    print("\n1. Testando com CPF...")
    form_data_cpf = {
        'nome_completo': 'João Silva Santos',
        'crp': '123456',
        'uf_crp': 'SP',
        'cpf': '123.456.789-01',
        'email': 'joao.silva@email.com',
        'telefone': '(11) 99999-9999',
    }
    
    form = PsicologoForm(data=form_data_cpf)
    if form.is_valid():
        try:
            psicologo = form.save()
            print(f"✅ Psicólogo criado com sucesso: {psicologo.nome_completo}")
            print(f"   Username: {psicologo.user.username}")
            print(f"   CPF: {psicologo.cpf}")
            # Limpar
            psicologo.user.delete()
            psicologo.delete()
        except Exception as e:
            print(f"❌ Erro ao criar psicólogo: {e}")
    else:
        print(f"❌ Formulário inválido: {form.errors}")
    
    # Cenário 2: Psicólogo sem CPF, com email longo
    print("\n2. Testando sem CPF, com email longo...")
    form_data_email_longo = {
        'nome_completo': 'Maria Fernanda Oliveira Santos',
        'crp': '987654321',
        'uf_crp': 'RJ',
        'email': 'maria.fernanda.oliveira.santos@empresa.com.br',
        'telefone': '(21) 88888-8888',
    }
    
    form = PsicologoForm(data=form_data_email_longo)
    if form.is_valid():
        try:
            psicologo = form.save()
            print(f"✅ Psicólogo criado com sucesso: {psicologo.nome_completo}")
            print(f"   Username: {psicologo.user.username}")
            print(f"   Email: {psicologo.email}")
            # Limpar
            psicologo.user.delete()
            psicologo.delete()
        except Exception as e:
            print(f"❌ Erro ao criar psicólogo: {e}")
    else:
        print(f"❌ Formulário inválido: {form.errors}")
    
    # Cenário 3: Psicólogo sem CPF e sem email
    print("\n3. Testando sem CPF e sem email...")
    form_data_sem_email = {
        'nome_completo': 'Carlos Eduardo Pereira',
        'crp': '555666777',
        'uf_crp': 'MG',
        'telefone': '(31) 77777-7777',
    }
    
    form = PsicologoForm(data=form_data_sem_email)
    if form.is_valid():
        try:
            psicologo = form.save()
            print(f"✅ Psicólogo criado com sucesso: {psicologo.nome_completo}")
            print(f"   Username: {psicologo.user.username}")
            print(f"   CRP: {psicologo.crp}")
            # Limpar
            psicologo.user.delete()
            psicologo.delete()
        except Exception as e:
            print(f"❌ Erro ao criar psicólogo: {e}")
    else:
        print(f"❌ Formulário inválido: {form.errors}")
    
    print("\n🎉 Testes concluídos!")

if __name__ == '__main__':
    test_psicologo_creation()
