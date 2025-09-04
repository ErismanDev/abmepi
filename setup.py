#!/usr/bin/env python3
"""
Script de configuração e inicialização do projeto ABMEPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído com sucesso!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {description.lower()}:")
        print(f"Comando: {command}")
        print(f"Erro: {e.stderr}")
        return False


def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
    return True


def check_postgresql():
    """Verifica se o PostgreSQL está disponível"""
    print("\n🐘 Verificando PostgreSQL...")
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL encontrado!")
            return True
        else:
            print("❌ PostgreSQL não encontrado!")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL não está instalado ou não está no PATH!")
        return False


def create_virtual_environment():
    """Cria ambiente virtual Python"""
    if os.path.exists('venv'):
        print("✅ Ambiente virtual já existe!")
        return True
    
    return run_command('python -m venv venv', 'Criando ambiente virtual')


def install_dependencies():
    """Instala as dependências do projeto"""
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip'
    else:  # Linux/Mac
        pip_cmd = 'venv/bin/pip'
    
    return run_command(f'{pip_cmd} install -r requirements.txt', 'Instalando dependências')


def create_env_file():
    """Cria arquivo .env se não existir"""
    if os.path.exists('.env'):
        print("✅ Arquivo .env já existe!")
        return True
    
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("✅ Arquivo .env criado a partir do env.example")
        print("⚠️  Lembre-se de configurar as variáveis de ambiente!")
        return True
    
    print("❌ Arquivo env.example não encontrado!")
    return False


def create_directories():
    """Cria diretórios necessários"""
    directories = ['static', 'media', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Diretórios criados!")
    return True


def run_migrations():
    """Executa as migrações do Django"""
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python'
    else:  # Linux/Mac
        python_cmd = 'venv/bin/python'
    
    # Verifica se o banco está configurado
    if not check_database_connection(python_cmd):
        print("⚠️  Configure o banco de dados antes de executar as migrações!")
        return False
    
    success = run_command(f'{python_cmd} manage.py makemigrations', 'Criando migrações')
    if success:
        success = run_command(f'{python_cmd} manage.py migrate', 'Executando migrações')
    
    return success


def check_database_connection(python_cmd):
    """Verifica a conexão com o banco de dados"""
    try:
        result = subprocess.run(
            f'{python_cmd} manage.py check --database default',
            shell=True, capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False


def create_superuser():
    """Cria superusuário se solicitado"""
    response = input("\n🤔 Deseja criar um superusuário? (s/n): ").lower().strip()
    
    if response in ['s', 'sim', 'y', 'yes']:
        if os.name == 'nt':  # Windows
            python_cmd = 'venv\\Scripts\\python'
        else:  # Linux/Mac
            python_cmd = 'venv/bin/python'
        
        return run_command(f'{python_cmd} manage.py createsuperuser', 'Criando superusuário')
    
    return True


def collect_static():
    """Coleta arquivos estáticos"""
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python'
    else:  # Linux/Mac
        python_cmd = 'venv/bin/python'
    
    return run_command(f'{python_cmd} manage.py collectstatic --noinput', 'Coletando arquivos estáticos')


def main():
    """Função principal"""
    print("🚀 Configurando projeto ABMEPI...")
    print("=" * 50)
    
    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)
    
    if not check_postgresql():
        print("⚠️  PostgreSQL não encontrado. Configure-o antes de continuar.")
        response = input("Deseja continuar mesmo assim? (s/n): ").lower().strip()
        if response not in ['s', 'sim', 'y', 'yes']:
            sys.exit(1)
    
    # Configuração do projeto
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not create_env_file():
        sys.exit(1)
    
    if not create_directories():
        sys.exit(1)
    
    # Configuração do Django
    if not run_migrations():
        print("⚠️  Migrações não executadas. Configure o banco de dados primeiro.")
    
    if not create_superuser():
        sys.exit(1)
    
    if not collect_static():
        print("⚠️  Arquivos estáticos não coletados.")
    
    print("\n" + "=" * 50)
    print("🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Configure o arquivo .env com suas credenciais do banco")
    print("2. Execute: python manage.py runserver")
    print("3. Acesse: http://localhost:8000")
    print("\n📚 Para mais informações, consulte o README.md")
    
    # Instruções para ativar o ambiente virtual
    if os.name == 'nt':  # Windows
        print("\n💡 Para ativar o ambiente virtual:")
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("\n💡 Para ativar o ambiente virtual:")
        print("   source venv/bin/activate")


if __name__ == '__main__':
    main()
