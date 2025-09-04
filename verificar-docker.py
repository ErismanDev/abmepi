#!/usr/bin/env python3
"""
Script para verificar se a configuração Docker está correta
"""

import os
import sys

def verificar_arquivos():
    """Verifica se todos os arquivos necessários estão presentes"""
    
    arquivos_necessarios = [
        'Dockerfile',
        'docker-compose.yml',
        'nginx.conf',
        '.dockerignore',
        'env.docker',
        'deploy-docker.sh',
        'requirements.txt'
    ]
    
    print("🔍 VERIFICANDO ARQUIVOS DOCKER")
    print("=" * 40)
    
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - FALTANDO")
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"\n⚠️  Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    else:
        print("\n✅ Todos os arquivos estão presentes!")
        return True

def verificar_dockerfile():
    """Verifica se o Dockerfile está correto"""
    
    print("\n🐳 VERIFICANDO DOCKERFILE")
    print("=" * 30)
    
    try:
        with open('Dockerfile', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ('FROM python:', 'Imagem base Python'),
            ('WORKDIR /app', 'Diretório de trabalho'),
            ('COPY requirements.txt', 'Cópia do requirements'),
            ('RUN pip install', 'Instalação de dependências'),
            ('EXPOSE 8080', 'Porta exposta'),
            ('CMD ["gunicorn"', 'Comando de inicialização')
        ]
        
        for check, desc in verificacoes:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ Dockerfile não encontrado")
        return False
    
    return True

def verificar_docker_compose():
    """Verifica se o docker-compose.yml está correto"""
    
    print("\n🐳 VERIFICANDO DOCKER-COMPOSE")
    print("=" * 35)
    
    try:
        with open('docker-compose.yml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ('version:', 'Versão do compose'),
            ('services:', 'Definição de serviços'),
            ('web:', 'Serviço web'),
            ('db:', 'Serviço de banco'),
            ('nginx:', 'Serviço nginx'),
            ('ports:', 'Mapeamento de portas'),
            ('environment:', 'Variáveis de ambiente')
        ]
        
        for check, desc in verificacoes:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ docker-compose.yml não encontrado")
        return False
    
    return True

def verificar_nginx():
    """Verifica se o nginx.conf está correto"""
    
    print("\n🌐 VERIFICANDO NGINX")
    print("=" * 25)
    
    try:
        with open('nginx.conf', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ('events {', 'Configuração de eventos'),
            ('http {', 'Configuração HTTP'),
            ('upstream django', 'Upstream para Django'),
            ('server {', 'Configuração do servidor'),
            ('location /', 'Configuração de localização'),
            ('proxy_pass', 'Proxy para Django')
        ]
        
        for check, desc in verificacoes:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ nginx.conf não encontrado")
        return False
    
    return True

def verificar_requirements():
    """Verifica se o requirements.txt tem as dependências necessárias"""
    
    print("\n📦 VERIFICANDO REQUIREMENTS")
    print("=" * 30)
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        dependencias_necessarias = [
            'Django',
            'gunicorn',
            'psycopg2-binary',
            'whitenoise',
            'dj-database-url'
        ]
        
        for dep in dependencias_necessarias:
            if dep in content:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado")
        return False
    
    return True

def main():
    """Função principal"""
    
    print("🐳 VERIFICAÇÃO DA CONFIGURAÇÃO DOCKER")
    print("=" * 50)
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # Verificar configurações
    dockerfile_ok = verificar_dockerfile()
    compose_ok = verificar_docker_compose()
    nginx_ok = verificar_nginx()
    requirements_ok = verificar_requirements()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL")
    print("=" * 50)
    
    if all([arquivos_ok, dockerfile_ok, compose_ok, nginx_ok, requirements_ok]):
        print("✅ CONFIGURAÇÃO DOCKER COMPLETA!")
        print("🚀 Pronto para deploy no DigitalOcean")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure as variáveis de ambiente no DigitalOcean")
        print("2. Faça o deploy da aplicação")
        print("3. Verifique se está funcionando")
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA!")
        print("🔧 Corrija os problemas antes de fazer o deploy")
    
    print("\n📖 Para mais informações, consulte:")
    print("   - DEPLOY_DOCKER_DIGITALOCEAN.md")
    print("   - CONFIGURACOES_DIGITALOCEAN.txt")

if __name__ == "__main__":
    main()
