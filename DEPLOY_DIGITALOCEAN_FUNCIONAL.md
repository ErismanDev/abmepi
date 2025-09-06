# 🚀 Deploy Funcional no DigitalOcean - Guia Completo

## ✅ Configurações Realizadas

### 1. **Variáveis de Ambiente Configuradas**
- ✅ `env.digitalocean.example` criado
- ✅ Configurações específicas para DigitalOcean
- ✅ Segurança SSL configurada

### 2. **Settings.py Ajustado**
- ✅ Suporte a `dj-database-url` para DATABASE_URL
- ✅ Configurações específicas para DigitalOcean App Platform
- ✅ SSL redirect configurado para load balancer
- ✅ Fallback para configuração manual

### 3. **Pacotes Instalados**
- ✅ `dj-database-url==2.1.0`
- ✅ `gunicorn==21.2.0`
- ✅ `psycopg2-binary==2.9.9`

### 4. **Requirements.txt Atualizado**
- ✅ Todas as dependências incluídas
- ✅ Versões específicas definidas

### 5. **Configurações Docker**
- ✅ `Dockerfile.digitalocean` otimizado
- ✅ Porta 8080 para DigitalOcean
- ✅ Health check configurado

## 🚀 Como Fazer o Deploy

### Opção 1: Via DigitalOcean App Platform (Recomendado)

1. **Acesse o DigitalOcean App Platform**
2. **Crie uma nova aplicação**
3. **Conecte o repositório GitHub**: `ErismanDev/abmepi`
4. **Use o arquivo de configuração**: `.do/app.yaml`
5. **Configure as variáveis de ambiente** (veja abaixo)
6. **Adicione banco PostgreSQL**
7. **Faça o deploy**

### Opção 2: Via Docker Compose

1. **Use o arquivo**: `docker-compose.digitalocean.yml`
2. **Configure as variáveis de ambiente**
3. **Deploy via DigitalOcean Droplet**

## ⚙️ Variáveis de Ambiente Essenciais

### No Painel do DigitalOcean, configure:

```env
# Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1

# DigitalOcean App Platform
DIGITALOCEAN_APP_PLATFORM=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=siteabmepi@gmail.com
EMAIL_HOST_PASSWORD=tlvt twcz livv zetu
DEFAULT_FROM_EMAIL=siteabmepi@gmail.com
SERVER_EMAIL=siteabmepi@gmail.com
```

## 🗄️ Configuração do Banco de Dados

### DigitalOcean App Platform:
- O banco será criado automaticamente via `.do/app.yaml`
- A variável `DATABASE_URL` será configurada automaticamente

### Docker Compose:
- Configure as variáveis `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## 🔧 Comandos de Deploy

### 1. Commit e Push das Mudanças
```bash
git add .
git commit -m "Configuração funcional para DigitalOcean"
git push origin master
```

### 2. Deploy via App Platform
1. Acesse o painel do DigitalOcean
2. Crie nova aplicação
3. Conecte o repositório
4. Use o arquivo `.do/app.yaml`
5. Configure as variáveis de ambiente
6. Deploy

### 3. Verificação Pós-Deploy
```bash
# Health check
curl https://lobster-app-pqkby.ondigitalocean.app/health/

# Página principal
curl https://lobster-app-pqkby.ondigitalocean.app/
```

## 🛠️ Comandos de Manutenção

### Via Terminal do DigitalOcean:
```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar configurações
python manage.py check --deploy
```

## 📊 Monitoramento

### Logs:
- Acesse o painel do DigitalOcean
- Vá em "Logs" da aplicação
- Monitore em tempo real

### Métricas:
- CPU, memória e tráfego
- Status do banco de dados
- Performance da aplicação

## 🚨 Solução de Problemas

### Erro 400 (Bad Request):
- Verifique `ALLOWED_HOSTS`
- Confirme `SECRET_KEY`
- Verifique logs da aplicação

### Erro de Banco de Dados:
- Confirme `DATABASE_URL`
- Verifique se o banco está rodando
- Execute migrações

### Erro de Arquivos Estáticos:
- Execute `collectstatic`
- Verifique configuração do WhiteNoise

## 🎯 Resultado Esperado

Após o deploy bem-sucedido:
- ✅ Aplicação acessível em `https://lobster-app-pqkby.ondigitalocean.app/`
- ✅ Health check funcionando: `/health/`
- ✅ Página de login da ABMEPI
- ✅ Banco de dados conectado
- ✅ Arquivos estáticos servidos
- ✅ SSL funcionando

## 📞 Suporte

Para problemas:
1. Verifique os logs no painel do DigitalOcean
2. Confirme todas as variáveis de ambiente
3. Teste a conectividade do banco
4. Entre em contato com a equipe de desenvolvimento

---

**🚀 Sua aplicação ABMEPI está pronta para deploy funcional no DigitalOcean!**
