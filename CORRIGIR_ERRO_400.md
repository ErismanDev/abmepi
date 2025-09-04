# 🚨 Como Corrigir o Erro 400 - Bad Request

## 🔍 Diagnóstico
Você está recebendo erro 400 no DigitalOcean. Este é um problema comum que pode ser resolvido rapidamente.

## ⚡ Solução Rápida

### 1. **Atualizar ALLOWED_HOSTS**
No painel do DigitalOcean, vá em **Variáveis de Ambiente** e configure:

```env
ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1
```

### 2. **Verificar outras variáveis essenciais:**
```env
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
DB_NAME=abmepi
DB_USER=postgres
DB_PASSWORD=sua-senha-do-banco
DB_HOST=db
DB_PORT=5432
```

### 3. **Fazer Redeploy**
Após atualizar as variáveis, clique em **"Redeploy"** no painel do DigitalOcean.

## 🔧 Solução Detalhada

### Passo 1: Verificar Logs
1. Acesse o painel do DigitalOcean
2. Vá em **"Logs"** da sua aplicação
3. Procure por erros relacionados a ALLOWED_HOSTS

### Passo 2: Atualizar Configuração
1. Vá em **"Settings"** → **"Environment Variables"**
2. Adicione/atualize:
   ```
   ALLOWED_HOSTS=lobster-app-pqkby.ondigitalocean.app,ondigitalocean.app,localhost,127.0.0.1
   ```

### Passo 3: Verificar Banco de Dados
1. Confirme se o serviço PostgreSQL está rodando
2. Verifique se as credenciais estão corretas
3. Execute as migrações se necessário

### Passo 4: Redeploy
1. Clique em **"Redeploy"**
2. Aguarde o build completar
3. Teste novamente

## 🛠️ Comandos de Diagnóstico

### Via Terminal do DigitalOcean:
```bash
# Verificar status dos containers
docker ps

# Ver logs da aplicação
docker logs <container_id>

# Executar migrações
docker exec -it <container_id> python manage.py migrate

# Coletar arquivos estáticos
docker exec -it <container_id> python manage.py collectstatic --noinput

# Verificar configurações Django
docker exec -it <container_id> python manage.py check --deploy
```

## 📊 Verificação Pós-Correção

### 1. Testar Health Check
```bash
curl https://lobster-app-pqkby.ondigitalocean.app/health/
```
**Resultado esperado:** `healthy`

### 2. Testar Página Principal
```bash
curl https://lobster-app-pqkby.ondigitalocean.app/
```
**Resultado esperado:** Página de login ou dashboard

### 3. Verificar no Navegador
- Acesse: `https://lobster-app-pqkby.ondigitalocean.app/`
- Deve mostrar a página de login da ABMEPI

## 🚨 Se o Problema Persistir

### Verificar Logs Específicos:
```bash
# Logs do Django
docker logs <container_id> 2>&1 | grep -i error

# Logs do Nginx
docker logs <nginx_container_id> 2>&1 | grep -i error
```

### Verificar Configuração do Banco:
```bash
# Testar conexão com o banco
docker exec -it <container_id> python manage.py dbshell
```

### Verificar Arquivos Estáticos:
```bash
# Verificar se os arquivos estáticos foram coletados
docker exec -it <container_id> ls -la /app/staticfiles/
```

## 📝 Checklist de Verificação

- [ ] ALLOWED_HOSTS configurado corretamente
- [ ] SECRET_KEY definido
- [ ] DEBUG=False
- [ ] Banco de dados configurado
- [ ] Migrações executadas
- [ ] Arquivos estáticos coletados
- [ ] Redeploy realizado
- [ ] Logs verificados

## 🎯 Resultado Esperado

Após seguir estes passos, você deve ver:
- ✅ Página de login da ABMEPI
- ✅ Sem erros 400
- ✅ Aplicação funcionando normalmente

## 📞 Suporte

Se o problema persistir:
1. Verifique os logs detalhados
2. Confirme todas as variáveis de ambiente
3. Teste a conectividade do banco
4. Entre em contato com a equipe de desenvolvimento

---

**O erro 400 é geralmente resolvido ajustando o ALLOWED_HOSTS. Siga os passos acima e sua aplicação deve funcionar! 🚀**
