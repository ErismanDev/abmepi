# 🌊 Deploy no Oceanfile - Guia Completo

## 📋 Pré-requisitos

1. **Conta no Oceanfile** ativa
2. **Docker** instalado localmente (para testes)
3. **Git** configurado
4. **Repositório** no GitHub/GitLab

## 🚀 Passo a Passo para Deploy

### 1. Preparar o Repositório

```bash
# Adicionar todos os arquivos de deploy
git add .
git commit -m "Preparação para deploy em produção"
git push origin main
```

### 2. Configurar no Oceanfile

#### A. Acessar o Painel
1. Faça login no [Oceanfile](https://oceanfile.com)
2. Vá para "Projetos" ou "Aplicações"
3. Clique em "Nova Aplicação"

#### B. Configurar a Aplicação
1. **Nome**: `abmepi`
2. **Tipo**: `Docker Compose`
3. **Repositório**: Seu repositório Git
4. **Branch**: `main`

### 3. Configurar Variáveis de Ambiente

No painel do Oceanfile, vá em "Variáveis de Ambiente" e configure:

```env
# Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.oceanfile.com,localhost,127.0.0.1

# Banco de Dados (Oceanfile fornece automaticamente)
DB_NAME=abmepi
DB_USER=postgres
DB_PASSWORD=senha-fornecida-pelo-oceanfile
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### 4. Configurar o Banco de Dados

1. No painel do Oceanfile, adicione um serviço PostgreSQL
2. Anote as credenciais fornecidas
3. Configure as variáveis de ambiente com essas credenciais

### 5. Deploy

1. Clique em "Deploy" no painel
2. Aguarde o build dos containers
3. Monitore os logs para verificar se tudo está funcionando

## 🔧 Configurações Específicas do Oceanfile

### A. Ajustar docker-compose.yml para Oceanfile

Crie um arquivo `docker-compose.oceanfile.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    restart: unless-stopped
    environment:
      - DEBUG=${DEBUG:-False}
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=${DB_NAME:-abmepi}
      - DB_USER=${DB_USER:-postgres}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=${DB_HOST:-db}
      - DB_PORT=${DB_PORT:-5432}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - EMAIL_HOST=${EMAIL_HOST}
      - EMAIL_PORT=${EMAIL_PORT}
      - EMAIL_USE_TLS=${EMAIL_USE_TLS}
      - EMAIL_HOST_USER=${EMAIL_HOST_USER}
      - EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - logs_volume:/app/logs
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 abmepi.wsgi:application"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.oceanfile.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  static_volume:
  media_volume:
  logs_volume:
```

### B. Configurar Nginx para Oceanfile

Crie um arquivo `nginx.oceanfile.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
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

    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Static files
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Main application
        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }

        # Health check
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 🧪 Testar Localmente Antes do Deploy

### 1. Testar com Docker Compose

```bash
# Usar a configuração específica do Oceanfile
docker-compose -f docker-compose.oceanfile.yml up --build -d

# Verificar se está funcionando
curl http://localhost/health/
```

### 2. Verificar Logs

```bash
# Ver logs da aplicação
docker-compose -f docker-compose.oceanfile.yml logs -f web

# Ver logs do nginx
docker-compose -f docker-compose.oceanfile.yml logs -f nginx
```

## 🔍 Verificações Pós-Deploy

### 1. Verificar se a aplicação está rodando
```bash
# Health check
curl https://seu-dominio.oceanfile.com/health/

# Página principal
curl https://seu-dominio.oceanfile.com/
```

### 2. Verificar banco de dados
- Acesse o painel do Oceanfile
- Vá em "Banco de Dados"
- Verifique se as tabelas foram criadas

### 3. Verificar arquivos estáticos
- Acesse: `https://seu-dominio.oceanfile.com/static/`
- Verifique se os arquivos CSS/JS estão sendo servidos

## 🛠️ Comandos Úteis no Oceanfile

### Via SSH (se disponível)
```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Shell do Django
python manage.py shell
```

### Via Painel Web
- Use o terminal web do Oceanfile
- Execute os comandos Django necessários

## 🚨 Solução de Problemas

### Problema: Aplicação não inicia
1. Verifique os logs no painel do Oceanfile
2. Confirme se todas as variáveis de ambiente estão configuradas
3. Verifique se o banco de dados está acessível

### Problema: Erro 500
1. Verifique se `DEBUG=False` está configurado
2. Confirme se `ALLOWED_HOSTS` inclui o domínio do Oceanfile
3. Verifique os logs da aplicação

### Problema: Arquivos estáticos não carregam
1. Execute `python manage.py collectstatic --noinput`
2. Verifique se o Nginx está servindo os arquivos corretamente

## 📊 Monitoramento

### Logs
- Acesse o painel do Oceanfile
- Vá em "Logs" para ver os logs em tempo real

### Métricas
- Use o painel de métricas do Oceanfile
- Monitore CPU, memória e tráfego

## 🔄 Atualizações

### Para atualizar a aplicação:
1. Faça push das mudanças para o repositório
2. No painel do Oceanfile, clique em "Redeploy"
3. Aguarde o build e deploy

### Para atualizar o banco:
1. Acesse o terminal web
2. Execute: `python manage.py migrate`

## 📞 Suporte

- **Documentação Oceanfile**: Consulte a documentação oficial
- **Logs**: Sempre verifique os logs primeiro
- **Equipe**: Entre em contato com a equipe de desenvolvimento

---

**🌊 Seu projeto ABMEPI estará rodando no Oceanfile!**
