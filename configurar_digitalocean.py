#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente no DigitalOcean
Este script gera as configurações que você precisa copiar para o painel
"""

import os
from django.core.management.utils import get_random_secret_key

def gerar_configuracoes():
    """Gera todas as configurações necessárias para o DigitalOcean"""
    
    # Gerar SECRET_KEY
    secret_key = get_random_secret_key()
    
    # Configurações base
    configs = {
        'SECRET_KEY': secret_key,
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1',
        'DIGITALOCEAN_APP_PLATFORM': 'True',
        'SECURE_SSL_REDIRECT': 'False',
        'SESSION_COOKIE_SECURE': 'True',
        'CSRF_COOKIE_SECURE': 'True',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'EMAIL_USE_TLS': 'True',
        'EMAIL_HOST_USER': 'siteabmepi@gmail.com',
        'EMAIL_HOST_PASSWORD': 'tlvt twcz livv zetu',
        'DEFAULT_FROM_EMAIL': 'siteabmepi@gmail.com',
        'SERVER_EMAIL': 'siteabmepi@gmail.com'
    }
    
    print("🔧 CONFIGURAÇÕES PARA DIGITALOCEAN")
    print("=" * 50)
    print()
    print("📋 Copie e cole estas variáveis no painel do DigitalOcean:")
    print()
    
    for key, value in configs.items():
        print(f"Chave: {key}")
        print(f"Valor: {value}")
        print(f"Criptografar: {'Sim' if key == 'SECRET_KEY' or 'PASSWORD' in key else 'Não'}")
        print("-" * 30)
    
    print()
    print("🚀 INSTRUÇÕES:")
    print("1. Acesse o painel do DigitalOcean")
    print("2. Vá em 'Variáveis de ambiente no nível do aplicativo'")
    print("3. Adicione cada chave-valor acima")
    print("4. Marque 'Criptografar' para SECRET_KEY e senhas")
    print("5. Clique em 'Salvar'")
    print("6. Faça o redeploy da aplicação")
    
    # Salvar em arquivo para referência
    with open('configuracoes_digitalocean.txt', 'w', encoding='utf-8') as f:
        f.write("CONFIGURAÇÕES PARA DIGITALOCEAN\n")
        f.write("=" * 50 + "\n\n")
        for key, value in configs.items():
            f.write(f"{key}={value}\n")
    
    print()
    print("💾 Configurações salvas em: configuracoes_digitalocean.txt")

if __name__ == "__main__":
    gerar_configuracoes()
