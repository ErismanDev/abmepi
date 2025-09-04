#!/usr/bin/env python
"""
Teste simples para verificar se a correção dos comentários funcionou
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from core.views import assejur_news_comment_ajax
from core.models import AssejurNews

def test_simple_comment():
    """Teste simples para verificar a correção"""
    print("=== Teste Simples da Correção ===")
    
    factory = RequestFactory()
    
    try:
        noticia = AssejurNews.objects.filter(ativo=True).first()
        if not noticia:
            print("❌ Nenhuma notícia encontrada")
            return
        
        print(f"✅ Notícia: {noticia.titulo}")
        
        # Teste de criação de comentário
        post_data = {
            'conteudo': 'Teste da correção',
            'nome_anonimo': 'Usuário Teste'
        }
        request = factory.post(f'/assejur/noticias/{noticia.id}/comment/', post_data)
        request.user = AnonymousUser()
        
        response = assejur_news_comment_ajax(request, noticia.id)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content.decode())
            print(f"✅ Sucesso: {data.get('success')}")
            print(f"📝 Mensagem: {data.get('message')}")
            
            if data.get('success'):
                comentario = data.get('comentario', {})
                print(f"🆔 ID: {comentario.get('id')}")
                print(f"👤 Autor: {comentario.get('author_name')}")
                print(f"📄 Conteúdo: {comentario.get('content')}")
                print(f"⏰ Tempo: {comentario.get('time_ago')}")
                print(f"🔐 Autenticado: {comentario.get('is_authenticated')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_comment()
