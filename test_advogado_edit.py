#!/usr/bin/env python
"""
Script para testar o carregamento de dados do advogado na edição
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.models import Advogado
from assejus.forms import AdvogadoForm

def test_advogado_edit():
    """Testa o carregamento de dados do advogado na edição"""
    print("=== TESTE DE CARREGAMENTO DE DADOS DO ADVOGADO ===")
    
    # Busca um advogado existente
    try:
        advogado = Advogado.objects.first()
        if not advogado:
            print("❌ Nenhum advogado encontrado no banco de dados")
            return
        
        print(f"✅ Advogado encontrado: {advogado.nome}")
        print(f"   ID: {advogado.pk}")
        print(f"   OAB: {advogado.oab}")
        print(f"   UF OAB: {advogado.uf_oab}")
        print(f"   Estado: {advogado.estado}")
        print(f"   Data inscrição OAB: {advogado.data_inscricao_oab}")
        print(f"   CPF: {advogado.cpf}")
        print(f"   Email: {advogado.email}")
        print(f"   Telefone: {advogado.telefone}")
        print(f"   Celular: {advogado.celular}")
        print(f"   Endereço: {advogado.endereco}")
        print(f"   Cidade: {advogado.cidade}")
        print(f"   CEP: {advogado.cep}")
        print(f"   Especialidades: {advogado.especialidades}")
        print(f"   Experiência anos: {advogado.experiencia_anos}")
        print(f"   Ativo: {advogado.ativo}")
        print(f"   Observações: {advogado.observacoes}")
        
        print("\n=== TESTE DO FORMULÁRIO ===")
        
        # Cria o formulário com a instância do advogado
        form = AdvogadoForm(instance=advogado)
        
        print(f"✅ Formulário criado com sucesso")
        print(f"   Campos disponíveis: {list(form.fields.keys())}")
        
        # Verifica os campos específicos
        print(f"\n   Campo UF OAB:")
        print(f"     Choices: {form.fields['uf_oab'].choices}")
        print(f"     Valor inicial: {form.initial.get('uf_oab')}")
        print(f"     Valor atual: {form['uf_oab'].value()}")
        
        print(f"\n   Campo Estado:")
        print(f"     Choices: {form.fields['estado'].choices}")
        print(f"     Valor inicial: {form.initial.get('estado')}")
        print(f"     Valor atual: {form['estado'].value()}")
        
        print(f"\n   Campo Data Inscrição OAB:")
        print(f"     Valor inicial: {form.initial.get('data_inscricao_oab')}")
        print(f"     Valor atual: {form['data_inscricao_oab'].value()}")
        print(f"     Widget: {form.fields['data_inscricao_oab'].widget}")
        
        # Verifica se todos os campos estão sendo preenchidos
        print(f"\n=== VERIFICAÇÃO DOS CAMPOS ===")
        
        for field_name in form.fields:
            field = form[field_name]
            value = field.value()
            print(f"   {field_name}: {value}")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_advogado_edit()
