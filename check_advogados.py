#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.models import Advogado

# Verificar advogados
total = Advogado.objects.count()
print(f"Total de advogados no banco: {total}")

if total > 0:
    print("\nAdvogados encontrados:")
    for adv in Advogado.objects.all()[:5]:
        print(f"- {adv.nome} (OAB: {adv.oab}) - Ativo: {adv.ativo}")
else:
    print("\nNenhum advogado encontrado no banco de dados.")
    print("Isso explica por que a tabela está vazia no template.")
