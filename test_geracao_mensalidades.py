#!/usr/bin/env python
"""
Teste para verificar a geração de mensalidades em lote
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from financeiro.models import TipoMensalidade, Mensalidade
from associados.models import Associado
from datetime import date, timedelta
from decimal import Decimal

def test_geracao_mensalidades_lote():
    print("=== Teste de Geração de Mensalidades em Lote ===")
    
    # Verificar tipos de mensalidade
    tipos = TipoMensalidade.objects.filter(ativo=True, categoria='mensalidade')
    print(f"Tipos de mensalidade ativos: {tipos.count()}")
    for tipo in tipos:
        print(f"  - {tipo.nome} (R$ {tipo.valor}) - Recorrente: {tipo.recorrente}")
    
    # Verificar associados ativos
    associados = Associado.objects.filter(ativo=True)
    print(f"Associados ativos: {associados.count()}")
    
    # Verificar mensalidades existentes
    mensalidades = Mensalidade.objects.all()
    print(f"Total de mensalidades: {mensalidades.count()}")
    
    # Verificar mensalidades por status
    pendentes = mensalidades.filter(status='pendente')
    pagas = mensalidades.filter(status='pago')
    print(f"  - Pendentes: {pendentes.count()}")
    print(f"  - Pagas: {pagas.count()}")
    
    # Simular geração de mensalidades para o próximo mês
    mes_atual = date.today().month
    ano_atual = date.today().year
    
    print(f"\n=== Simulação de Geração para {mes_atual}/{ano_atual} ===")
    
    if tipos.exists() and associados.exists():
        tipo = tipos.first()
        associado = associados.first()
        
        # Verificar se já existe mensalidade para este mês/ano
        mensalidade_existe = Mensalidade.objects.filter(
            associado=associado,
            tipo=tipo,
            data_vencimento__month=mes_atual,
            data_vencimento__year=ano_atual
        ).exists()
        
        print(f"Tipo selecionado: {tipo.nome}")
        print(f"Associado selecionado: {associado.nome}")
        print(f"Mensalidade já existe para {mes_atual}/{ano_atual}: {mensalidade_existe}")
        
        if not mensalidade_existe:
            # Calcular data de vencimento (dia 10 do mês)
            try:
                data_vencimento = date(ano_atual, mes_atual, 10)
                print(f"Data de vencimento calculada: {data_vencimento}")
                
                # Simular criação (sem salvar no banco)
                print(f"Mensalidade seria criada:")
                print(f"  - Associado: {associado.nome}")
                print(f"  - Tipo: {tipo.nome}")
                print(f"  - Valor: R$ {tipo.valor}")
                print(f"  - Vencimento: {data_vencimento}")
                print(f"  - Status: Pendente")
                
            except ValueError as e:
                print(f"ERRO ao calcular data: {e}")
        else:
            print("Mensalidade já existe, não seria criada")
    else:
        print("ERRO: Não há tipos de mensalidade ou associados ativos")
    
    print("\n=== Verificação de Dados ===")
    
    # Verificar se há tipos de mensalidade com categoria 'mensalidade'
    tipos_mensalidade = TipoMensalidade.objects.filter(ativo=True, categoria='mensalidade')
    print(f"Tipos de mensalidade (categoria='mensalidade'): {tipos_mensalidade.count()}")
    
    # Verificar se há associados ativos
    associados_ativos = Associado.objects.filter(ativo=True)
    print(f"Associados ativos: {associados_ativos.count()}")
    
    # Verificar anos disponíveis
    ano_atual = date.today().year
    anos_disponiveis = range(ano_atual, ano_atual + 3)
    print(f"Anos disponíveis: {list(anos_disponiveis)}")
    
    print("\n=== Teste Concluído ===")

if __name__ == '__main__':
    test_geracao_mensalidades_lote()
