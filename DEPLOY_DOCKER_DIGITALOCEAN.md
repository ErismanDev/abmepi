# 🐳 Deploy Docker para DigitalOcean

## 📋 **Pré-requisitos**

- ✅ Docker instalado
- ✅ Docker Compose instalado
- ✅ Conta no DigitalOcean
- ✅ Aplicação configurada no App Platform

## 🚀 **Passos para Deploy**

### 1. **Preparar o Projeto**

```bash
# Verificar se todos os arquivos estão presentes
ls -la | grep -E "(Dockerfile|docker-compose|nginx.conf|.dockerignore)"
```

### 2. **Configurar Variáveis de Ambiente**

No painel do DigitalOcean, adicione estas variáveis:

```
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

### 3. **Testar Localmente (Opcional)**

```bash
# Tornar script executável
chmod +x deploy-docker.sh

# Executar deploy local
./deploy-docker.sh
```

### 4. **Deploy no DigitalOcean**

1. **Acesse o painel**: https://cloud.digitalocean.com/apps
2. **Clique na sua aplicação** ABMEPI
3. **Vá em "Settings"** → "App-Level Environment Variables"
4. **Adicione todas as variáveis** listadas acima
5. **Vá em "Actions"** → "Force Rebuild and Deploy"

## 🔧 **Configuração do App Platform**

### **Source Code**
- **Source Type**: GitHub
- **Repository**: Seu repositório
- **Branch**: main/master

### **Build & Deploy**
- **Build Command**: `docker build -t abmepi .`
- **Run Command**: `docker run -p 8080:8080 abmepi`
- **Port**: 8080

### **Environment Variables**
- Adicione todas as variáveis listadas acima
- Marque "Encrypt" para SECRET_KEY e senhas

## 📊 **Estrutura Docker**

```
abmepi/
├── Dockerfile              # Imagem da aplicação
├── docker-compose.yml      # Orquestração dos serviços
├── nginx.conf              # Configuração do Nginx
├── .dockerignore           # Arquivos ignorados
├── env.docker              # Variáveis de ambiente
├── deploy-docker.sh        # Script de deploy
└── requirements.txt        # Dependências Python
```

## 🐳 **Serviços Docker**

### **Web (Django)**
- **Porta**: 8080
- **Imagem**: Python 3.11-slim
- **Comando**: Gunicorn com 3 workers

### **Database (PostgreSQL)**
- **Porta**: 5432
- **Imagem**: PostgreSQL 15
- **Volume**: Persistência de dados

### **Nginx (Proxy)**
- **Porta**: 80/443
- **Imagem**: Nginx Alpine
- **Função**: Proxy reverso e arquivos estáticos

## 🔍 **Verificação Pós-Deploy**

### **Health Checks**
```bash
# Verificar se a aplicação está rodando
curl https://lobster-app-pqkby.ondigitalocean.app/health/

# Verificar página principal
curl https://lobster-app-pqkby.ondigitalocean.app/
```

### **Logs**
```bash
# Ver logs no painel do DigitalOcean
# Ou via CLI (se configurado)
doctl apps logs <app-id>
```

## 🛠️ **Comandos Úteis**

### **Local**
```bash
# Construir imagem
docker build -t abmepi .

# Executar container
docker run -p 8080:8080 abmepi

# Ver logs
docker logs <container-id>

# Entrar no container
docker exec -it <container-id> bash
```

### **Docker Compose**
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir
docker-compose build --no-cache
```

## 🚨 **Troubleshooting**

### **Erro 400 Bad Request**
- ✅ Verificar ALLOWED_HOSTS
- ✅ Verificar SECURE_SSL_REDIRECT
- ✅ Verificar variáveis de ambiente

### **Erro de Conexão com Banco**
- ✅ Verificar DATABASE_URL
- ✅ Verificar se PostgreSQL está rodando
- ✅ Verificar credenciais

### **Erro de Arquivos Estáticos**
- ✅ Verificar collectstatic
- ✅ Verificar configuração do Nginx
- ✅ Verificar permissões

## 📈 **Monitoramento**

### **Métricas Importantes**
- CPU Usage
- Memory Usage
- Response Time
- Error Rate

### **Logs Importantes**
- Application logs
- Nginx access logs
- Database logs
- Build logs

## 🎯 **Resultado Esperado**

Após o deploy bem-sucedido:
- ✅ Aplicação acessível via HTTPS
- ✅ Banco de dados conectado
- ✅ Arquivos estáticos servidos
- ✅ SSL funcionando
- ✅ Performance otimizada

## 📞 **Suporte**

Se houver problemas:
1. Verificar logs no painel do DigitalOcean
2. Verificar variáveis de ambiente
3. Verificar configuração do Docker
4. Verificar conectividade de rede
