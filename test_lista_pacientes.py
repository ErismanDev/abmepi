#!/usr/bin/env python
"""
Teste específico da lista de pacientes
"""
import os
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

def test_lista():
    """Teste da lista de pacientes"""
    
    print("🧪 Testando lista de pacientes...")
    
    # Buscar usuário admin
    User = get_user_model()
    admin = User.objects.filter(tipo_usuario='administrador_sistema').first()
    if not admin:
        print("❌ Nenhum admin encontrado")
        return
    
    print(f"✅ Admin encontrado: {admin.username}")
    
    # Testar acesso à lista
    client = Client()
    client.force_login(admin)
    
    url = reverse('psicologia:paciente_list')
    print(f"🌐 Testando acesso a: {url}")
    
    try:
        response = client.get(url)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Lista carregada com sucesso")
            content = response.content.decode('utf-8')
            if 'FLAUBERT' in content:
                print("✅ Paciente encontrado na lista")
            else:
                print("⚠️ Paciente não encontrado na lista")
        else:
            print(f"❌ Erro ao carregar lista: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Conteúdo: {response.content[:500]}")
    except Exception as e:
        print(f"❌ Exceção: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_lista()





