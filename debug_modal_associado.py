#!/usr/bin/env python3
"""
Script de debug para verificar o funcionamento do modal de associados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from core.models import Usuario
from associados.models import Associado
from associados.forms import AssociadoForm

def test_modal_create():
    """Testa a criação de associado via modal"""
    print("🔍 Testando criação de associado via modal...")
    
    # Criar cliente de teste
    client = Client()
    
    # Criar usuário de teste
    user, created = Usuario.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Usuário de teste criado: {user.username}")
    else:
        print(f"ℹ️ Usuário de teste já existe: {user.username}")
    
    # Fazer login
    login_success = client.login(username='test_user', password='testpass123')
    if login_success:
        print("✅ Login realizado com sucesso")
    else:
        print("❌ Falha no login")
        return
    
    # Testar GET do modal
    print("\n📋 Testando GET do modal...")
    response = client.get('/associados/associados/modal/novo/')
    
    if response.status_code == 200:
        print(f"✅ GET bem-sucedido (Status: {response.status_code})")
        try:
            data = response.json()
            if 'form_html' in data:
                print(f"✅ Form HTML retornado ({len(data['form_html'])} caracteres)")
            else:
                print("⚠️ Form HTML não encontrado na resposta")
                print(f"Dados recebidos: {data}")
        except Exception as e:
            print(f"❌ Erro ao processar JSON: {e}")
            print(f"Resposta: {response.content[:500]}...")
    else:
        print(f"❌ GET falhou (Status: {response.status_code})")
        print(f"Resposta: {response.content[:500]}...")
    
    # Testar POST com dados válidos
    print("\n📤 Testando POST com dados válidos...")
    post_data = {
        'nome': 'João Silva Teste',
        'cpf': '123.456.789-01',
        'rg': '1234567',
        'data_nascimento': '1990-01-01',
        'sexo': 'M',
        'estado_civil': 'solteiro',
        'naturalidade': 'São Paulo',
        'nacionalidade': 'Brasileira',
        'email': 'joao.teste@example.com',
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
        'nome_civil': 'João Silva Teste',
        'ativo': 'on',
        'observacoes': 'Associado de teste'
    }
    
    response = client.post('/associados/associados/modal/novo/', post_data)
    
    if response.status_code == 200:
        print(f"✅ POST bem-sucedido (Status: {response.status_code})")
        try:
            data = response.json()
            if data.get('success'):
                print("✅ Associado criado com sucesso!")
                print(f"Mensagem: {data.get('message')}")
                print(f"ID: {data.get('associado_id')}")
                
                # Verificar se o associado foi realmente criado
                associado = Associado.objects.get(id=data.get('associado_id'))
                print(f"✅ Associado encontrado no banco: {associado.nome}")
                
            else:
                print("❌ Falha na criação do associado")
                print(f"Mensagem: {data.get('message')}")
                if 'errors' in data:
                    print(f"Erros: {data['errors']}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar resposta JSON: {e}")
            print(f"Resposta: {response.content[:500]}...")
    else:
        print(f"❌ POST falhou (Status: {response.status_code})")
        print(f"Resposta: {response.content[:500]}...")
    
    # Testar validação do formulário
    print("\n🔍 Testando validação do formulário...")
    form = AssociadoForm(data=post_data)
    if form.is_valid():
        print("✅ Formulário é válido")
        print(f"✅ Dados limpos: {form.cleaned_data}")
    else:
        print("❌ Formulário inválido")
        print(f"❌ Erros: {form.errors}")
    
    # Limpar dados de teste
    print("\n🧹 Limpando dados de teste...")
    Associado.objects.filter(nome__contains='Teste').delete()
    print("✅ Dados de teste removidos")
    
    # Remover usuário de teste
    user.delete()
    print("✅ Usuário de teste removido")

def test_form_validation():
    """Testa a validação do formulário"""
    print("\n🔍 Testando validação do formulário...")
    
    # Dados válidos
    valid_data = {
        'nome': 'João Silva',
        'cpf': '12345678901',
        'rg': '1234567',
        'data_nascimento': '1990-01-01',
        'sexo': 'M',
        'estado_civil': 'solteiro',
        'naturalidade': 'São Paulo',
        'nacionalidade': 'Brasileira',
        'email': 'joao@example.com',
        'telefone': '11999999999',
        'celular': '11999999999',
        'cep': '01234-567',
        'rua': 'Rua Teste',
        'numero': '123',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'tipo_socio': 'efetivo',
        'tipo_profissional': 'bombeiro',
        'matricula_militar': '12345',
        'posto_graduacao': 'soldado',
        'unidade_lotacao': '1º Batalhão',
        'data_ingresso': '2020-01-01',
        'situacao': 'ativo',
        'nome_civil': 'João Silva',
        'ativo': True,
        'observacoes': 'Teste'
    }
    
    form = AssociadoForm(data=valid_data)
    if form.is_valid():
        print("✅ Formulário válido com dados completos")
    else:
        print("❌ Formulário inválido com dados completos")
        print(f"Erros: {form.errors}")
    
    # Dados inválidos (sem nome)
    invalid_data = valid_data.copy()
    del invalid_data['nome']
    
    form = AssociadoForm(data=invalid_data)
    if not form.is_valid():
        print("✅ Formulário corretamente inválido sem nome")
        if 'nome' in form.errors:
            print("✅ Erro de nome detectado corretamente")
    else:
        print("❌ Formulário deveria ser inválido sem nome")

if __name__ == '__main__':
    print("🚀 Iniciando testes de debug do modal de associados...")
    
    try:
        test_modal_create()
        test_form_validation()
        print("\n✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
