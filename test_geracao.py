#!/usr/bin/env python
"""
Teste para verificar a geração de mensalidades
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

def test_geracao():
    print("=== Teste de Geração de Mensalidades ===")
    
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
    
    # Verificar mensalidades por mês/ano
    mes_atual = date.today().month
    ano_atual = date.today().year
    mensalidades_mes = mensalidades.filter(
        data_vencimento__month=mes_atual,
        data_vencimento__year=ano_atual
    )
    print(f"Mensalidades para {mes_atual}/{ano_atual}: {mensalidades_mes.count()}")

def test_simulacao_geracao():
    print("\n=== Teste de Simulação de Geração ===")
    
    # Parâmetros de teste
    mes_inicial = 8  # Agosto
    ano = 2025
    quantidade_meses = 3
    dia_vencimento = 10
    
    print(f"Simulando geração para {quantidade_meses} meses a partir de {mes_inicial}/{ano}")
    
    # Buscar tipo de mensalidade
    try:
        tipo = TipoMensalidade.objects.filter(ativo=True, categoria='mensalidade').first()
        if not tipo:
            print("ERRO: Nenhum tipo de mensalidade encontrado")
            return
        print(f"Tipo selecionado: {tipo.nome}")
    except Exception as e:
        print(f"ERRO ao buscar tipo: {e}")
        return
    
    # Buscar associados ativos
    try:
        associados_ativos = Associado.objects.filter(ativo=True)
        print(f"Associados ativos encontrados: {associados_ativos.count()}")
    except Exception as e:
        print(f"ERRO ao buscar associados: {e}")
        return
    
    # Simular geração
    mensalidades_criadas = 0
    mensalidades_duplicadas = 0
    
    for i in range(quantidade_meses):
        mes_atual = mes_inicial + i
        ano_atual = ano
        
        # Ajustar mês e ano se passar de dezembro
        if mes_atual > 12:
            mes_atual = mes_atual - 12
            ano_atual = ano + 1
        
        print(f"  Processando mês {mes_atual}/{ano_atual}")
        
        for associado in associados_ativos:
            # Verificar se já existe mensalidade para este mês/ano
            if not Mensalidade.objects.filter(
                associado=associado,
                tipo=tipo,
                data_vencimento__month=mes_atual,
                data_vencimento__year=ano_atual
            ).exists():
                # Calcular data de vencimento
                try:
                    data_vencimento = date(ano_atual, mes_atual, dia_vencimento)
                    print(f"    Criando mensalidade para {associado.nome} - {data_vencimento}")
                    mensalidades_criadas += 1
                except ValueError as e:
                    print(f"    ERRO ao criar data para {associado.nome}: {e}")
            else:
                print(f"    Mensalidade já existe para {associado.nome} - {mes_atual}/{ano_atual}")
                mensalidades_duplicadas += 1
    
    print(f"\nResumo da simulação:")
    print(f"  - Mensalidades que seriam criadas: {mensalidades_criadas}")
    print(f"  - Mensalidades duplicadas: {mensalidades_duplicadas}")

if __name__ == '__main__':
    test_geracao()
    test_simulacao_geracao()
