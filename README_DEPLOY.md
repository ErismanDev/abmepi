# 🚀 Guia de Deploy - ABMEPI

Este guia explica como fazer o deploy do sistema ABMEPI em produção usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker (versão 20.10 ou superior)
- Docker Compose (versão 2.0 ou superior)
- Git

## 🔧 Configuração Inicial

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd abmepi
```

### 2. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp env.production.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

### 3. Configure as variáveis obrigatórias no .env:

```env
# Configurações do Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Configurações do Banco de Dados
DB_NAME=abmepi_prod
DB_USER=abmepi_user
DB_PASSWORD=sua-senha-super-segura-aqui
DB_HOST=db
DB_PORT=5432

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-aqui
```

## 🚀 Deploy Automatizado

### Usando o script de deploy (Linux/Mac):
```bash
./deploy.sh
```

### Deploy manual:

#### 1. Construir e iniciar os containers
```bash
docker-compose up --build -d
```

#### 2. Executar migrações
```bash
docker-compose exec web python manage.py migrate
```

#### 3. Coletar arquivos estáticos
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

#### 4. Criar superusuário (opcional)
```bash
docker-compose exec web python manage.py createsuperuser
```

## 🔍 Verificação do Deploy

### Verificar status dos containers:
```bash
docker-compose ps
```

### Ver logs:
```bash
# Todos os serviços
docker-compose logs -f

# Apenas o serviço web
docker-compose logs -f web

# Apenas o banco de dados
docker-compose logs -f db
```

### Testar a aplicação:
```bash
# Health check
curl http://localhost/health/

# Acessar a aplicação
curl http://localhost/
```

## 🛠️ Comandos Úteis

### Parar os serviços:
```bash
docker-compose down
```

### Parar e remover volumes:
```bash
docker-compose down -v
```

### Reconstruir apenas um serviço:
```bash
docker-compose up --build -d web
```

### Executar comandos Django:
```bash
# Shell do Django
docker-compose exec web python manage.py shell

# Criar migrações
docker-compose exec web python manage.py makemigrations

# Executar migrações
docker-compose exec web python manage.py migrate

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup do banco de dados:
```bash
# Criar backup
docker-compose exec db pg_dump -U abmepi_user abmepi_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose exec -T db psql -U abmepi_user abmepi_prod < backup.sql
```

## 🔒 Configurações de Segurança

### 1. SSL/HTTPS
Para habilitar HTTPS, descomente e configure a seção SSL no arquivo `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... resto da configuração
}
```

### 2. Firewall
Configure o firewall para permitir apenas as portas necessárias:
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH)

### 3. Variáveis de ambiente
- Nunca commite o arquivo `.env` no repositório
- Use senhas fortes e únicas
- Rotacione as chaves regularmente

## 📊 Monitoramento

### Logs da aplicação:
```bash
# Logs do Django
docker-compose exec web tail -f /app/logs/abmepi.log

# Logs do Nginx
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

### Monitoramento de recursos:
```bash
# Uso de CPU e memória
docker stats

# Espaço em disco
docker system df
```

## 🔄 Atualizações

### Atualizar a aplicação:
```bash
# 1. Fazer backup do banco
docker-compose exec db pg_dump -U abmepi_user abmepi_prod > backup_antes_atualizacao.sql

# 2. Parar os serviços
docker-compose down

# 3. Atualizar o código
git pull origin main

# 4. Reconstruir e iniciar
docker-compose up --build -d

# 5. Executar migrações
docker-compose exec web python manage.py migrate

# 6. Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

## 🆘 Solução de Problemas

### Container não inicia:
```bash
# Verificar logs
docker-compose logs web

# Verificar configuração
docker-compose config
```

### Erro de banco de dados:
```bash
# Verificar se o banco está rodando
docker-compose exec db pg_isready -U abmepi_user

# Conectar ao banco
docker-compose exec db psql -U abmepi_user abmepi_prod
```

### Erro de permissões:
```bash
# Verificar permissões dos volumes
docker-compose exec web ls -la /app/staticfiles/
docker-compose exec web ls -la /app/media/
```

### Limpar cache do Docker:
```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Remover volumes não utilizados
docker volume prune

# Limpeza completa
docker system prune -a
```

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o deploy:
- Consulte os logs da aplicação
- Verifique a documentação do Django
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ para a ABMEPI**
