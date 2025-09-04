#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.views import LegislacaoView

def test_legislacao_view():
    """Testa se a view de legislação está funcionando"""
    try:
        # Criar uma requisição fake
        factory = RequestFactory()
        request = factory.get('/legislacao/')
        
        # Criar a view
        view = LegislacaoView()
        view.request = request
        
        # Obter o contexto
        context = view.get_context_data()
        
        print("✅ View de legislação funcionando!")
        print(f"Template: {view.template_name}")
        print(f"Contexto: {list(context.keys())}")
        print(f"Legislações: {list(context['legislacoes'].keys())}")
        
        # Verificar dados específicos
        leis = context['legislacoes']['leis_estaduais']
        print(f"\nLeis estaduais encontradas: {len(leis)}")
        for lei in leis:
            print(f"  - {lei['titulo']} ({lei['categoria']})")
            
    except Exception as e:
        print(f"❌ Erro na view de legislação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_legislacao_view()
