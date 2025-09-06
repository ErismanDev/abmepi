# Script de Deploy para Digital Ocean - ABMEPI (PowerShell)
# Execute este script no servidor Digital Ocean via PowerShell

param(
    [string]$Domain = "",
    [string]$Email = "admin@abmepi.org.br"
)

# Configurações
$ErrorActionPreference = "Stop"
$ProjectDir = "/opt/abmepi"
$BackupDir = "/opt/backups/abmepi"

# Função para log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

Write-Log "🚀 Iniciando deploy do ABMEPI no Digital Ocean..." "SUCCESS"

try {
    # Verificar se está rodando como root
    if ($env:USER -eq "root") {
        Write-Log "Não execute este script como root. Use um usuário com sudo." "ERROR"
        exit 1
    }

    # Atualizar sistema
    Write-Log "Atualizando sistema..."
    sudo apt update
    sudo apt upgrade -y

    # Instalar dependências do sistema
    Write-Log "Instalando dependências do sistema..."
    $packages = @(
        "python3", "python3-pip", "python3-venv", "postgresql", "postgresql-contrib",
        "nginx", "git", "curl", "wget", "unzip", "software-properties-common",
        "apt-transport-https", "ca-certificates", "gnupg", "lsb-release"
    )
    sudo apt install -y $packages

    # Instalar Docker
    Write-Log "Instalando Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    $dockerRepo = "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    echo $dockerRepo | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $env:USER

    # Instalar Docker Compose
    Write-Log "Instalando Docker Compose..."
    $dockerComposeUrl = "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
    sudo curl -L $dockerComposeUrl -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    # Configurar PostgreSQL
    Write-Log "Configurando PostgreSQL..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql

    # Criar usuário e banco de dados
    sudo -u postgres psql -c "CREATE USER abmepi_user WITH PASSWORD 'Abmepi2024!';"
    sudo -u postgres psql -c "CREATE DATABASE abmepi_prod OWNER abmepi_user;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE abmepi_prod TO abmepi_user;"

    # Configurar firewall
    Write-Log "Configurando firewall..."
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable

    # Criar diretório do projeto
    Write-Log "Criando diretório do projeto em $ProjectDir..."
    sudo mkdir -p $ProjectDir
    sudo chown $env:USER:$env:USER $ProjectDir

    # Copiar arquivos do projeto (assumindo que já estão no servidor)
    Write-Log "Copiando arquivos do projeto..."
    Copy-Item -Path "." -Destination $ProjectDir -Recurse -Force
    Set-Location $ProjectDir

    # Criar arquivo .env
    Write-Log "Criando arquivo de configuração..."
    $secretKey = python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    $publicIp = (Invoke-WebRequest -Uri "https://ifconfig.me" -UseBasicParsing).Content.Trim()
    $hostname = hostname

    $envContent = @"
# Configurações de Produção - ABMEPI
SECRET_KEY=$secretKey
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$publicIp,$hostname

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
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8

    # Criar ambiente virtual Python
    Write-Log "Criando ambiente virtual Python..."
    python3 -m venv venv
    & "./venv/bin/activate"

    # Instalar dependências Python
    Write-Log "Instalando dependências Python..."
    pip install --upgrade pip
    pip install -r requirements.txt

    # Executar migrações
    Write-Log "Executando migrações do banco de dados..."
    python manage.py migrate --settings=abmepi.settings_production

    # Criar superusuário
    Write-Log "Criando superusuário..."
    try {
        python manage.py createsuperuser --settings=abmepi.settings_production
    } catch {
        Write-Log "Superusuário já existe ou erro na criação" "WARNING"
    }

    # Coletar arquivos estáticos
    Write-Log "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --settings=abmepi.settings_production

    # Configurar Nginx
    Write-Log "Configurando Nginx..."
    Copy-Item "nginx.conf" "/etc/nginx/nginx.conf"
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx

    # Criar serviço systemd para a aplicação
    Write-Log "Criando serviço systemd..."
    $serviceContent = @"
[Unit]
Description=ABMEPI Django Application
After=network.target postgresql.service

[Service]
Type=exec
User=$env:USER
Group=$env:USER
WorkingDirectory=$ProjectDir
Environment=PATH=$ProjectDir/venv/bin
ExecStart=$ProjectDir/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 abmepi.wsgi:application
ExecReload=/bin/kill -s HUP `$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

    $serviceContent | sudo tee /etc/systemd/system/abmepi.service > /dev/null

    # Recarregar systemd e iniciar serviço
    sudo systemctl daemon-reload
    sudo systemctl enable abmepi
    sudo systemctl start abmepi

    # Verificar status dos serviços
    Write-Log "Verificando status dos serviços..."
    sudo systemctl status postgresql --no-pager
    sudo systemctl status nginx --no-pager
    sudo systemctl status abmepi --no-pager

    # Configurar backup automático
    Write-Log "Configurando backup automático..."
    $backupScript = @"
#!/bin/bash
# Backup do banco de dados ABMEPI
BACKUP_DIR="/opt/backups/abmepi"
mkdir -p `$BACKUP_DIR
cd $ProjectDir
source venv/bin/activate
python manage.py dumpdata --settings=abmepi.settings_production > `$BACKUP_DIR/abmepi_`$(date +%Y%m%d_%H%M%S).json
# Manter apenas os últimos 7 backups
find `$BACKUP_DIR -name "abmepi_*.json" -mtime +7 -delete
"@

    $backupScript | sudo tee /etc/cron.daily/abmepi-backup > /dev/null
    sudo chmod +x /etc/cron.daily/abmepi-backup

    # Criar diretório de backups
    sudo mkdir -p $BackupDir
    sudo chown $env:USER:$env:USER $BackupDir

    Write-Log "✅ Deploy concluído com sucesso!" "SUCCESS"
    Write-Log "🌐 Aplicação disponível em: http://$publicIp" "SUCCESS"
    Write-Log "📊 Status dos serviços:" "SUCCESS"
    Write-Host "   - PostgreSQL: $(sudo systemctl is-active postgresql)"
    Write-Host "   - Nginx: $(sudo systemctl is-active nginx)"
    Write-Host "   - ABMEPI: $(sudo systemctl is-active abmepi)"

    Write-Log "📝 Próximos passos:" "SUCCESS"
    Write-Host "   1. Configure o domínio no Digital Ocean"
    Write-Host "   2. Configure SSL/TLS (Let's Encrypt)"
    Write-Host "   3. Configure as credenciais de email no arquivo .env"
    Write-Host "   4. Acesse http://$publicIp/admin/ para configurar o sistema"

    Write-Log "⚠️  IMPORTANTE: Configure as credenciais de email no arquivo .env antes de usar o sistema!" "WARNING"

} catch {
    Write-Log "Erro durante o deploy: $($_.Exception.Message)" "ERROR"
    exit 1
}
