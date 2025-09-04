# 🔍 Diagnóstico do Erro 400 - Bad Request

## 🚨 Problema Identificado
- **URL**: `lobster-app-pqkby.ondigitalocean.app`
- **Erro**: 400 (Bad Request)
- **Status**: Aplicação não está respondendo corretamente

## 🔧 Possíveis Causas e Soluções

### 1. **Configuração de ALLOWED_HOSTS**
O erro 400 geralmente indica que o Django está rejeitando a requisição por questões de segurança.

**Solução:**
```env
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1
```

### 2. **Configuração de DEBUG**
Em produção, DEBUG deve estar como False, mas isso pode causar problemas se não estiver configurado corretamente.

**Solução:**
```env
DEBUG=False
```

### 3. **Configuração do Banco de Dados**
O banco pode não estar configurado corretamente.

**Verificar:**
- Credenciais do banco
- Conexão com PostgreSQL
- Migrações executadas

### 4. **Configuração do Nginx**
O proxy reverso pode não estar configurado corretamente.

## 🛠️ Passos para Correção

### Passo 1: Verificar Logs
No painel do DigitalOcean, verifique os logs da aplicação:
```bash
# Logs da aplicação Django
docker logs <container_id>

# Logs do Nginx
docker logs <nginx_container_id>
```

### Passo 2: Verificar Variáveis de Ambiente
Confirme se todas as variáveis estão configuradas:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app
DB_NAME=abmepi
DB_USER=postgres
DB_PASSWORD=sua-senha
DB_HOST=db
DB_PORT=5432
```

### Passo 3: Verificar Banco de Dados
```bash
# Conectar ao container
docker exec -it <container_id> bash

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### Passo 4: Verificar Configuração do Nginx
O arquivo nginx.conf deve estar configurado corretamente para o domínio.

## 🚀 Solução Rápida

### 1. Atualizar ALLOWED_HOSTS
No painel do DigitalOcean, adicione/atualize a variável:
```env
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1
```

### 2. Verificar DEBUG
```env
DEBUG=False
```

### 3. Redeploy
Após atualizar as variáveis, faça um redeploy da aplicação.

## 📊 Verificação Pós-Correção

### 1. Testar Health Check
```bash
curl https://lobster-app-pqkby.ondigitalocean.app/health/
```

### 2. Testar Página Principal
```bash
curl https://lobster-app-pqkby.ondigitalocean.app/
```

### 3. Verificar Logs
Monitore os logs para confirmar que não há mais erros.

## 🔍 Comandos de Diagnóstico

### Verificar Status dos Containers
```bash
docker ps
```

### Verificar Logs em Tempo Real
```bash
docker logs -f <container_id>
```

### Testar Conectividade do Banco
```bash
docker exec -it <container_id> python manage.py dbshell
```

### Verificar Configurações Django
```bash
docker exec -it <container_id> python manage.py check --deploy
```

## 📞 Próximos Passos

1. **Verificar logs** no painel do DigitalOcean
2. **Atualizar ALLOWED_HOSTS** com o domínio correto
3. **Verificar variáveis de ambiente**
4. **Executar migrações** se necessário
5. **Fazer redeploy** da aplicação
6. **Testar novamente**

---

**O erro 400 é comum em deploys iniciais e geralmente é resolvido ajustando as configurações de segurança do Django.**
