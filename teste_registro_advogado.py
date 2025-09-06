#!/usr/bin/env python
"""
Script para testar o registro de um novo advogado
Identifica e corrige possíveis erros no sistema
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.models import Advogado
from assejus.forms import AdvogadoForm

def testar_registro_advogado():
    """Testa o registro de um novo advogado"""
    print("=== TESTE DE REGISTRO DE ADVOGADO ===\n")
    
    # Dados de teste para o advogado
    dados_advogado = {
        'nome': 'Dr. João Silva Santos',
        'cpf': '123.456.789-00',
        'oab': '123456/SP',
        'uf_oab': 'SP',
        'email': 'joao.silva@exemplo.com',
        'telefone': '(11) 3333-4444',
        'celular': '(11) 99999-8888',
        'endereco': 'Rua das Flores, 123 - Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234-567',
        'especialidades': 'Direito Civil, Direito Trabalhista',
        'data_inscricao_oab': date(2015, 6, 15),
        'experiencia_anos': 8,
        'situacao': 'ativo',
        'ativo': True,
        'observacoes': 'Advogado especialista em direito civil e trabalhista'
    }
    
    print("1. Testando validação do formulário...")
    
    # Testar o formulário
    form = AdvogadoForm(data=dados_advogado)
    
    if form.is_valid():
        print("✅ Formulário válido!")
        print("Dados validados com sucesso")
    else:
        print("❌ Formulário inválido!")
        print("Erros encontrados:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
        
        # Tentar corrigir erros comuns
        print("\n2. Tentando corrigir erros...")
        dados_corrigidos = corrigir_dados_advogado(dados_advogado, form.errors)
        
        # Testar novamente
        form_corrigido = AdvogadoForm(data=dados_corrigidos)
        if form_corrigido.is_valid():
            print("✅ Formulário corrigido e válido!")
        else:
            print("❌ Ainda há erros após correção:")
            for field, errors in form_corrigido.errors.items():
                print(f"  - {field}: {errors}")
    
    print("\n3. Testando criação do modelo...")
    
    try:
        # Tentar criar o advogado diretamente no modelo
        advogado = Advogado(**dados_advogado)
        advogado.full_clean()  # Validação do modelo
        print("✅ Modelo válido!")
        
        # Verificar se já existe advogado com mesmo CPF ou OAB
        if Advogado.objects.filter(cpf=dados_advogado['cpf']).exists():
            print("⚠️  Já existe advogado com este CPF")
        
        if Advogado.objects.filter(oab=dados_advogado['oab']).exists():
            print("⚠️  Já existe advogado com esta OAB")
        
    except Exception as e:
        print(f"❌ Erro no modelo: {e}")
    
    print("\n4. Testando salvamento no banco...")
    
    try:
        # Tentar salvar no banco
        if form.is_valid():
            advogado = form.save()
            print(f"✅ Advogado salvo com sucesso! ID: {advogado.id}")
            print(f"   Nome: {advogado.nome}")
            print(f"   OAB: {advogado.oab}")
            
            # Limpar dados de teste
            advogado.delete()
            print("   Dados de teste removidos")
        else:
            print("❌ Não foi possível salvar - formulário inválido")
            
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
    print("\n=== FIM DO TESTE ===")

def corrigir_dados_advogado(dados, erros):
    """Tenta corrigir dados comuns do advogado"""
    dados_corrigidos = dados.copy()
    
    for field, errors in erros.items():
        if field == 'cpf':
            # Remover formatação do CPF
            cpf_limpo = dados['cpf'].replace('.', '').replace('-', '')
            if len(cpf_limpo) == 11:
                dados_corrigidos['cpf'] = cpf_limpo
                print(f"  - CPF corrigido: {dados['cpf']} -> {cpf_limpo}")
        
        elif field == 'cep':
            # Remover formatação do CEP
            cep_limpo = dados['cep'].replace('-', '')
            if len(cep_limpo) == 8:
                dados_corrigidos['cep'] = cep_limpo
                print(f"  - CEP corrigido: {dados['cep']} -> {cep_limpo}")
        
        elif field == 'telefone':
            # Remover formatação do telefone
            tel_limpo = dados['telefone'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            dados_corrigidos['telefone'] = tel_limpo
            print(f"  - Telefone corrigido: {dados['telefone']} -> {tel_limpo}")
        
        elif field == 'celular':
            # Remover formatação do celular
            cel_limpo = dados['celular'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            dados_corrigidos['celular'] = cel_limpo
            print(f"  - Celular corrigido: {dados['celular']} -> {cel_limpo}")
    
    return dados_corrigidos

def verificar_configuracao():
    """Verifica a configuração do Django e modelos"""
    print("=== VERIFICAÇÃO DE CONFIGURAÇÃO ===\n")
    
    try:
        from django.conf import settings
        print(f"✅ Django configurado: {settings.DEBUG}")
        print(f"   Database: {settings.DATABASES['default']['ENGINE']}")
        
        # Verificar se o modelo Advogado está registrado
        from django.apps import apps
        app_config = apps.get_app_config('assejus')
        print(f"✅ App assejus configurado: {app_config.ready}")
        
        # Verificar campos do modelo
        campos = Advogado._meta.fields
        print(f"✅ Modelo Advogado tem {len(campos)} campos")
        
        # Verificar se há migrações pendentes
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', 'assejus', stdout=out)
        migrations_output = out.getvalue()
        
        if '[X]' in migrations_output:
            print("✅ Migrações aplicadas")
        else:
            print("⚠️  Verificar migrações pendentes")
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")

if __name__ == '__main__':
    print("Iniciando teste de registro de advogado...\n")
    
    # Verificar configuração primeiro
    verificar_configuracao()
    
    print("\n" + "="*50 + "\n")
    
    # Executar teste principal
    testar_registro_advogado()
