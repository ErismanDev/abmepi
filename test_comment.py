#!/usr/bin/env python
"""
Teste para verificar se a view de comentários está funcionando
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from core.views import post_comment_ajax
from core.models import FeedPost, Usuario
from django.contrib.auth import get_user_model

def test_comment_view():
    """Testa a view de comentários"""
    print("=== Teste da View de Comentários ===")
    
    # Criar uma instância de request factory
    factory = RequestFactory()
    
    # Verificar se existe algum post para testar
    try:
        post = FeedPost.objects.first()
        if not post:
            print("❌ Nenhum post encontrado no banco de dados")
            return
        
        print(f"✅ Post encontrado: {post.titulo} (ID: {post.id})")
        
        # Teste 1: Método GET (deve retornar erro)
        print("\n--- Teste 1: Método GET ---")
        request = factory.get(f'/posts/{post.id}/comment/')
        request.user = AnonymousUser()
        response = post_comment_ajax(request, post.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 2: Método POST sem dados (deve retornar erro)
        print("\n--- Teste 2: Método POST sem dados ---")
        request = factory.post(f'/posts/{post.id}/comment/')
        request.user = AnonymousUser()
        response = post_comment_ajax(request, post.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 3: Método POST com dados válidos
        print("\n--- Teste 3: Método POST com dados válidos ---")
        post_data = {
            'conteudo': 'Teste de comentário',
            'nome_usuario': 'Usuário Teste'
        }
        request = factory.post(f'/posts/{post.id}/comment/', post_data)
        request.user = AnonymousUser()
        response = post_comment_ajax(request, post.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 4: Verificar se o comentário foi criado
        print("\n--- Teste 4: Verificar comentário criado ---")
        from core.models import Comentario
        comentarios = Comentario.objects.filter(post=post).order_by('-data_criacao')
        if comentarios.exists():
            ultimo = comentarios.first()
            print(f"✅ Comentário criado: {ultimo.conteudo}")
            print(f"   Autor: {ultimo.get_author_name()}")
            print(f"   Data: {ultimo.data_criacao}")
        else:
            print("❌ Nenhum comentário encontrado")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_comment_view()
