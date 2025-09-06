#!/bin/bash

# Script de Inicialização Rápida - ABMEPI
# Para desenvolvimento local ou teste rápido

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log "🚀 Iniciando configuração rápida do ABMEPI..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    error "Python 3 não está instalado. Instale Python 3.8+ primeiro."
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    error "pip3 não está instalado. Instale pip primeiro."
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    log "Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
log "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
log "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    log "Criando arquivo de configuração .env..."
    cp env.example .env
    warning "Configure as variáveis no arquivo .env antes de continuar!"
    warning "Especialmente: SECRET_KEY, DB_PASSWORD, EMAIL_HOST_PASSWORD"
fi

# Verificar se PostgreSQL está rodando
if ! pg_isready -q; then
    warning "PostgreSQL não está rodando. Iniciando..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
    elif command -v service &> /dev/null; then
        sudo service postgresql start
    else
        error "Não foi possível iniciar o PostgreSQL automaticamente. Inicie manualmente."
    fi
fi

# Criar banco de dados se não existir
log "Verificando banco de dados..."
python manage.py migrate --settings=abmepi.settings

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=abmepi.settings

# Criar superusuário se não existir
log "Verificando superusuário..."
python manage.py shell --settings=abmepi.settings << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@abmepi.org.br', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
EOF

# Criar diretórios necessários
log "Criando diretórios necessários..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Verificar configuração
log "Verificando configuração..."
python manage.py check --settings=abmepi.settings

log "✅ Configuração rápida concluída!"
log ""
log "🌐 Para iniciar o servidor de desenvolvimento:"
log "   source venv/bin/activate"
log "   python manage.py runserver"
log ""
log "👤 Credenciais de acesso:"
log "   Usuário: admin"
log "   Senha: admin123"
log "   URL: http://localhost:8000/admin/"
log ""
log "📝 Próximos passos:"
log "   1. Configure as variáveis no arquivo .env"
log "   2. Execute: python manage.py runserver"
log "   3. Acesse: http://localhost:8000"
log "   4. Para produção, use: ./deploy.sh"
