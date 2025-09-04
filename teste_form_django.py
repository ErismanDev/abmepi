#!/usr/bin/env python
"""
Script para testar o formulário Django AdvogadoForm diretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.forms import AdvogadoForm

def test_form():
    """Testa o formulário AdvogadoForm"""
    print("🧪 Testando AdvogadoForm...")
    
    # Criar instância do formulário
    form = AdvogadoForm()
    
    print(f"\n✅ Formulário criado com sucesso")
    print(f"📋 Campos disponíveis: {list(form.fields.keys())}")
    
    # Verificar campos específicos
    campos_importantes = ['uf_oab', 'estado', 'situacao']
    
    for campo in campos_importantes:
        if campo in form.fields:
            field = form.fields[campo]
            print(f"\n🔍 Campo: {campo}")
            print(f"   - Tipo: {type(field)}")
            print(f"   - Widget: {type(field.widget)}")
            print(f"   - Choices: {field.choices}")
            print(f"   - Required: {field.required}")
            print(f"   - Disabled: {field.disabled}")
            
            # Verificar se tem choices
            if hasattr(field, 'choices') and field.choices:
                print(f"   - Número de choices: {len(field.choices)}")
                print(f"   - Primeiras choices: {field.choices[:3]}")
            else:
                print(f"   - ⚠️ SEM CHOICES!")
        else:
            print(f"\n❌ Campo {campo} não encontrado!")
    
    # Verificar se o formulário pode ser renderizado
    print(f"\n🖼️ Testando renderização...")
    try:
        html = form.as_p()
        print(f"✅ Formulário renderizado com sucesso")
        print(f"📏 Tamanho do HTML: {len(html)} caracteres")
        
        # Verificar se contém as choices
        if 'Acre' in html:
            print("✅ Choice 'Acre' encontrada no HTML")
        else:
            print("❌ Choice 'Acre' NÃO encontrada no HTML")
            
        if 'São Paulo' in html:
            print("✅ Choice 'São Paulo' encontrada no HTML")
        else:
            print("❌ Choice 'São Paulo' NÃO encontrada no HTML")
            
    except Exception as e:
        print(f"❌ Erro ao renderizar: {e}")
    
    # Verificar se há problemas com as choices
    print(f"\n🔍 Verificando choices das UFs...")
    uf_choices = form.fields['uf_oab'].choices
    if uf_choices:
        print(f"✅ UF choices encontradas: {len(uf_choices)}")
        for value, label in uf_choices[:5]:  # Primeiras 5
            print(f"   - {value}: {label}")
    else:
        print("❌ UF choices vazias!")
    
    # Verificar se há problemas com as choices de situação
    print(f"\n🔍 Verificando choices de situação...")
    situacao_choices = form.fields['situacao'].choices
    if situacao_choices:
        print(f"✅ Situação choices encontradas: {len(situacao_choices)}")
        for value, label in situacao_choices:
            print(f"   - {value}: {label}")
    else:
        print("❌ Situação choices vazias!")

if __name__ == '__main__':
    test_form()
