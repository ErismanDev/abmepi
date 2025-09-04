#!/usr/bin/env python
"""
Teste para verificar se os comentários das notícias ASSEJUR estão funcionando
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from core.views import assejur_news_comment_ajax, assejur_news_comments_list_ajax
from core.models import AssejurNews

def test_assejur_comments():
    """Testa as views de comentários das notícias ASSEJUR"""
    print("=== Teste dos Comentários ASSEJUR ===")
    
    # Criar uma instância de request factory
    factory = RequestFactory()
    
    # Verificar se existe alguma notícia para testar
    try:
        noticia = AssejurNews.objects.filter(ativo=True).first()
        if not noticia:
            print("❌ Nenhuma notícia ativa encontrada no banco de dados")
            return
        
        print(f"✅ Notícia encontrada: {noticia.titulo} (ID: {noticia.id})")
        
        # Teste 1: Método GET (deve retornar erro)
        print("\n--- Teste 1: Método GET ---")
        request = factory.get(f'/assejur/noticias/{noticia.id}/comment/')
        request.user = AnonymousUser()
        response = assejur_news_comment_ajax(request, noticia.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 2: Método POST sem dados (deve retornar erro)
        print("\n--- Teste 2: Método POST sem dados ---")
        request = factory.post(f'/assejur/noticias/{noticia.id}/comment/')
        request.user = AnonymousUser()
        response = assejur_news_comment_ajax(request, noticia.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 3: Método POST com dados válidos
        print("\n--- Teste 3: Método POST com dados válidos ---")
        post_data = {
            'conteudo': 'Teste de comentário ASSEJUR',
            'nome_anonimo': 'Usuário Teste ASSEJUR'
        }
        request = factory.post(f'/assejur/noticias/{noticia.id}/comment/', post_data)
        request.user = AnonymousUser()
        response = assejur_news_comment_ajax(request, noticia.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 4: Listar comentários
        print("\n--- Teste 4: Listar comentários ---")
        request = factory.get(f'/assejur/noticias/{noticia.id}/comments/')
        request.user = AnonymousUser()
        response = assejur_news_comments_list_ajax(request, noticia.id)
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")
        
        # Teste 5: Verificar se o comentário foi criado
        print("\n--- Teste 5: Verificar comentário criado ---")
        from core.models import AssejurNewsComentario
        comentarios = AssejurNewsComentario.objects.filter(noticia=noticia).order_by('-data_criacao')
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
    test_assejur_comments()
