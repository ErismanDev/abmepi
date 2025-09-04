#!/usr/bin/env python
"""
Script simples para testar validação de CPF
"""

import re

def validar_cpf(cpf):
    """Valida CPF usando algoritmo oficial"""
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True

def testar_cpfs():
    """Testa vários CPFs para verificar a validação"""
    cpfs_teste = [
        "123.456.789-00",  # CPF inválido (todos dígitos iguais)
        "111.111.111-11",  # CPF inválido (todos dígitos iguais)
        "123.456.789-09",  # CPF inválido
        "338.886.473-04",  # CPF válido
        "490.083.823-34",  # CPF válido
        "12345678909",     # CPF inválido
        "123.456.789-10",  # CPF inválido
    ]
    
    print("=== TESTE DE VALIDAÇÃO DE CPF ===\n")
    
    for cpf in cpfs_teste:
        valido = validar_cpf(cpf)
        status = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        print(f"{cpf}: {status}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_cpfs()
