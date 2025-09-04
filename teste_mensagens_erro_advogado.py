#!/usr/bin/env python
"""
Script para testar as mensagens de erro do formulário de advogados
Verifica se as mensagens seguem o mesmo padrão do sistema de associados
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.forms import AdvogadoForm
from assejus.models import Advogado

def testar_mensagens_erro():
    """Testa as mensagens de erro do formulário de advogados"""
    print("=== TESTE DAS MENSAGENS DE ERRO DO FORMULÁRIO DE ADVOGADOS ===\n")
    
    # Teste 1: Formulário vazio
    print("1. Testando formulário vazio...")
    form = AdvogadoForm({})
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 2: CPF inválido
    print("2. Testando CPF inválido...")
    dados_cpf_invalido = {
        'nome': 'Dr. Teste Silva',
        'cpf': '123.456.789-00',  # CPF inválido
        'oab': '123456',
        'uf_oab': 'SP',
        'email': 'teste@exemplo.com',
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua Teste, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_cpf_invalido)
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 3: OAB inválida
    print("3. Testando OAB inválida...")
    dados_oab_invalida = {
        'nome': 'Dr. Teste Silva',
        'cpf': '338.886.473-04',  # CPF válido
        'oab': '12',  # OAB muito curta
        'uf_oab': 'SP',
        'email': 'teste@exemplo.com',
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua Teste, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_oab_invalida)
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 4: Email inválido
    print("4. Testando email inválido...")
    dados_email_invalido = {
        'nome': 'Dr. Teste Silva',
        'cpf': '338.886.473-04',
        'oab': '123456/SP',
        'uf_oab': 'SP',
        'email': 'email_invalido',  # Email sem @
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua Teste, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_email_invalido)
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 5: Endereço muito curto
    print("5. Testando endereço muito curto...")
    dados_endereco_curto = {
        'nome': 'Dr. Teste Silva',
        'cpf': '338.886.473-04',
        'oab': '123456/SP',
        'uf_oab': 'SP',
        'email': 'teste@exemplo.com',
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua A',  # Endereço muito curto
        'cidade': 'São Paulo',
        'estado': 'SP',
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_endereco_curto)
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 6: CEP inválido
    print("6. Testando CEP inválido...")
    dados_cep_invalido = {
        'nome': 'Dr. Teste Silva',
        'cpf': '338.886.473-04',
        'oab': '123456/SP',
        'uf_oab': 'SP',
        'email': 'teste@exemplo.com',
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua Teste, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '123',  # CEP muito curto
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_cep_invalido)
    if not form.is_valid():
        print("✅ Formulário inválido (esperado)")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    else:
        print("❌ Formulário deveria ser inválido")
    
    print()
    
    # Teste 7: Formulário válido
    print("7. Testando formulário válido...")
    dados_validos = {
        'nome': 'Dr. Teste Silva',
        'cpf': '338.886.473-04',
        'oab': '123456/SP',
        'uf_oab': 'SP',
        'email': 'teste@exemplo.com',
        'telefone': '(11) 3333-4444',
        'endereco': 'Rua Teste, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234-567',
        'situacao': 'ativo'
    }
    
    form = AdvogadoForm(dados_validos)
    if form.is_valid():
        print("✅ Formulário válido (esperado)")
        print("   Dados limpos:", form.cleaned_data)
    else:
        print("❌ Formulário deveria ser válido")
        for field, errors in form.errors.items():
            print(f"   Campo '{field}': {errors}")
    
    print("\n=== FIM DOS TESTES ===")

if __name__ == '__main__':
    testar_mensagens_erro()
