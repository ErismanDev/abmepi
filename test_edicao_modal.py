#!/usr/bin/env python
"""
Teste da funcionalidade de edição modal de pacientes
"""
import os
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from psicologia.models import Paciente, Sessao

def test_edicao_modal():
    """Testa a funcionalidade de edição modal"""
    
    print("🧪 Testando edição modal de pacientes...")
    
    # Buscar usuário admin
    User = get_user_model()
    admin = User.objects.filter(tipo_usuario='administrador_sistema').first()
    if not admin:
        print("❌ Nenhum admin encontrado")
        return
    
    print(f"✅ Admin encontrado: {admin.username}")
    
    # Buscar paciente para editar
    paciente = Paciente.objects.filter(ativo=True).first()
    if not paciente:
        print("❌ Nenhum paciente ativo encontrado")
        return
    
    print(f"✅ Paciente encontrado: {paciente.associado.nome}")
    print(f"   Psicólogo responsável: {paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else 'N/A'}")
    
    # Verificar se tem sessões realizadas
    tem_sessoes = Sessao.objects.filter(
        paciente=paciente,
        status='realizada'
    ).exists()
    
    print(f"   Tem sessões realizadas: {tem_sessoes}")
    
    # Testar acesso à view modal
    client = Client()
    client.force_login(admin)
    
    url = reverse('psicologia:paciente_update_modal', args=[paciente.pk])
    print(f"🌐 Testando acesso a: {url}")
    
    try:
        response = client.get(url)
        print(f"📊 Status GET: {response.status_code}")
        
        # Testar POST com dados de edição
        data = {
            'associado': paciente.associado.pk,
            'psicologo_responsavel': paciente.psicologo_responsavel.pk if paciente.psicologo_responsavel else '',
            'data_primeira_consulta': paciente.data_primeira_consulta.strftime('%Y-%m-%d') if paciente.data_primeira_consulta else '',
            'observacoes_iniciais': paciente.observacoes_iniciais or 'Teste de edição modal'
        }
        
        response = client.post(url, data)
        print(f"📊 Status POST: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Edição modal funcionando!")
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'success' in content:
                    print("✅ Resposta JSON recebida")
                else:
                    print("⚠️ Resposta não é JSON")
        else:
            print(f"❌ Erro na edição modal: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Conteúdo: {response.content[:500]}")
                
    except Exception as e:
        print(f"❌ Exceção: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_edicao_modal()
