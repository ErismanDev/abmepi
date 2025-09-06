#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def teste_links_final():
    print("=== TESTE FINAL: Links do Menu ===")
    
    # Buscar um administrador
    admin = User.objects.filter(tipo_usuario='administrador_sistema').first()
    if not admin:
        print("❌ Nenhum administrador encontrado")
        return
    
    print(f"✅ Administrador: {admin.get_full_name()}")
    print(f"🏷️ Tipo de usuário: {admin.tipo_usuario}")
    
    # Testar acesso ao dashboard
    client = Client(HTTP_HOST='127.0.0.1:8000')
    client.force_login(admin)
    
    response = client.get('/dashboard/')
    print(f"📊 Dashboard: Status {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar se a variável user_tipo está sendo passada
        if 'user_tipo' in content:
            print("✅ Variável user_tipo encontrada no HTML")
        else:
            print("❌ Variável user_tipo NÃO encontrada no HTML")
        
        # Verificar se os links estão sendo renderizados
        links_checks = [
            ('href="/dashboard/"', 'Link Dashboard'),
            ('href="/associados/"', 'Link Associados'),
            ('href="/assejus/"', 'Link Assejus'),
            ('href="/psicologia/"', 'Link Psicologia'),
            ('href="/financeiro/"', 'Link Financeiro'),
            ('href="/beneficios/"', 'Link Benefícios'),
            ('href="/core/usuarios/"', 'Link Usuários'),
            ('href="/hotel-transito/"', 'Link Hotel'),
            ('href="/admin/"', 'Link Admin Django')
        ]
        
        for check, description in links_checks:
            if check in content:
                print(f"✅ {description}: Encontrado")
            else:
                print(f"❌ {description}: NÃO encontrado")
        
        # Verificar se há links com classes corretas
        if 'class="menu-link"' in content:
            print("✅ Classe menu-link encontrada")
        else:
            print("❌ Classe menu-link NÃO encontrada")
        
        if 'class="submenu-link"' in content:
            print("✅ Classe submenu-link encontrada")
        else:
            print("❌ Classe submenu-link NÃO encontrada")
        
        # Verificar se há ícones
        if '<i class="fas fa-' in content:
            print("✅ Ícones FontAwesome encontrados")
        else:
            print("❌ Ícones FontAwesome NÃO encontrados")
        
        # Verificar se há submenus
        if 'data-target=' in content:
            print("✅ Data-target para submenus encontrado")
        else:
            print("❌ Data-target para submenus NÃO encontrado")
        
        # Verificar se há notificações
        if 'notificacoes_pendentes' in content:
            print("✅ Sistema de notificações funcionando")
        else:
            print("❌ Sistema de notificações NÃO funcionando")
        
        # Verificar se há JavaScript para submenus
        if 'menu-toggle' in content:
            print("✅ JavaScript menu-toggle encontrado")
        else:
            print("❌ JavaScript menu-toggle NÃO encontrado")
        
        # Salvar HTML para análise
        with open('teste_links_final.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("📄 HTML salvo em teste_links_final.html")
    
    print(f"\n{'='*60}")
    print("🎯 INSTRUÇÕES PARA TESTAR:")
    print("1. Acesse http://127.0.0.1:8000/dashboard/")
    print("2. Faça login com um administrador")
    print("3. Verifique se o menu lateral azul está visível à esquerda")
    print("4. Verifique se os links do menu estão visíveis")
    print("5. Teste os submenus clicando nas setas (▼)")
    print("6. Verifique se há uma notificação no navbar (badge vermelho)")
    print("7. Verifique se a notificação aparece na seção do dashboard")
    print(f"{'='*60}")

if __name__ == "__main__":
    teste_links_final()



