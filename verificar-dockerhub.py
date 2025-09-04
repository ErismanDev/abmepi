#!/usr/bin/env python3
"""
Script para verificar se a configuração Docker Hub está correta
"""

import os
import sys
import subprocess

def verificar_docker():
    """Verifica se Docker está instalado e funcionando"""
    
    print("🐳 VERIFICANDO DOCKER")
    print("=" * 25)
    
    try:
        # Verificar se Docker está instalado
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker instalado: {result.stdout.strip()}")
        
        # Verificar se Docker está rodando
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, check=True)
        print("✅ Docker está rodando")
        
        # Verificar se está logado no Docker Hub
        if 'Username' in result.stdout:
            print("✅ Logado no Docker Hub")
        else:
            print("❌ Não está logado no Docker Hub")
            print("🔑 Execute: docker login")
            return False
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Docker não está instalado ou não está rodando")
        print("📥 Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/")
        return False
    except FileNotFoundError:
        print("❌ Docker não está instalado")
        print("📥 Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/")
        return False

def verificar_arquivos_dockerhub():
    """Verifica se todos os arquivos necessários estão presentes"""
    
    print("\n🔍 VERIFICANDO ARQUIVOS DOCKER HUB")
    print("=" * 40)
    
    arquivos_necessarios = [
        'Dockerfile.dockerhub',
        'docker-compose.dockerhub.yml',
        'deploy-dockerhub.sh',
        'deploy-dockerhub-tags.sh',
        'DEPLOY_DOCKERHUB.md',
        'requirements.txt'
    ]
    
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

def verificar_dockerfile_dockerhub():
    """Verifica se o Dockerfile.dockerhub está correto"""
    
    print("\n🐳 VERIFICANDO DOCKERFILE.DOCKERHUB")
    print("=" * 40)
    
    try:
        with open('Dockerfile.dockerhub', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ('FROM python:', 'Imagem base Python'),
            ('LABEL maintainer=', 'Metadados da imagem'),
            ('LABEL description=', 'Descrição da imagem'),
            ('WORKDIR /app', 'Diretório de trabalho'),
            ('COPY requirements.txt', 'Cópia do requirements'),
            ('RUN pip install', 'Instalação de dependências'),
            ('USER appuser', 'Usuário não-root'),
            ('EXPOSE 8080', 'Porta exposta'),
            ('HEALTHCHECK', 'Health check configurado'),
            ('CMD ["gunicorn"', 'Comando de inicialização')
        ]
        
        for check, desc in verificacoes:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ Dockerfile.dockerhub não encontrado")
        return False
    
    return True

def verificar_docker_compose_dockerhub():
    """Verifica se o docker-compose.dockerhub.yml está correto"""
    
    print("\n🐳 VERIFICANDO DOCKER-COMPOSE.DOCKERHUB")
    print("=" * 45)
    
    try:
        with open('docker-compose.dockerhub.yml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificacoes = [
            ('version:', 'Versão do compose'),
            ('services:', 'Definição de serviços'),
            ('web:', 'Serviço web'),
            ('db:', 'Serviço de banco'),
            ('nginx:', 'Serviço nginx'),
            ('image: erisman/abmepi', 'Imagem do Docker Hub'),
            ('ports:', 'Mapeamento de portas'),
            ('environment:', 'Variáveis de ambiente'),
            ('healthcheck:', 'Health checks configurados')
        ]
        
        for check, desc in verificacoes:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - FALTANDO")
        
    except FileNotFoundError:
        print("❌ docker-compose.dockerhub.yml não encontrado")
        return False
    
    return True

def verificar_scripts_deploy():
    """Verifica se os scripts de deploy estão corretos"""
    
    print("\n🚀 VERIFICANDO SCRIPTS DE DEPLOY")
    print("=" * 35)
    
    scripts = [
        'deploy-dockerhub.sh',
        'deploy-dockerhub-tags.sh'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script}")
            
            # Verificar se é executável
            if os.access(script, os.X_OK):
                print(f"   ✅ Executável")
            else:
                print(f"   ⚠️  Não é executável (execute: chmod +x {script})")
        else:
            print(f"❌ {script} - FALTANDO")
    
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
    
    print("🐳 VERIFICAÇÃO DA CONFIGURAÇÃO DOCKER HUB")
    print("=" * 50)
    
    # Verificar Docker
    docker_ok = verificar_docker()
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos_dockerhub()
    
    # Verificar configurações
    dockerfile_ok = verificar_dockerfile_dockerhub()
    compose_ok = verificar_docker_compose_dockerhub()
    scripts_ok = verificar_scripts_deploy()
    requirements_ok = verificar_requirements()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL")
    print("=" * 50)
    
    if all([docker_ok, arquivos_ok, dockerfile_ok, compose_ok, scripts_ok, requirements_ok]):
        print("✅ CONFIGURAÇÃO DOCKER HUB COMPLETA!")
        print("🚀 Pronto para deploy no Docker Hub")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: chmod +x deploy-dockerhub.sh")
        print("2. Execute: ./deploy-dockerhub.sh")
        print("3. Verifique se a imagem foi enviada")
        print("4. Teste a imagem localmente")
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA!")
        print("🔧 Corrija os problemas antes de fazer o deploy")
    
    print("\n📖 Para mais informações, consulte:")
    print("   - DEPLOY_DOCKERHUB.md")
    print("   - https://hub.docker.com/r/erisman/abmepi")

if __name__ == "__main__":
    main()
