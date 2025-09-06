#!/usr/bin/env python3
"""
Script para verificar e criar comunicados de teste
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from administrativo.models import Comunicado
from core.models import Usuario
from django.utils import timezone

def check_and_create_comunicados():
    """Verificar comunicados existentes e criar alguns para teste"""
    
    # Verificar comunicados existentes
    comunicados = Comunicado.objects.all()
    print(f"📊 Total de comunicados no banco: {comunicados.count()}")
    
    if comunicados.exists():
        print("\n📋 Comunicados existentes:")
        for c in comunicados:
            print(f"  ID: {c.pk} - {c.titulo} (Status: {'Ativo' if c.ativo else 'Inativo'})")
    else:
        print("❌ Nenhum comunicado encontrado!")
    
    # Buscar um usuário administrador para criar comunicados
    admin_user = Usuario.objects.filter(tipo_usuario='administrador_sistema').first()
    
    if not admin_user:
        print("❌ Nenhum usuário administrador encontrado!")
        return
    
    # Criar comunicados de teste se não existirem
    if comunicados.count() < 3:
        print(f"\n🔧 Criando comunicados de teste...")
        
        comunicados_teste = [
            {
                'titulo': 'Bem-vindos ao Sistema ASSEJUS',
                'conteudo': 'Sejam bem-vindos ao novo sistema da ASSEJUS! Aqui vocês encontrarão todas as informações e serviços disponíveis.',
                'tipo': 'informacao',
                'prioridade': 'normal',
                'ativo': True
            },
            {
                'titulo': 'Reunião Mensal - Próxima Semana',
                'conteudo': 'Informamos que a reunião mensal da associação será realizada na próxima semana. Todos os associados estão convidados.',
                'tipo': 'evento',
                'prioridade': 'alta',
                'ativo': True
            },
            {
                'titulo': 'Atualização de Dados Cadastrais',
                'conteudo': 'Solicitamos que todos os associados atualizem seus dados cadastrais no sistema para manter as informações sempre atualizadas.',
                'tipo': 'lembrete',
                'prioridade': 'normal',
                'ativo': True
            }
        ]
        
        for dados in comunicados_teste:
            comunicado = Comunicado.objects.create(
                titulo=dados['titulo'],
                conteudo=dados['conteudo'],
                tipo=dados['tipo'],
                prioridade=dados['prioridade'],
                ativo=dados['ativo'],
                autor=admin_user,
                data_publicacao=timezone.now()
            )
            print(f"✅ Comunicado criado: ID {comunicado.pk} - {comunicado.titulo}")
    
    print(f"\n🎉 Verificação concluída! Total de comunicados: {Comunicado.objects.count()}")

if __name__ == "__main__":
    check_and_create_comunicados()

