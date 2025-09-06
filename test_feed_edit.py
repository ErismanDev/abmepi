#!/usr/bin/env python
"""
Script de teste para verificar a edição dos posts do feed
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import FeedPost
from core.forms import FeedPostForm

def test_feed_post_edit():
    """Testa a edição de um post do feed"""
    print("=== Teste de Edição de Post do Feed ===")
    
    # Verificar se existem posts
    posts = FeedPost.objects.all()
    print(f"Total de posts encontrados: {posts.count()}")
    
    if posts.count() == 0:
        print("Nenhum post encontrado. Criando um post de teste...")
        
        # Criar um post de teste
        post = FeedPost.objects.create(
            titulo="Post de Teste para Edição",
            conteudo="Este é um post de teste para verificar se a edição está funcionando.",
            tipo_post="noticia",
            autor="ABMEPI Oficial",
            ativo=True,
            destaque=False,
            ordem_exibicao=0
        )
        print(f"Post criado com ID: {post.id}")
    else:
        post = posts.first()
        print(f"Usando post existente: {post.titulo} (ID: {post.id})")
    
    # Testar edição do post
    print(f"\n--- Testando Edição ---")
    print(f"Título atual: {post.titulo}")
    print(f"Conteúdo atual: {post.conteudo}")
    print(f"Ativo: {post.ativo}")
    print(f"Destaque: {post.destaque}")
    
    # Dados para edição
    edit_data = {
        'titulo': 'Post Editado - Teste de Funcionamento',
        'conteudo': 'Este post foi editado para testar se a funcionalidade está funcionando corretamente.',
        'tipo_post': 'evento',
        'autor': 'ABMEPI Oficial',
        'ativo': True,
        'destaque': True,
        'ordem_exibicao': 1
    }
    
    # Testar formulário
    print(f"\n--- Testando Formulário ---")
    form = FeedPostForm(edit_data, instance=post)
    
    if form.is_valid():
        print("✓ Formulário é válido")
        print(f"✓ Título: {form.cleaned_data['titulo']}")
        print(f"✓ Conteúdo: {form.cleaned_data['conteudo']}")
        print(f"✓ Tipo: {form.cleaned_data['tipo_post']}")
        print(f"✓ Ativo: {form.cleaned_data['ativo']}")
        print(f"✓ Destaque: {form.cleaned_data['destaque']}")
        print(f"✓ Ordem: {form.cleaned_data['ordem_exibicao']}")
        
        # Salvar alterações
        updated_post = form.save()
        print(f"\n✓ Post atualizado com sucesso!")
        print(f"✓ Novo título: {updated_post.titulo}")
        print(f"✓ Novo conteúdo: {updated_post.conteudo}")
        print(f"✓ Novo tipo: {updated_post.tipo_post}")
        print(f"✓ Ativo: {updated_post.ativo}")
        print(f"✓ Destaque: {updated_post.destaque}")
        print(f"✓ Ordem: {updated_post.ordem_exibicao}")
        print(f"✓ Data de atualização: {updated_post.data_atualizacao}")
        
    else:
        print("✗ Formulário inválido")
        print(f"✗ Erros: {form.errors}")
    
    # Verificar se as alterações foram salvas no banco
    print(f"\n--- Verificando Banco de Dados ---")
    post_refreshed = FeedPost.objects.get(pk=post.id)
    print(f"✓ Post no banco: {post_refreshed.titulo}")
    print(f"✓ Conteúdo no banco: {post_refreshed.conteudo}")
    print(f"✓ Tipo no banco: {post_refreshed.tipo_post}")
    print(f"✓ Ativo no banco: {post_refreshed.ativo}")
    print(f"✓ Destaque no banco: {post_refreshed.destaque}")
    print(f"✓ Ordem no banco: {post_refreshed.ordem_exibicao}")
    
    print("\n=== Teste Concluído ===")

if __name__ == '__main__':
    test_feed_post_edit()
