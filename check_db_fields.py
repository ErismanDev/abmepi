#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.db import connection

def check_field_lengths():
    cursor = connection.cursor()
    
    # Verificar campos com character_maximum_length = 14
    cursor.execute("""
        SELECT column_name, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'psicologia_psicologo' 
        AND character_maximum_length = 14;
    """)
    
    fields_14 = cursor.fetchall()
    print("Campos com max_length=14:")
    for field in fields_14:
        print(f"  {field[0]}: {field[1]}")
    
    # Verificar todos os campos varchar da tabela
    cursor.execute("""
        SELECT column_name, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'psicologia_psicologo' 
        AND data_type = 'character varying'
        ORDER BY character_maximum_length;
    """)
    
    all_varchar_fields = cursor.fetchall()
    print("\nTodos os campos varchar:")
    for field in all_varchar_fields:
        print(f"  {field[0]}: {field[1]}")

if __name__ == "__main__":
    check_field_lengths()

