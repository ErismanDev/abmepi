#!/usr/bin/env python
"""
Script para testar a validação de duplicatas de pacientes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from psicologia.models import Paciente
from associados.models import Associado
from psicologia.forms import PacienteForm
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_paciente_duplicata():
    """Testa se a validação de duplicatas está funcionando"""
    print("Testando validação de duplicatas de pacientes...")
    
    # Verificar se existem associados e psicólogos
    associados = Associado.objects.all()
    if not associados.exists():
        print("❌ Nenhum associado encontrado no sistema")
        return
    
    # Pegar o primeiro associado para teste
    associado_teste = associados.first()
    print(f"Usando associado para teste: {associado_teste.nome}")
    
    # Verificar se já existe um paciente para este associado
    paciente_existente = Paciente.objects.filter(associado=associado_teste).first()
    
    if paciente_existente:
        print(f"✅ Associado já é paciente (ID: {paciente_existente.id})")
        
        # Testar se o formulário rejeita criar outro paciente para o mesmo associado
        data = {
            'associado': associado_teste.id,
            'ativo': True
        }
        
        form = PacienteForm(data=data)
        if not form.is_valid():
            print("✅ Validação funcionando: Formulário rejeitou associado duplicado")
            if 'associado' in form.errors:
                print(f"   Erro: {form.errors['associado']}")
        else:
            print("❌ ERRO: Formulário aceitou associado duplicado!")
    else:
        print("ℹ️  Associado não é paciente ainda")
        
        # Testar se o formulário aceita criar paciente para associado novo
        data = {
            'associado': associado_teste.id,
            'ativo': True
        }
        
        form = PacienteForm(data=data)
        if form.is_valid():
            print("✅ Validação funcionando: Formulário aceitou associado novo")
        else:
            print("❌ ERRO: Formulário rejeitou associado novo!")
            print(f"   Erros: {form.errors}")
    
    # Testar constraint do banco de dados
    print("\nTestando constraint do banco de dados...")
    
    try:
        # Tentar criar um paciente duplicado diretamente no banco
        if paciente_existente:
            print("Tentando criar paciente duplicado...")
            novo_paciente = Paciente(
                associado=associado_teste,
                ativo=True
            )
            novo_paciente.save()
            print("❌ ERRO: Banco de dados permitiu criar paciente duplicado!")
        else:
            print("ℹ️  Não há paciente existente para testar duplicata")
            
    except Exception as e:
        if "UNIQUE constraint failed" in str(e) or "duplicate key value" in str(e):
            print("✅ Constraint do banco funcionando: Impediu paciente duplicado")
        else:
            print(f"❌ Erro inesperado: {e}")
    
    print("\nTeste concluído!")

if __name__ == '__main__':
    test_paciente_duplicata()
