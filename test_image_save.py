#!/usr/bin/env python
"""
Script para testar se a imagem está sendo salva corretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig
from django.core.files.uploadedfile import SimpleUploadedFile

def test_image_save():
    """Testa se a imagem está sendo salva corretamente"""
    try:
        # Obter configuração atual
        config = InstitucionalConfig.get_config()
        
        print("=== TESTE DE SALVAMENTO DA IMAGEM ===")
        print(f"Config ID: {config.id}")
        print(f"Hotel imagem atual: {config.hotel_transito_imagem}")
        
        # Verificar se já existe uma imagem
        if config.hotel_transito_imagem:
            print(f"Imagem existente: {config.hotel_transito_imagem.name}")
            print(f"URL: {config.hotel_transito_imagem.url}")
            
            # Verificar se o arquivo físico existe
            if hasattr(config.hotel_transito_imagem, 'path'):
                file_path = config.hotel_transito_imagem.path
                print(f"Caminho físico: {file_path}")
                
                if os.path.exists(file_path):
                    print("✅ Arquivo físico existe")
                    print(f"Tamanho: {os.path.getsize(file_path)} bytes")
                else:
                    print("❌ Arquivo físico NÃO existe")
        
        # Criar uma nova imagem de teste
        print(f"\n=== CRIANDO NOVA IMAGEM DE TESTE ===")
        test_image_content = b'fake-image-content-for-testing'
        test_image = SimpleUploadedFile(
            name='hotel_test_new.jpg',
            content=test_image_content,
            content_type='image/jpeg'
        )
        
        # Salvar a nova imagem
        print("Salvando nova imagem...")
        config.hotel_transito_imagem = test_image
        config.save()
        
        print(f"Imagem após salvar: {config.hotel_transito_imagem}")
        
        # Verificar se foi salvo no banco
        print(f"\n=== VERIFICANDO SALVAMENTO ===")
        config_refresh = InstitucionalConfig.objects.get(pk=config.id)
        print(f"Imagem no banco: {config_refresh.hotel_transito_imagem}")
        
        if config_refresh.hotel_transito_imagem:
            print(f"Nome do arquivo: {config_refresh.hotel_transito_imagem.name}")
            print(f"URL: {config_refresh.hotel_transito_imagem.url}")
            
            # Verificar se o arquivo físico foi criado
            if hasattr(config_refresh.hotel_transito_imagem, 'path'):
                new_file_path = config_refresh.hotel_transito_imagem.path
                print(f"Novo caminho físico: {new_file_path}")
                
                if os.path.exists(new_file_path):
                    print("✅ Novo arquivo físico criado")
                    print(f"Tamanho: {os.path.getsize(new_file_path)} bytes")
                else:
                    print("❌ Novo arquivo físico NÃO foi criado")
        else:
            print("❌ Imagem não foi salva no banco")
            
        # Verificar pasta media
        print(f"\n=== VERIFICAÇÃO DA PASTA MEDIA ===")
        media_root = os.path.join(os.getcwd(), 'media')
        print(f"Pasta media: {media_root}")
        
        if os.path.exists(media_root):
            print("✅ Pasta media existe")
            
            # Verificar pasta hotel_transito
            hotel_folder = os.path.join(media_root, 'hotel_transito')
            if os.path.exists(hotel_folder):
                print("✅ Pasta hotel_transito existe")
                files = os.listdir(hotel_folder)
                print(f"Arquivos na pasta: {files}")
            else:
                print("❌ Pasta hotel_transito NÃO existe")
        else:
            print("❌ Pasta media NÃO existe")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_image_save()
