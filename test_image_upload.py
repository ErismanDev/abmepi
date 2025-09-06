#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

def test_image_upload():
    """Testa o upload de uma imagem real"""
    try:
        config = InstitucionalConfig.get_config()
        
        print("=== TESTE DE UPLOAD DE IMAGEM ===")
        print(f"Configuração atual: {config}")
        print(f"Imagem atual: {config.hotel_transito_imagem}")
        
        # Criar uma imagem de teste simples (1x1 pixel PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\xa7\xd4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Criar arquivo temporário
        with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(png_data)
            temp_file.flush()
            
            print(f"Arquivo temporário criado: {temp_file.name}")
            print(f"Tamanho do arquivo: {len(png_data)} bytes")
            
            # Abrir o arquivo e salvar no modelo
            with open(temp_file.name, 'rb') as f:
                # Limpar imagem anterior se existir
                if config.hotel_transito_imagem:
                    print(f"Removendo imagem anterior: {config.hotel_transito_imagem.name}")
                    config.hotel_transito_imagem.delete(save=False)
                
                # Salvar nova imagem
                config.hotel_transito_imagem.save('test_hotel_real.png', File(f), save=True)
                
                print(f"Imagem salva: {config.hotel_transito_imagem.name}")
                print(f"URL: {config.hotel_transito_imagem.url}")
                print(f"Path: {config.hotel_transito_imagem.path}")
                
                # Verificar se o arquivo foi salvo
                if os.path.exists(config.hotel_transito_imagem.path):
                    file_size = os.path.getsize(config.hotel_transito_imagem.path)
                    print(f"✓ Arquivo salvo com sucesso! Tamanho: {file_size} bytes")
                    
                    # Verificar se é uma imagem válida
                    if file_size > 100:  # PNG válido deve ter pelo menos 100 bytes
                        print("✓ Arquivo parece ser uma imagem válida")
                    else:
                        print("⚠️  Arquivo muito pequeno, pode não ser uma imagem válida")
                else:
                    print("✗ Arquivo não foi salvo corretamente")
            
            # Limpar arquivo temporário
            os.unlink(temp_file.name)
            print("Arquivo temporário removido")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_image_upload()
