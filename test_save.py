#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig
from core.forms import InstitucionalConfigForm

def test_save():
    print("=== Teste de Salvamento ===")
    
    # Obter configuração atual
    config = InstitucionalConfig.get_config()
    print(f"Config ANTES - ID: {config.id}")
    print(f"Config ANTES - Telefone: {config.telefone}")
    print(f"Config ANTES - Email: {config.email}")
    print(f"Config ANTES - Endereço: {config.endereco}")
    
    # Criar dados para teste
    data = {
        'titulo_principal': config.titulo_principal,
        'subtitulo_hero': config.subtitulo_hero,
        'titulo_sobre': config.titulo_sobre,
        'texto_sobre_1': config.texto_sobre_1,
        'texto_sobre_2': config.texto_sobre_2,
        'texto_sobre_3': config.texto_sobre_3,
        'titulo_cta': config.titulo_cta,
        'texto_cta': config.texto_cta,
        'telefone': '(11) 98765-4321',  # Novo telefone
        'email': config.email,
        'endereco': config.endereco,
        'mostrar_estatisticas': config.mostrar_estatisticas,
        'mostrar_servicos': config.mostrar_servicos,
        'mostrar_sobre': config.mostrar_sobre,
        'mostrar_cta': config.mostrar_cta,
        'meta_description': config.meta_description or '',
        'meta_keywords': config.meta_keywords or '',
    }
    
    # Criar formulário com dados
    form = InstitucionalConfigForm(data=data, instance=config)
    
    print(f"\nFormulário válido? {form.is_valid()}")
    if not form.is_valid():
        print(f"Erros do formulário: {form.errors}")
        return
    
    # Salvar o formulário
    print("Salvando formulário...")
    config_updated = form.save()
    
    # Verificar se foi salvo
    config.refresh_from_db()
    print(f"\nConfig DEPOIS - ID: {config.id}")
    print(f"Config DEPOIS - Telefone: {config.telefone}")
    print(f"Config DEPOIS - Email: {config.email}")
    print(f"Config DEPOIS - Endereço: {config.endereco}")
    
    # Verificar se o telefone foi alterado
    if config.telefone == '(11) 98765-4321':
        print("✅ Telefone foi alterado com sucesso!")
    else:
        print("❌ Telefone NÃO foi alterado!")
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_save()
