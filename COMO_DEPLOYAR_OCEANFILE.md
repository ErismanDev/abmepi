# 🌊 Como Deployar no Oceanfile - Passo a Passo

## ✅ Status do Projeto
- ✅ **Código limpo** - Todos os prints de debug removidos
- ✅ **Configurações de produção** - Settings.py configurado
- ✅ **Docker configurado** - Dockerfile e docker-compose prontos
- ✅ **Segurança implementada** - Headers de segurança configurados
- ✅ **Nginx configurado** - Proxy reverso e arquivos estáticos
- ✅ **Documentação completa** - Guias e scripts criados

## 🚀 Passo a Passo para Deploy

### 1. **Preparar o Repositório**
```bash
# Adicionar todos os arquivos
git add .

# Commit das mudanças
git commit -m "Preparação completa para deploy no Oceanfile"

# Push para o repositório
git push origin main
```

### 2. **Acessar o Oceanfile**
1. Acesse [oceanfile.com](https://oceanfile.com)
2. Faça login na sua conta
3. Vá para "Projetos" ou "Aplicações"
4. Clique em "Nova Aplicação"

### 3. **Configurar a Aplicação**
- **Nome**: `abmepi`
- **Tipo**: `Docker Compose`
- **Repositório**: Seu repositório Git (GitHub/GitLab)
- **Branch**: `main`
- **Arquivo Compose**: `docker-compose.oceanfile.yml`

### 4. **Configurar Variáveis de Ambiente**
No painel do Oceanfile, vá em "Variáveis de Ambiente" e adicione:

```env
SECRET_KEY=sua-chave-secreta-super-segura-com-pelo-menos-50-caracteres
DEBUG=False
ALLOWED_HOSTS=seu-dominio.oceanfile.com,localhost,127.0.0.1

DB_NAME=abmepi
DB_USER=postgres
DB_PASSWORD=senha-fornecida-pelo-oceanfile
DB_HOST=db
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### 5. **Configurar Banco de Dados**
1. No painel do Oceanfile, adicione um serviço **PostgreSQL**
2. Anote as credenciais fornecidas
3. Use essas credenciais nas variáveis de ambiente

### 6. **Fazer o Deploy**
1. Clique em **"Deploy"** no painel
2. Aguarde o build dos containers (pode levar alguns minutos)
3. Monitore os logs para verificar se tudo está funcionando

### 7. **Verificar se Funcionou**
- Acesse a URL fornecida pelo Oceanfile
- Teste o health check: `https://seu-dominio.oceanfile.com/health/`
- Faça login na aplicação

## 🔧 Arquivos Importantes Criados

### Para o Oceanfile:
- `docker-compose.oceanfile.yml` - Configuração específica
- `nginx.oceanfile.conf` - Nginx otimizado
- `DEPLOY_OCEANFILE.md` - Guia completo
- `deploy-oceanfile.sh` - Script de preparação

### Configurações Gerais:
- `Dockerfile` - Imagem Docker otimizada
- `docker-compose.yml` - Para desenvolvimento
- `nginx.conf` - Nginx para desenvolvimento
- `.dockerignore` - Arquivos ignorados no build

## 🛠️ Comandos Úteis no Oceanfile

### Via Terminal Web:
```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Ver logs
tail -f /app/logs/abmepi.log
```

## 🚨 Solução de Problemas

### ❌ Aplicação não inicia
1. Verifique os logs no painel do Oceanfile
2. Confirme se todas as variáveis de ambiente estão configuradas
3. Verifique se o banco de dados está acessível

### ❌ Erro 500
1. Verifique se `DEBUG=False` está configurado
2. Confirme se `ALLOWED_HOSTS` inclui o domínio do Oceanfile
3. Verifique os logs da aplicação

### ❌ Arquivos estáticos não carregam
1. Execute `python manage.py collectstatic --noinput`
2. Verifique se o Nginx está servindo os arquivos corretamente

### ❌ Banco de dados não conecta
1. Verifique as credenciais do banco
2. Confirme se o serviço PostgreSQL está rodando
3. Teste a conexão: `python manage.py dbshell`

## 📊 Monitoramento

### Logs:
- Acesse o painel do Oceanfile
- Vá em "Logs" para ver os logs em tempo real

### Métricas:
- Use o painel de métricas do Oceanfile
- Monitore CPU, memória e tráfego

## 🔄 Atualizações Futuras

### Para atualizar:
1. Faça as mudanças no código
2. Commit e push: `git push origin main`
3. No painel do Oceanfile, clique em "Redeploy"
4. Aguarde o build e deploy

## 📞 Suporte

- **Documentação**: `DEPLOY_OCEANFILE.md`
- **Logs**: Sempre verifique os logs primeiro
- **Equipe**: Entre em contato com a equipe de desenvolvimento

---

## 🎉 Resumo Final

**Seu projeto ABMEPI está 100% pronto para deploy no Oceanfile!**

✅ Código limpo e otimizado  
✅ Configurações de produção  
✅ Docker configurado  
✅ Segurança implementada  
✅ Documentação completa  
✅ Scripts de deploy  

**Agora é só seguir os passos acima e seu sistema estará rodando em produção!** 🚀
