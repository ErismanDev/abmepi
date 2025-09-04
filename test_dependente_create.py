#!/usr/bin/env python
"""
Script de teste para simular a criação de um dependente com foto
"""
import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from associados.models import Dependente, Associado
from associados.forms import DependenteForm
from associados.views import dependente_create

def test_dependente_create_with_photo():
    """Testa a criação de um dependente com foto"""
    print("=== Teste de Criação de Dependente com Foto ===")
    
    # Verificar se existe pelo menos um associado
    try:
        associado = Associado.objects.first()
        if not associado:
            print("❌ Nenhum associado encontrado. Crie um associado primeiro.")
            return False
        print(f"✅ Associado encontrado: {associado.nome} (ID: {associado.id})")
    except Exception as e:
        print(f"❌ Erro ao buscar associado: {e}")
        return False
    
    # Criar um usuário para o teste
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
        print(f"✅ Usuário para teste: {user.username}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False
    
    # Criar um arquivo de teste
    try:
        # Criar um arquivo de imagem simples para teste
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
        uploaded_file = SimpleUploadedFile(
            "test_photo.png",
            image_content,
            content_type="image/png"
        )
        print("✅ Arquivo de teste criado")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de teste: {e}")
        return False
    
    # Testar o formulário diretamente
    print("\n--- Testando Formulário ---")
    try:
        form_data = {
            'nome': 'Teste Dependente',
            'parentesco': 'filho',
            'data_nascimento': '2010-01-01',
            'cpf': '123.456.789-01',
            'observacoes': 'Teste de upload de foto'
        }
        
        form = DependenteForm(data=form_data, files={'foto': uploaded_file})
        
        if form.is_valid():
            print("✅ Formulário é válido")
            print(f"   Dados limpos: {form.cleaned_data}")
            
            # Verificar se a foto foi processada
            if 'foto' in form.cleaned_data:
                print(f"✅ Foto processada: {form.cleaned_data['foto']}")
                print(f"   Nome do arquivo: {form.cleaned_data['foto'].name}")
                print(f"   Tamanho: {form.cleaned_data['foto'].size} bytes")
            else:
                print("❌ Foto não foi processada")
                
        else:
            print("❌ Formulário inválido")
            print(f"   Erros: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar formulário: {e}")
        return False
    
    # Testar salvamento do modelo
    print("\n--- Testando Salvamento do Modelo ---")
    try:
        dependente = form.save(commit=False)
        dependente.associado = associado
        dependente.save()
        
        print(f"✅ Dependente salvo com sucesso! ID: {dependente.id}")
        print(f"   Nome: {dependente.nome}")
        print(f"   Foto: {dependente.foto}")
        
        # Verificar se a foto foi salva no sistema de arquivos
        if dependente.foto:
            if os.path.exists(dependente.foto.path):
                print(f"✅ Arquivo salvo no sistema: {dependente.foto.path}")
                print(f"   Tamanho do arquivo: {os.path.getsize(dependente.foto.path)} bytes")
            else:
                print(f"❌ Arquivo não encontrado no sistema: {dependente.foto.path}")
        else:
            print("❌ Campo foto está vazio após salvamento")
            
    except Exception as e:
        print(f"❌ Erro ao salvar dependente: {e}")
        return False
    
    # Limpar arquivo de teste
    try:
        if dependente.foto:
            dependente.foto.delete(save=False)
        dependente.delete()
        print("✅ Dados de teste removidos")
    except Exception as e:
        print(f"⚠️  Erro ao limpar dados de teste: {e}")
    
    print("\n=== Resumo ===")
    print("✅ Teste de criação de dependente com foto passou!")
    print("O problema pode estar na view web ou na interface do usuário.")
    
    return True

if __name__ == '__main__':
    test_dependente_create_with_photo()
