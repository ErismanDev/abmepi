#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import InstitucionalConfig

def test_assejur_social():
    """Testa se as redes sociais da ASSEJUR estão configuradas"""
    try:
        config = InstitucionalConfig.get_config()
        
        print("=== REDES SOCIAIS ASSEJUR ===")
        print(f"ID da configuração: {config.id}")
        
        # Verificar cada rede social
        redes_sociais = [
            ('Facebook', config.assejur_facebook_url),
            ('Instagram', config.assejur_instagram_url),
            ('LinkedIn', config.assejur_linkedin_url),
            ('YouTube', config.assejur_youtube_url),
            ('Twitter', config.assejur_twitter_url),
        ]
        
        total_configuradas = 0
        for nome, url in redes_sociais:
            if url:
                print(f"✓ {nome}: {url}")
                total_configuradas += 1
            else:
                print(f"✗ {nome}: Não configurado")
        
        print(f"\n=== RESUMO ===")
        print(f"Total de redes configuradas: {total_configuradas}/5")
        
        if total_configuradas == 0:
            print("⚠️  Nenhuma rede social configurada!")
            print("   Acesse: http://127.0.0.1:8000/core/institucional/editar/")
            print("   E configure as redes sociais da ASSEJUR na seção correspondente.")
        elif total_configuradas < 3:
            print("⚠️  Poucas redes sociais configuradas.")
        else:
            print("✅ Boa quantidade de redes sociais configuradas!")
            
        # Verificar se o context processor está funcionando
        print(f"\n=== TESTE DO CONTEXT PROCESSOR ===")
        try:
            from core.context_processors import institucional_config
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get('/')
            
            context = institucional_config(request)
            print(f"Context processor retornou: {context}")
            
            if 'institucional_config' in context:
                config_processor = context['institucional_config']
                print(f"✓ Context processor funcionando")
                print(f"  Config ID: {config_processor.id}")
                
                # Verificar se as redes sociais estão disponíveis
                if hasattr(config_processor, 'assejur_facebook_url'):
                    print(f"  Facebook disponível: {config_processor.assejur_facebook_url}")
                else:
                    print(f"  ✗ Campo assejur_facebook_url não encontrado")
            else:
                print(f"✗ Context processor não retornou institucional_config")
                
        except Exception as e:
            print(f"✗ Erro no context processor: {e}")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_assejur_social()
