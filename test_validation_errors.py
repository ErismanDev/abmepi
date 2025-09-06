#!/usr/bin/env python3
"""
Script para testar erros de validação específicos do formulário de associados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from associados.forms import AssociadoForm

def test_validation_errors():
    """Testa erros de validação específicos"""
    print("🔍 Testando erros de validação do formulário de associados...")
    
    # Dados que causaram erro (baseado nos logs)
    test_data = {
        'nome': 'FLAUBERT ROCHA VIEIRA',
        'cpf': '037.476.123-00',
        'rg': '2293913',
        'data_nascimento': '19971-05-01',  # Ano inválido
        'sexo': 'M',
        'estado_civil': 'solteiro',
        'naturalidade': 'São Paulo',
        'nacionalidade': 'Brasileira',
        'email': 'teste@example.com',
        'telefone': '(11) 9999-9999',
        'celular': '(11) 9999-9999',
        'cep': '01234-567',
        'rua': 'Rua Teste',
        'numero': '123',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'tipo_socio': 'contribuinte',
        'tipo_profissional': 'bombeiro_militar',
        'matricula_militar': 'TESTE12345',
        'posto_graduacao': 'soldado_bm',
        'unidade_lotacao': '1º Batalhão',
        'data_ingresso': '2020-01-01',
        'situacao': 'ativo',
        'nome_civil': 'FLAUBERT ROCHA VIEIRA',
        'ativo': 'on',
        'observacoes': 'Teste de validação'
    }
    
    print("\n📋 Dados de teste:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Testar validação
    print("\n🔍 Testando validação...")
    form = AssociadoForm(data=test_data)
    
    if form.is_valid():
        print("✅ Formulário é válido!")
        print("📋 Dados limpos:")
        for key, value in form.cleaned_data.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Formulário inválido!")
        print("❌ Erros de validação:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    
    # Testar com data corrigida
    print("\n🔍 Testando com data corrigida...")
    test_data_corrected = test_data.copy()
    test_data_corrected['data_nascimento'] = '1997-05-01'  # Ano corrigido
    
    form_corrected = AssociadoForm(data=test_data_corrected)
    
    if form_corrected.is_valid():
        print("✅ Formulário corrigido é válido!")
    else:
        print("❌ Formulário corrigido ainda inválido!")
        for field, errors in form_corrected.errors.items():
            print(f"  {field}: {errors}")
    
    # Testar validação de CPF
    print("\n🔍 Testando validação de CPF...")
    cpf_test_data = test_data_corrected.copy()
    
    # CPF válido
    cpf_test_data['cpf'] = '111.444.777-35'
    form_cpf_valid = AssociadoForm(data=cpf_test_data)
    print(f"CPF válido (111.444.777-35): {'✅' if form_cpf_valid.is_valid() else '❌'}")
    
    # CPF inválido
    cpf_test_data['cpf'] = '123.456.789-00'
    form_cpf_invalid = AssociadoForm(data=cpf_test_data)
    print(f"CPF inválido (123.456.789-00): {'✅' if form_cpf_invalid.is_valid() else '❌'}")
    if not form_cpf_invalid.is_valid():
        print(f"  Erro: {form_cpf_invalid.errors.get('cpf', [])}")
    
    # Testar validação de telefone
    print("\n🔍 Testando validação de telefone...")
    phone_test_data = test_data_corrected.copy()
    
    # Telefone válido
    phone_test_data['telefone'] = '(11) 9999-9999'
    form_phone_valid = AssociadoForm(data=phone_test_data)
    print(f"Telefone válido ((11) 9999-9999): {'✅' if form_phone_valid.is_valid() else '❌'}")
    
    # Telefone inválido
    phone_test_data['telefone'] = '11999999999'
    form_phone_invalid = AssociadoForm(data=phone_test_data)
    print(f"Telefone inválido (11999999999): {'✅' if form_phone_invalid.is_valid() else '❌'}")
    if not form_phone_invalid.is_valid():
        print(f"  Erro: {form_phone_invalid.errors.get('telefone', [])}")

if __name__ == '__main__':
    print("🚀 Iniciando testes de validação...")
    
    try:
        test_validation_errors()
        print("\n✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
