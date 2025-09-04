# 🐳 Guia Completo de Deploy Docker para DigitalOcean

## 🎯 **Objetivo**
Fazer deploy da aplicação ABMEPI usando Docker no DigitalOcean App Platform.

## 📋 **Arquivos Criados**

### **Configuração Docker**
- ✅ `Dockerfile` - Imagem da aplicação
- ✅ `docker-compose.yml` - Orquestração dos serviços
- ✅ `nginx.conf` - Configuração do proxy reverso
- ✅ `.dockerignore` - Arquivos ignorados no build
- ✅ `env.docker` - Variáveis de ambiente

### **Deploy e Scripts**
- ✅ `deploy-docker.sh` - Script de deploy local
- ✅ `deploy-digitalocean.sh` - Script de deploy no DigitalOcean
- ✅ `verificar-docker.py` - Verificação da configuração
- ✅ `.do/app.yaml` - Configuração do App Platform

### **Documentação**
- ✅ `DEPLOY_DOCKER_DIGITALOCEAN.md` - Guia detalhado
- ✅ `CONFIGURACOES_DIGITALOCEAN.txt` - Variáveis de ambiente

## 🚀 **Passos para Deploy**

### **1. Preparar o Repositório**
```bash
# Verificar se todos os arquivos estão presentes
python verificar-docker.py
```

### **2. Configurar no DigitalOcean**

#### **A. Via Painel Web (Recomendado)**
1. Acesse: https://cloud.digitalocean.com/apps
2. Clique em "Create App"
3. Conecte seu repositório GitHub
4. Configure as variáveis de ambiente (veja `CONFIGURACOES_DIGITALOCEAN.txt`)
5. Faça o deploy

#### **B. Via CLI (Avançado)**
```bash
# Instalar doctl
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Autenticar
doctl auth init

# Criar app
doctl apps create --spec .do/app.yaml

# Fazer deploy
./deploy-digitalocean.sh
```

### **3. Variáveis de Ambiente Obrigatórias**

```bash
SECRET_KEY=#&%6t2x3b7i&8b+5gd@ucxfel1t#z12(+)!idj8@b)91kept%t
DEBUG=False
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1
DIGITALOCEAN_APP_PLATFORM=True
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=siteabmepi@gmail.com
EMAIL_HOST_PASSWORD=tlvt twcz livv zetu
DEFAULT_FROM_EMAIL=siteabmepi@gmail.com
SERVER_EMAIL=siteabmepi@gmail.com
```

## 🐳 **Estrutura Docker**

### **Serviços**
- **Web**: Django + Gunicorn (porta 8080)
- **Database**: PostgreSQL 15
- **Nginx**: Proxy reverso (portas 80/443)

### **Volumes**
- `postgres_data`: Dados do banco
- `static_volume`: Arquivos estáticos
- `media_volume`: Arquivos de mídia

### **Rede**
- Todos os serviços na mesma rede Docker
- Comunicação interna via nomes dos serviços

## 🔧 **Configurações Específicas**

### **Dockerfile**
- Base: Python 3.11-slim
- Usuário não-root para segurança
- Otimização de layers para cache
- Coleta de arquivos estáticos

### **Docker Compose**
- Orquestração de 3 serviços
- Variáveis de ambiente externas
- Volumes persistentes
- Restart automático

### **Nginx**
- Proxy reverso para Django
- Servir arquivos estáticos
- Compressão Gzip
- Rate limiting
- Headers de segurança

## 📊 **Monitoramento**

### **Health Checks**
- Endpoint: `/health/`
- Intervalo: 10 segundos
- Timeout: 5 segundos
- Threshold: 3 falhas

### **Logs**
- Application logs
- Build logs
- Runtime logs
- Error logs

### **Métricas**
- CPU usage
- Memory usage
- Response time
- Error rate

## 🚨 **Troubleshooting**

### **Erro 400 Bad Request**
```bash
# Verificar ALLOWED_HOSTS
echo $ALLOWED_HOSTS

# Verificar SECURE_SSL_REDIRECT
echo $SECURE_SSL_REDIRECT
```

### **Erro de Conexão com Banco**
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Verificar se PostgreSQL está rodando
docker-compose ps db
```

### **Erro de Arquivos Estáticos**
```bash
# Verificar collectstatic
docker-compose exec web python manage.py collectstatic --noinput

# Verificar permissões
docker-compose exec web ls -la staticfiles/
```

## 🎯 **Resultado Esperado**

Após o deploy bem-sucedido:
- ✅ Aplicação acessível via HTTPS
- ✅ Banco de dados conectado
- ✅ Arquivos estáticos servidos
- ✅ SSL funcionando
- ✅ Performance otimizada
- ✅ Logs centralizados
- ✅ Monitoramento ativo

## 📞 **Suporte**

### **Recursos Úteis**
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)

### **Comandos de Emergência**
```bash
# Parar todos os containers
docker-compose down

# Ver logs em tempo real
docker-compose logs -f

# Reconstruir tudo
docker-compose build --no-cache

# Reset completo
docker-compose down -v
docker system prune -a
```

## 🏆 **Conclusão**

A configuração Docker está completa e pronta para deploy no DigitalOcean! 

**Próximos passos:**
1. Configure as variáveis de ambiente no painel
2. Faça o deploy da aplicação
3. Verifique se está funcionando
4. Monitore os logs e métricas

**Boa sorte com o deploy! 🚀**
