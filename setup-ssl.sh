#!/bin/bash

# Script para configurar SSL/TLS com Let's Encrypt - ABMEPI
# Execute este script após configurar o domínio

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

# Verificar se o domínio foi fornecido
if [ -z "$1" ]; then
    error "Uso: $0 <dominio> [email]"
    echo "Exemplo: $0 abmepi.org.br admin@abmepi.org.br"
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

log "Configurando SSL para o domínio: $DOMAIN"
log "Email para notificações: $EMAIL"

# Instalar Certbot
log "Instalando Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Parar Nginx temporariamente
log "Parando Nginx..."
sudo systemctl stop nginx

# Obter certificado SSL
log "Obtendo certificado SSL..."
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

# Criar diretório para certificados
sudo mkdir -p /etc/nginx/ssl

# Copiar certificados
log "Copiando certificados..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/nginx/ssl/key.pem
sudo chmod 644 /etc/nginx/ssl/cert.pem
sudo chmod 600 /etc/nginx/ssl/key.pem

# Atualizar configuração do Nginx
log "Atualizando configuração do Nginx..."
sudo tee /etc/nginx/nginx.conf > /dev/null << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

    # Upstream
    upstream django {
        server 127.0.0.1:8000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;
        
        # Redirect all HTTP requests to HTTPS
        return 301 https://\$host\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN www.$DOMAIN;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Client max body size
        client_max_body_size 20M;

        # Static files
        location /static/ {
            alias /opt/abmepi/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /opt/abmepi/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header Host \$host;
            proxy_redirect off;
        }

        # Login rate limiting
        location /login/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://django;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header Host \$host;
            proxy_redirect off;
        }

        # Main application
        location / {
            proxy_pass http://django;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header Host \$host;
            proxy_redirect off;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Testar configuração do Nginx
log "Testando configuração do Nginx..."
sudo nginx -t

# Iniciar Nginx
log "Iniciando Nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Configurar renovação automática do certificado
log "Configurando renovação automática..."
sudo tee /etc/cron.d/certbot-renew > /dev/null << EOF
# Renovar certificados SSL automaticamente
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Atualizar arquivo .env com o domínio
log "Atualizando configuração com o domínio..."
cd /opt/abmepi
sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN,www.$DOMAIN/" .env

# Reiniciar aplicação
log "Reiniciando aplicação..."
sudo systemctl restart abmepi

# Verificar status
log "Verificando status dos serviços..."
sudo systemctl status nginx --no-pager
sudo systemctl status abmepi --no-pager

log "✅ SSL configurado com sucesso!"
log "🌐 Aplicação disponível em: https://$DOMAIN"
log "🔒 Certificado SSL válido até: $(sudo certbot certificates | grep "Expiry Date" | head -1 | awk '{print $3, $4, $5}')"

log "📝 Próximos passos:"
echo "   1. Acesse https://$DOMAIN para verificar se está funcionando"
echo "   2. Configure o DNS do seu domínio para apontar para este servidor"
echo "   3. Teste todas as funcionalidades da aplicação"
echo "   4. Configure backup automático dos certificados SSL"
