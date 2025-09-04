#!/usr/bin/env python
"""
Script de teste rápido para registro de advogados
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

def teste_rapido():
    """Teste rápido de registro de advogado"""
    print("=== TESTE RÁPIDO DE REGISTRO DE ADVOGADO ===\n")
    
    # Dados de teste
    dados = {
        'nome': 'Dr. Carlos Eduardo Silva',
        'cpf': '338.886.473-04',
        'oab': '789456/SP',
        'uf_oab': 'SP',
        'email': 'carlos.silva@exemplo.com',
        'telefone': '(11) 4444-5555',
        'celular': '(11) 97777-6666',
        'endereco': 'Rua das Palmeiras, 789 - Jardim',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '04567-890',
        'especialidades': 'Direito Civil, Direito do Consumidor',
        'data_inscricao_oab': date(2020, 8, 10),
        'experiencia_anos': 3,
        'situacao': 'ativo',
        'ativo': True,
        'observacoes': 'Advogado especialista em direito civil e do consumidor'
    }
    
    print("1. Testando formulário...")
    form = AdvogadoForm(data=dados)
    
    if form.is_valid():
        print("✅ Formulário válido!")
        
        print("\n2. Salvando advogado...")
        try:
            advogado = form.save()
            print(f"✅ Advogado salvo com sucesso!")
            print(f"   ID: {advogado.id}")
            print(f"   Nome: {advogado.nome}")
            print(f"   OAB: {advogado.oab}")
            print(f"   CPF: {advogado.cpf}")
            
            print("\n3. Limpando dados de teste...")
            advogado.delete()
            print("✅ Dados de teste removidos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    else:
        print("❌ Formulário inválido!")
        print("Erros:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    teste_rapido()
