#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig

def test_template_context():
    """Testa o contexto do template institucional"""
    try:
        # Obter a configuração diretamente
        config = InstitucionalConfig.get_config()
        
        print("=== CONFIGURAÇÃO INSTITUCIONAL ===")
        print(f"ID: {config.id}")
        print(f"Telefone: {config.hotel_transito_telefone}")
        print(f"Imagem: {config.hotel_transito_imagem}")
        
        if config.hotel_transito_imagem:
            print(f"Nome: {config.hotel_transito_imagem.name}")
            print(f"URL: {config.hotel_transito_imagem.url}")
            print(f"Path: {config.hotel_transito_imagem.path if hasattr(config.hotel_transito_imagem, 'path') else 'N/A'}")
            
            # Verificar se o arquivo existe
            if hasattr(config.hotel_transito_imagem, 'path'):
                import os
                exists = os.path.exists(config.hotel_transito_imagem.path)
                print(f"Arquivo existe: {exists}")
        else:
            print("Nenhuma imagem configurada")
            
        # Verificar se o campo existe
        if hasattr(config, 'hotel_transito_imagem'):
            print("✓ Campo hotel_transito_imagem existe no objeto")
        else:
            print("✗ Campo hotel_transito_imagem NÃO existe no objeto")
            
        # Verificar todos os campos do modelo
        print(f"\n=== CAMPOS DO MODELO ===")
        model_fields = [field.name for field in InstitucionalConfig._meta.get_fields()]
        for field in sorted(model_fields):
            if 'hotel' in field.lower():
                print(f"* {field}: {getattr(config, field, 'N/A')}")
                
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_template_context()
