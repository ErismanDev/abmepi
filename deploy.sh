#!/bin/bash

<<<<<<< HEAD
# Script de Deploy para Digital Ocean - ABMEPI
# Execute este script no servidor Digital Ocean

set -e

echo "🚀 Iniciando deploy do ABMEPI no Digital Ocean..."

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

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    error "Não execute este script como root. Use um usuário com sudo."
fi

# Atualizar sistema
log "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
log "Instalando dependências do sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    wget \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Instalar Docker
log "Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
log "Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configurar PostgreSQL
log "Configurando PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco de dados
sudo -u postgres psql -c "CREATE USER abmepi_user WITH PASSWORD 'Abmepi2024!';"
sudo -u postgres psql -c "CREATE DATABASE abmepi_prod OWNER abmepi_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE abmepi_prod TO abmepi_user;"

# Configurar firewall
log "Configurando firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Criar diretório do projeto
PROJECT_DIR="/opt/abmepi"
log "Criando diretório do projeto em $PROJECT_DIR..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Copiar arquivos do projeto (assumindo que já estão no servidor)
log "Copiando arquivos do projeto..."
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# Criar arquivo .env
log "Criando arquivo de configuração..."
cat > .env << EOF
# Configurações de Produção - ABMEPI
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s ifconfig.me),$(hostname)

# Configurações do Banco de Dados PostgreSQL
DB_NAME=abmepi_prod
DB_USER=abmepi_user
DB_PASSWORD=Abmepi2024!
DB_HOST=localhost
DB_PORT=5432

# Configurações de Email (configure com seus dados)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=noreply@abmepi.org.br
SERVER_EMAIL=noreply@abmepi.org.br
ADMIN_EMAIL=admin@abmepi.org.br

# Configurações de Senha Padrão
SENHA_PADRAO_USUARIO=Abmepi2024!
EOF

# Criar ambiente virtual Python
log "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
log "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Executar migrações
log "Executando migrações do banco de dados..."
python manage.py migrate --settings=abmepi.settings_production

# Criar superusuário
log "Criando superusuário..."
python manage.py createsuperuser --settings=abmepi.settings_production || warning "Superusuário já existe ou erro na criação"

# Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=abmepi.settings_production

# Configurar Nginx
log "Configurando Nginx..."
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Criar serviço systemd para a aplicação
log "Criando serviço systemd..."
sudo tee /etc/systemd/system/abmepi.service > /dev/null << EOF
[Unit]
Description=ABMEPI Django Application
After=network.target postgresql.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 abmepi.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable abmepi
sudo systemctl start abmepi

# Verificar status dos serviços
log "Verificando status dos serviços..."
sudo systemctl status postgresql --no-pager
sudo systemctl status nginx --no-pager
sudo systemctl status abmepi --no-pager

# Configurar backup automático
log "Configurando backup automático..."
sudo tee /etc/cron.daily/abmepi-backup > /dev/null << EOF
#!/bin/bash
# Backup do banco de dados ABMEPI
BACKUP_DIR="/opt/backups/abmepi"
mkdir -p \$BACKUP_DIR
cd $PROJECT_DIR
source venv/bin/activate
python manage.py dumpdata --settings=abmepi.settings_production > \$BACKUP_DIR/abmepi_\$(date +%Y%m%d_%H%M%S).json
# Manter apenas os últimos 7 backups
find \$BACKUP_DIR -name "abmepi_*.json" -mtime +7 -delete
EOF

sudo chmod +x /etc/cron.daily/abmepi-backup

# Criar diretório de backups
sudo mkdir -p /opt/backups/abmepi
sudo chown $USER:$USER /opt/backups/abmepi

log "✅ Deploy concluído com sucesso!"
log "🌐 Aplicação disponível em: http://$(curl -s ifconfig.me)"
log "📊 Status dos serviços:"
echo "   - PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "   - Nginx: $(sudo systemctl is-active nginx)"
echo "   - ABMEPI: $(sudo systemctl is-active abmepi)"

log "📝 Próximos passos:"
echo "   1. Configure o domínio no Digital Ocean"
echo "   2. Configure SSL/TLS (Let's Encrypt)"
echo "   3. Configure as credenciais de email no arquivo .env"
echo "   4. Acesse http://$(curl -s ifconfig.me)/admin/ para configurar o sistema"

warning "⚠️  IMPORTANTE: Configure as credenciais de email no arquivo .env antes de usar o sistema!"
=======
# Script de Deploy para ABMEPI
# Este script automatiza o processo de deploy em produção

set -e

echo "🚀 Iniciando deploy do ABMEPI..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando do exemplo..."
    if [ -f env.production.example ]; then
        cp env.production.example .env
        echo "📝 Arquivo .env criado. Configure as variáveis antes de continuar."
        echo "   Edite o arquivo .env com suas configurações de produção."
        exit 1
    else
        echo "❌ Arquivo env.production.example não encontrado."
        exit 1
    fi
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional)
read -p "🗑️  Deseja remover imagens antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removendo imagens antigas..."
    docker-compose down --rmi all
fi

# Construir e iniciar os containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar o banco de dados estar pronto
echo "⏳ Aguardando banco de dados..."
sleep 10

# Executar migrações
echo "📊 Executando migrações..."
docker-compose exec web python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput

# Criar superusuário (opcional)
read -p "👤 Deseja criar um superusuário? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "👤 Criando superusuário..."
    docker-compose exec web python manage.py createsuperuser
fi

# Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker-compose ps

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: http://localhost"
echo "📊 Para ver logs: docker-compose logs -f"
echo "🛑 Para parar: docker-compose down"
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
