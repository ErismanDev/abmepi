# 🐳 Deploy no Docker Hub - ABMEPI

## 📋 **Pré-requisitos**

- ✅ Docker instalado
- ✅ Conta no Docker Hub
- ✅ Login no Docker Hub
- ✅ Repositório criado no Docker Hub

## 🚀 **Passos para Deploy**

### 1. **Preparar o Ambiente**

```bash
# Verificar se Docker está instalado
docker --version

# Fazer login no Docker Hub
docker login
# Usuário: erisman
# Senha: [sua senha]
```

### 2. **Construir e Fazer Push da Imagem**

#### **Opção A: Deploy Simples**
```bash
# Executar script de deploy
chmod +x deploy-dockerhub.sh
./deploy-dockerhub.sh
```

#### **Opção B: Deploy com Tags Específicas**
```bash
# Executar script com tags
chmod +x deploy-dockerhub-tags.sh
./deploy-dockerhub-tags.sh
```

#### **Opção C: Deploy Manual**
```bash
# Construir imagem
docker build -t erisman/abmepi:latest .

# Fazer push
docker push erisman/abmepi:latest

# Criar tags adicionais
docker tag erisman/abmepi:latest erisman/abmepi:v1.0
docker tag erisman/abmepi:latest erisman/abmepi:production
docker tag erisman/abmepi:latest erisman/abmepi:stable

# Fazer push das tags
docker push erisman/abmepi:v1.0
docker push erisman/abmepi:production
docker push erisman/abmepi:stable
```

### 3. **Usar a Imagem**

#### **Docker Run Simples**
```bash
# Baixar e executar
docker pull erisman/abmepi:latest
docker run -p 8080:8080 erisman/abmepi:latest
```

#### **Docker Compose**
```bash
# Usar docker-compose
docker-compose -f docker-compose.dockerhub.yml up -d
```

## 🏷️ **Tags Disponíveis**

- `latest` - Versão mais recente
- `v1.0` - Versão 1.0
- `production` - Versão de produção
- `stable` - Versão estável

## 🔧 **Configuração**

### **Variáveis de Ambiente**
```bash
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:port/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com
```

### **Portas**
- **8080** - Aplicação Django
- **80** - Nginx (HTTP)
- **443** - Nginx (HTTPS)

## 📊 **Estrutura da Imagem**

### **Base**
- Python 3.11-slim
- Debian-based

### **Dependências**
- PostgreSQL client
- Build tools
- Curl (para health checks)

### **Usuário**
- Não-root (appuser)
- Segurança aprimorada

### **Health Check**
- Endpoint: `/health/`
- Intervalo: 30s
- Timeout: 30s
- Retries: 3

## 🌐 **Acesso**

### **Docker Hub**
- **Repositório**: https://hub.docker.com/r/erisman/abmepi
- **Tags**: latest, v1.0, production, stable

### **Comandos de Pull**
```bash
# Versão mais recente
docker pull erisman/abmepi:latest

# Versão específica
docker pull erisman/abmepi:v1.0

# Versão de produção
docker pull erisman/abmepi:production

# Versão estável
docker pull erisman/abmepi:stable
```

## 🚀 **Deploy em Produção**

### **DigitalOcean**
```bash
# Usar a imagem do Docker Hub
docker run -d \
  --name abmepi \
  -p 8080:8080 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=your-domain.com \
  -e DATABASE_URL=your-database-url \
  erisman/abmepi:production
```

### **AWS ECS**
```yaml
# task-definition.json
{
  "family": "abmepi",
  "containerDefinitions": [
    {
      "name": "abmepi",
      "image": "erisman/abmepi:production",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SECRET_KEY",
          "value": "your-secret-key"
        }
      ]
    }
  ]
}
```

### **Google Cloud Run**
```bash
# Deploy no Cloud Run
gcloud run deploy abmepi \
  --image erisman/abmepi:production \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## 🔍 **Monitoramento**

### **Health Check**
```bash
# Verificar saúde da aplicação
curl http://localhost:8080/health/
```

### **Logs**
```bash
# Ver logs do container
docker logs abmepi

# Ver logs em tempo real
docker logs -f abmepi
```

### **Métricas**
```bash
# Ver uso de recursos
docker stats abmepi
```

## 🚨 **Troubleshooting**

### **Problemas Comuns**

#### **Erro de Login**
```bash
# Fazer login novamente
docker logout
docker login
```

#### **Erro de Push**
```bash
# Verificar permissões
docker info

# Verificar se está logado
docker system info | grep Username
```

#### **Erro de Build**
```bash
# Limpar cache
docker system prune -a

# Reconstruir sem cache
docker build --no-cache -t erisman/abmepi:latest .
```

## 📞 **Suporte**

### **Recursos**
- [Docker Hub](https://hub.docker.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### **Comandos Úteis**
```bash
# Listar imagens
docker images

# Remover imagem
docker rmi erisman/abmepi:latest

# Limpar sistema
docker system prune -a

# Ver informações da imagem
docker inspect erisman/abmepi:latest
```

## 🏆 **Conclusão**

**A imagem está pronta para deploy no Docker Hub!**

**Próximos passos:**
1. ✅ Fazer login no Docker Hub
2. ✅ Executar script de deploy
3. ✅ Verificar se a imagem foi enviada
4. ✅ Testar a imagem localmente
5. ✅ Usar em produção

**Boa sorte com o deploy! 🚀**
