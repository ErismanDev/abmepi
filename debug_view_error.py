#!/usr/bin/env python
"""
Debug do erro 400 nas views
"""
import os
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from psicologia.models import Paciente, Sessao

def debug_view():
    """Debug do erro na view"""
    
    print("🔍 Debugando erro 400...")
    
    # Buscar paciente
    paciente = Paciente.objects.first()
    if not paciente:
        print("❌ Nenhum paciente encontrado")
        return
    
    print(f"✅ Paciente encontrado: {paciente.associado.nome}")
    print(f"   ID: {paciente.pk}")
    print(f"   Psicólogo responsável: {paciente.psicologo_responsavel}")
    
    # Verificar sessões
    try:
        sessoes = Sessao.objects.filter(paciente=paciente)
        print(f"   Total de sessões: {sessoes.count()}")
        
        sessoes_realizadas = Sessao.objects.filter(
            paciente=paciente,
            status='realizada'
        )
        print(f"   Sessões realizadas: {sessoes_realizadas.count()}")
        
        tem_sessoes = sessoes_realizadas.exists()
        print(f"   Tem sessões realizadas: {tem_sessoes}")
        
        if tem_sessoes:
            print("   Primeira sessão realizada:", sessoes_realizadas.first())
        
    except Exception as e:
        print(f"❌ Erro ao verificar sessões: {e}")
        print(f"   Tipo do erro: {type(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_view()





