#!/usr/bin/env python
"""
Teste completo das restrições de acesso implementadas
"""
import os
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from psicologia.models import Paciente, Sessao, Psicologo
from associados.models import Associado

def test_restricoes_completo():
    """Teste completo das restrições implementadas"""
    
    print("🧪 Teste completo das restrições de acesso...")
    
    # Buscar dados de teste
    User = get_user_model()
    
    # Buscar usuários
    admin = User.objects.filter(tipo_usuario='administrador_sistema').first()
    atendente = User.objects.filter(tipo_usuario='atendente_psicologo').first()
    psicologo1 = Psicologo.objects.filter(ativo=True).first()
    psicologo2 = Psicologo.objects.filter(ativo=True).exclude(pk=psicologo1.pk).first() if psicologo1 else None
    
    if not all([admin, psicologo1]):
        print("❌ Usuários necessários não encontrados")
        return
    
    # Buscar paciente com sessões realizadas
    paciente = Paciente.objects.filter(
        sessao__status='realizada'
    ).distinct().first()
    
    if not paciente:
        print("❌ Nenhum paciente com sessões realizadas encontrado")
        return
    
    print(f"✅ Dados de teste encontrados:")
    print(f"   Admin: {admin.username}")
    print(f"   Atendente: {atendente.username if atendente else 'N/A'}")
    print(f"   Psicólogo 1: {psicologo1.nome_completo}")
    print(f"   Psicólogo 2: {psicologo2.nome_completo if psicologo2 else 'N/A'}")
    print(f"   Paciente: {paciente.associado.nome}")
    print(f"   Psicólogo responsável: {paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else 'N/A'}")
    
    client = Client()
    
    def test_acesso(user, user_label, should_allow=False):
        """Testa acesso para um usuário específico"""
        print(f"\n🔍 Testando {user_label}...")
        client.force_login(user)
        
        # URLs para testar
        urls = {
            'detail': reverse('psicologia:paciente_detail', args=[paciente.pk]),
            'update': reverse('psicologia:paciente_update', args=[paciente.pk]),
            'delete': reverse('psicologia:paciente_delete', args=[paciente.pk])
        }
        
        for action, url in urls.items():
            try:
                response = client.get(url)
                if should_allow:
                    if response.status_code == 200:
                        print(f"   ✅ {action.title()}: PERMITIDO (200)")
                    else:
                        print(f"   ❌ {action.title()}: BLOQUEADO INCORRETAMENTE ({response.status_code})")
                else:
                    if response.status_code == 302:
                        print(f"   ✅ {action.title()}: BLOQUEADO CORRETAMENTE (302)")
                    elif response.status_code == 200:
                        print(f"   ❌ {action.title()}: PERMITIDO INCORRETAMENTE (200)")
                    else:
                        print(f"   ⚠️ {action.title()}: ERRO ({response.status_code})")
            except Exception as e:
                print(f"   ❌ {action.title()}: EXCEÇÃO ({e})")
    
    # Testar diferentes usuários
    
    # 1. Admin (deve ser bloqueado)
    test_acesso(admin, "Administrador", should_allow=False)
    
    # 2. Atendente (deve ser bloqueado)
    if atendente:
        test_acesso(atendente, "Atendente", should_allow=False)
    
    # 3. Psicólogo responsável (deve ser permitido)
    if paciente.psicologo_responsavel:
        test_acesso(
            paciente.psicologo_responsavel.user, 
            f"Psicólogo Responsável ({paciente.psicologo_responsavel.nome_completo})", 
            should_allow=True
        )
    
    # 4. Outro psicólogo (deve ser bloqueado)
    if psicologo2 and psicologo2 != paciente.psicologo_responsavel:
        test_acesso(
            psicologo2.user, 
            f"Outro Psicólogo ({psicologo2.nome_completo})", 
            should_allow=False
        )
    
    print(f"\n🏁 Teste concluído!")

if __name__ == "__main__":
    test_restricoes_completo()





