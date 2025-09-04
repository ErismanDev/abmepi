#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from core.models import AssejurNews

# Encontrar e desativar a notícia redundante
noticia = AssejurNews.objects.filter(titulo__icontains='SEMINÁRIO SOBRE DIREITO MILITAR').first()

if noticia:
    print(f"Encontrada notícia: {noticia.titulo}")
    print(f"ID: {noticia.id}")
    print(f"Status atual: {'Ativa' if noticia.ativo else 'Inativa'}")
    
    # Desativar a notícia
    noticia.ativo = False
    noticia.save()
    
    print("✅ Notícia desativada com sucesso!")
    print("A tarjeta não aparecerá mais na página principal.")
else:
    print("❌ Notícia não encontrada.")
    
    # Listar todas as notícias para verificar
    print("\n📋 Todas as notícias disponíveis:")
    for n in AssejurNews.objects.all():
        status = "✅ Ativa" if n.ativo else "❌ Inativa"
        print(f"  {n.id}: {n.titulo} - {status}")
