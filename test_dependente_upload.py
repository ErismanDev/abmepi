#!/usr/bin/env python
"""
Script de teste para verificar upload de fotos de dependentes
"""
import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from associados.models import Dependente, Associado
from associados.forms import DependenteForm

def test_dependente_upload():
    """Testa o upload de foto para dependente"""
    print("=== Teste de Upload de Foto para Dependente ===")
    
    # Verificar se existe pelo menos um associado
    try:
        associado = Associado.objects.first()
        if not associado:
            print("❌ Nenhum associado encontrado. Crie um associado primeiro.")
            return False
        print(f"✅ Associado encontrado: {associado.nome}")
    except Exception as e:
        print(f"❌ Erro ao buscar associado: {e}")
        return False
    
    # Verificar se existe pelo menos um dependente
    try:
        dependente = Dependente.objects.filter(associado=associado).first()
        if not dependente:
            print("❌ Nenhum dependente encontrado para este associado.")
            return False
        print(f"✅ Dependente encontrado: {dependente.nome}")
    except Exception as e:
        print(f"❌ Erro ao buscar dependente: {e}")
        return False
    
    # Verificar configurações de mídia
    from django.conf import settings
    print(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"🌐 MEDIA_URL: {settings.MEDIA_URL}")
    
    # Verificar se a pasta de destino existe
    foto_path = os.path.join(settings.MEDIA_ROOT, 'associados', 'dependentes', 'fotos')
    if os.path.exists(foto_path):
        print(f"✅ Pasta de destino existe: {foto_path}")
    else:
        print(f"❌ Pasta de destino não existe: {foto_path}")
        return False
    
    # Verificar permissões da pasta
    if os.access(foto_path, os.W_OK):
        print("✅ Pasta tem permissão de escrita")
    else:
        print("❌ Pasta não tem permissão de escrita")
        return False
    
    # Verificar se o campo foto está presente no modelo
    if hasattr(dependente, 'foto'):
        print("✅ Campo 'foto' existe no modelo")
        print(f"   Tipo do campo: {type(dependente.foto)}")
        print(f"   Valor atual: {dependente.foto}")
    else:
        print("❌ Campo 'foto' não existe no modelo")
        return False
    
    # Verificar se o campo foto está presente no formulário
    form = DependenteForm(instance=dependente)
    if 'foto' in form.fields:
        print("✅ Campo 'foto' está presente no formulário")
        print(f"   Widget: {form.fields['foto'].widget}")
    else:
        print("❌ Campo 'foto' não está presente no formulário")
        return False
    
    # Verificar se o campo foto está nos campos do formulário
    if 'foto' in form.Meta.fields:
        print("✅ Campo 'foto' está na lista de campos do formulário")
    else:
        print("❌ Campo 'foto' não está na lista de campos do formulário")
        return False
    
    print("\n=== Resumo ===")
    print("✅ Todas as verificações passaram!")
    print("O problema pode estar na view ou no processamento do formulário.")
    
    return True

if __name__ == '__main__':
    test_dependente_upload()
