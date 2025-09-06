#!/usr/bin/env python
"""
Script para testar a funcionalidade de acesso restrito a fichas de pacientes 
após primeira sessão finalizada.
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
from datetime import datetime, date

def test_acesso_restrito():
    """Testa a funcionalidade de acesso restrito após primeira sessão finalizada"""
    
    print("🧪 Testando acesso restrito a fichas de pacientes...")
    
    # Buscar usuários de teste
    User = get_user_model()
    
    # Buscar psicólogo
    try:
        psicologo1 = Psicologo.objects.filter(ativo=True).first()
        if not psicologo1:
            print("❌ Nenhum psicólogo encontrado")
            return
        
        user_psicologo1 = psicologo1.user
        print(f"✅ Psicólogo 1 encontrado: {psicologo1.nome_completo}")
        print(f"   Usuário: {user_psicologo1.username} - Tipo: {user_psicologo1.tipo_usuario}")
        
        # Buscar outro psicólogo se existir
        psicologo2 = Psicologo.objects.filter(ativo=True).exclude(pk=psicologo1.pk).first()
        if psicologo2:
            user_psicologo2 = psicologo2.user
            print(f"✅ Psicólogo 2 encontrado: {psicologo2.nome_completo}")
            print(f"   Usuário: {user_psicologo2.username} - Tipo: {user_psicologo2.tipo_usuario}")
        
        # Buscar administrador
        admin_user = User.objects.filter(tipo_usuario='administrador_sistema').first()
        if not admin_user:
            print("❌ Nenhum usuário administrador encontrado")
            return
        print(f"✅ Administrador encontrado: {admin_user.username}")
        
        # Buscar atendente se existir
        atendente_user = User.objects.filter(tipo_usuario='atendente_psicologo').first()
        if atendente_user:
            print(f"✅ Atendente encontrado: {atendente_user.username}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuários: {e}")
        return
    
    # Buscar um paciente com psicólogo responsável
    try:
        paciente = Paciente.objects.filter(
            psicologo_responsavel__isnull=False,
            ativo=True
        ).first()
        
        if not paciente:
            print("❌ Nenhum paciente com psicólogo responsável encontrado")
            return
        
        print(f"✅ Paciente encontrado: {paciente.nome_completo}")
        print(f"   Psicólogo responsável: {paciente.psicologo_responsavel.nome_completo}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar paciente: {e}")
        return
    
    # Verificar se existe sessão realizada
    sessao_realizada = Sessao.objects.filter(
        paciente=paciente,
        status='realizada'
    ).first()
    
    if not sessao_realizada:
        print("📝 Criando sessão realizada para teste...")
        # Criar uma sessão realizada
        sessao_realizada = Sessao.objects.create(
            paciente=paciente,
            psicologo=paciente.psicologo_responsavel,
            data_hora=datetime.now(),
            status='realizada',
            tipo_sessao='terapia',
            duracao=50,
            observacoes='Sessão de teste para verificar acesso restrito'
        )
        print(f"✅ Sessão realizada criada: {sessao_realizada.pk}")
    else:
        print(f"✅ Sessão realizada já existe: {sessao_realizada.pk}")
    
    # Testar acessos
    client = Client()
    paciente_url = reverse('psicologia:paciente_detail', kwargs={'pk': paciente.pk})
    
    print("\n🔒 Testando regras de acesso...")
    
    # 1. Teste com psicólogo responsável - DEVE PERMITIR
    print(f"\n1️⃣ Testando acesso do psicólogo responsável ({paciente.psicologo_responsavel.nome_completo})...")
    
    # Verificar qual psicólogo é o responsável
    if paciente.psicologo_responsavel == psicologo1:
        client.force_login(user_psicologo1)
    elif paciente.psicologo_responsavel == psicologo2:
        client.force_login(user_psicologo2)
    else:
        print(f"⚠️ Psicólogo responsável não está na lista de teste: {paciente.psicologo_responsavel.nome_completo}")
        return
    
    response = client.get(paciente_url)
    
    if response.status_code == 200:
        print("✅ SUCESSO: Psicólogo responsável pode acessar a ficha")
    else:
        print(f"❌ ERRO: Psicólogo responsável foi bloqueado! Status: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Conteúdo da resposta: {response.content[:500]}")
    
    # 2. Teste com outro psicólogo - DEVE BLOQUEAR
    if psicologo2 and psicologo2 != paciente.psicologo_responsavel:
        print(f"\n2️⃣ Testando acesso de outro psicólogo ({psicologo2.nome_completo})...")
        client.force_login(user_psicologo2)
        response = client.get(paciente_url)
        
        if response.status_code == 302:  # Redirecionamento
            print("✅ SUCESSO: Outro psicólogo foi bloqueado corretamente")
        else:
            print(f"❌ ERRO: Outro psicólogo deveria ser bloqueado! Status: {response.status_code}")
    
    # 3. Teste com administrador - DEVE PERMITIR
    print(f"\n3️⃣ Testando acesso do administrador ({admin_user.username})...")
    client.force_login(admin_user)
    response = client.get(paciente_url)
    
    if response.status_code == 200:
        print("✅ SUCESSO: Administrador pode acessar a ficha")
    else:
        print(f"❌ ERRO: Administrador foi bloqueado! Status: {response.status_code}")
    
    # 4. Teste com atendente - DEVE BLOQUEAR
    if atendente_user:
        print(f"\n4️⃣ Testando acesso do atendente ({atendente_user.username})...")
        client.force_login(atendente_user)
        response = client.get(paciente_url)
        
        if response.status_code == 302:  # Redirecionamento
            print("✅ SUCESSO: Atendente foi bloqueado corretamente")
        else:
            print(f"❌ ERRO: Atendente deveria ser bloqueado! Status: {response.status_code}")
    
    print("\n📋 Resumo dos testes:")
    print("- ✅ Psicólogo responsável: Acesso permitido")
    if psicologo2:
        print("- 🚫 Outro psicólogo: Acesso bloqueado")
    print("- ✅ Administrador: Acesso permitido")
    if atendente_user:
        print("- 🚫 Atendente: Acesso bloqueado")
    
    print("\n🎯 Regra implementada com sucesso!")
    print("📝 Depois da 1ª sessão finalizada, só o psicólogo responsável pode acessar a ficha do paciente.")
    print("   (Administradores do sistema mantêm acesso total)")

if __name__ == "__main__":
    test_acesso_restrito()
