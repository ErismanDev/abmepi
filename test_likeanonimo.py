#!/usr/bin/env python
"""
Teste simples para verificar se o modelo LikeAnonimo está funcionando
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import FeedPost, LikeAnonimo

def test_likeanonimo():
    """Testa se o modelo LikeAnonimo está funcionando"""
    print("=== Teste do Modelo LikeAnonimo ===\n")
    
    try:
        # Verificar se há posts
        posts = FeedPost.objects.filter(ativo=True)
        print(f"📊 Posts ativos encontrados: {posts.count()}")
        
        if not posts.exists():
            print("❌ Nenhum post ativo encontrado")
            return
        
        post = posts.first()
        print(f"📝 Testando com post: {post.titulo}")
        
        # Testar contagem de likes
        print(f"\n--- Contagem de Likes ---")
        likes_count = post.get_likes_count()
        print(f"💖 Total de likes: {likes_count}")
        
        # Testar sincronização
        print(f"\n--- Sincronização ---")
        counters = post.sync_counters()
        print(f"✅ Contadores sincronizados:")
        print(f"   💖 Likes: {counters['likes']}")
        print(f"   💬 Comentários: {counters['comentarios']}")
        
        print(f"\n🎉 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_likeanonimo()
