#!/usr/bin/env python
"""
Teste para verificar se os botões do feed estão funcionando
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from core.models import FeedPost

def test_feed_buttons():
    """Testa se os botões do feed estão funcionando"""
    print("=== Teste dos Botões do Feed ===\n")
    
    try:
        # Configurar cliente
        client = Client()
        
        # 1. Verificar se há posts
        posts = FeedPost.objects.filter(ativo=True)
        print(f"📊 Posts ativos encontrados: {posts.count()}")
        
        if not posts.exists():
            print("❌ Nenhum post ativo encontrado")
            return
        
        post = posts.first()
        print(f"📝 Testando com post: {post.titulo}")
        
        # 2. Testar página principal
        print(f"\n--- Teste da Página Principal ---")
        response = client.get('/', HTTP_HOST='127.0.0.1')
        print(f"📄 Status da página: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Verificar se os botões estão presentes
            if 'like-btn' in content:
                print("✅ Botões de like encontrados")
            else:
                print("❌ Botões de like não encontrados")
                
            if 'comment-btn' in content:
                print("✅ Botões de comentário encontrados")
            else:
                print("❌ Botões de comentário não encontrados")
                
            if 'share-btn' in content:
                print("✅ Botões de compartilhamento encontrados")
            else:
                print("❌ Botões de compartilhamento não encontrados")
                
            if 'save-btn' in content:
                print("✅ Botões de salvar encontrados")
            else:
                print("❌ Botões de salvar não encontrados")
            
            # Verificar se o JavaScript está presente
            if 'initializeFeedButtons' in content:
                print("✅ JavaScript dos botões encontrado")
            else:
                print("❌ JavaScript dos botões não encontrado")
                
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
        
        # 3. Testar API de like
        print(f"\n--- Teste da API de Like ---")
        response = client.post(f'/core/posts/{post.id}/like/', HTTP_HOST='127.0.0.1')
        print(f"📄 Status da API: {response.status_code}")
        
        if response.status_code == 200:
            import json
            try:
                data = json.loads(response.content.decode())
                print(f"✅ Resposta da API: {data}")
            except:
                print(f"📄 Conteúdo da resposta: {response.content.decode()}")
        else:
            print(f"❌ Erro na API: {response.status_code}")
        
        print(f"\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_feed_buttons()
