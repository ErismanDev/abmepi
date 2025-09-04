#!/usr/bin/env python
"""
Script de debug para verificar problemas na edição dos posts do feed
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import FeedPost
from core.forms import FeedPostForm

def debug_feed_post_edit():
    """Debug da edição de posts do feed"""
    print("=== Debug da Edição de Posts do Feed ===")
    
    # Verificar posts existentes
    posts = FeedPost.objects.all()
    print(f"Total de posts: {posts.count()}")
    
    if posts.count() == 0:
        print("Nenhum post encontrado")
        return
    
    # Pegar o primeiro post para teste
    post = posts.first()
    print(f"\n--- Post para teste ---")
    print(f"ID: {post.id}")
    print(f"Título: {post.titulo}")
    print(f"Conteúdo: {post.conteudo}")
    print(f"Tipo: {post.tipo_post}")
    print(f"Autor: {post.autor}")
    print(f"Ativo: {post.ativo}")
    print(f"Destaque: {post.destaque}")
    print(f"Ordem: {post.ordem_exibicao}")
    print(f"Data publicação: {post.data_publicacao}")
    print(f"Data atualização: {post.data_atualizacao}")
    
    # Testar diferentes cenários de edição
    print(f"\n--- Testando Cenários de Edição ---")
    
    # Cenário 1: Edição simples (sem imagem)
    print(f"\n1. Edição simples (sem imagem):")
    edit_data_1 = {
        'titulo': 'Título Editado - Teste 1',
        'conteudo': 'Conteúdo editado para teste 1',
        'tipo_post': 'evento',
        'autor': 'ABMEPI Oficial',
        'ativo': True,
        'destaque': True,
        'ordem_exibicao': 5
    }
    
    form1 = FeedPostForm(edit_data_1, instance=post)
    if form1.is_valid():
        print("✓ Formulário 1 válido")
        updated_post = form1.save()
        print(f"✓ Post atualizado: {updated_post.titulo}")
        print(f"✓ Nova ordem: {updated_post.ordem_exibicao}")
        print(f"✓ Data atualização: {updated_post.data_atualizacao}")
    else:
        print("✗ Formulário 1 inválido")
        print(f"✗ Erros: {form1.errors}")
    
    # Cenário 2: Edição com campos vazios
    print(f"\n2. Edição com campos vazios:")
    edit_data_2 = {
        'titulo': 'Título Editado - Teste 2',
        'conteudo': 'Conteúdo editado para teste 2',
        'tipo_post': 'noticia',
        'autor': 'ABMEPI Oficial',
        'ativo': False,
        'destaque': False,
        'ordem_exibicao': 0
    }
    
    form2 = FeedPostForm(edit_data_2, instance=post)
    if form2.is_valid():
        print("✓ Formulário 2 válido")
        updated_post = form2.save()
        print(f"✓ Post atualizado: {updated_post.titulo}")
        print(f"✓ Ativo: {updated_post.ativo}")
        print(f"✓ Destaque: {updated_post.destaque}")
        print(f"✓ Data atualização: {updated_post.data_atualizacao}")
    else:
        print("✗ Formulário 2 inválido")
        print(f"✗ Erros: {form2.errors}")
    
    # Cenário 3: Validação de campos obrigatórios
    print(f"\n3. Validação de campos obrigatórios:")
    edit_data_3 = {
        'titulo': '',  # Título vazio
        'conteudo': 'Conteúdo válido',
        'tipo_post': 'noticia',
        'autor': 'ABMEPI Oficial',
        'ativo': True,
        'destaque': False,
        'ordem_exibicao': 1
    }
    
    form3 = FeedPostForm(edit_data_3, instance=post)
    if form3.is_valid():
        print("✓ Formulário 3 válido (não deveria ser)")
    else:
        print("✗ Formulário 3 inválido (esperado)")
        print(f"✗ Erros: {form3.errors}")
    
    # Verificar estado final do post
    print(f"\n--- Estado Final do Post ---")
    post.refresh_from_db()
    print(f"ID: {post.id}")
    print(f"Título: {post.titulo}")
    print(f"Conteúdo: {post.conteudo}")
    print(f"Tipo: {post.tipo_post}")
    print(f"Autor: {post.autor}")
    print(f"Ativo: {post.ativo}")
    print(f"Destaque: {post.destaque}")
    print(f"Ordem: {post.ordem_exibicao}")
    print(f"Data publicação: {post.data_publicacao}")
    print(f"Data atualização: {post.data_atualizacao}")
    
    print("\n=== Debug Concluído ===")

if __name__ == '__main__':
    debug_feed_post_edit()
