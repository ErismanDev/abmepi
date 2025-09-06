# Instruções para Windows - Deploy ABMEPI

Como você está no Windows, aqui estão as instruções específicas para preparar o sistema para deploy no Digital Ocean.

## 📋 Pré-requisitos no Windows

1. **Git** - Para fazer upload do código
2. **WinSCP** ou **FileZilla** - Para transferir arquivos (opcional)
3. **PuTTY** - Para conectar via SSH (opcional, pode usar o terminal do Windows)

## 🚀 Passo a Passo

### 1. Preparar o Código

Todos os arquivos necessários já foram criados:
- ✅ `abmepi/settings_production.py` - Configurações de produção
- ✅ `env.production` - Variáveis de ambiente
- ✅ `Dockerfile` - Containerização
- ✅ `docker-compose.yml` - Orquestração
- ✅ `nginx.conf` - Configuração do servidor web
- ✅ `deploy.sh` - Script de deploy
- ✅ `setup-ssl.sh` - Configuração SSL
- ✅ `backup-restore.sh` - Backup e restore
- ✅ `quick-start.sh` - Inicialização rápida
- ✅ `gunicorn.conf.py` - Configuração do servidor WSGI
- ✅ `.gitignore` - Arquivos ignorados pelo Git

### 2. Fazer Upload para o Servidor

#### Opção A: Via Git (Recomendado)

```bash
# No seu computador Windows (PowerShell ou CMD)
git add .
git commit -m "Preparar para deploy no Digital Ocean"
git push origin main
```

Depois no servidor Digital Ocean:
```bash
git clone SEU_REPOSITORIO_GIT /opt/abmepi
cd /opt/abmepi
```

#### Opção B: Via SCP (WinSCP)

1. Abra o WinSCP
2. Conecte ao seu servidor Digital Ocean
3. Navegue até `/opt/`
4. Crie a pasta `abmepi`
5. Faça upload de todos os arquivos do projeto

#### Opção C: Via FileZilla

1. Abra o FileZilla
2. Conecte ao servidor
3. Navegue até `/opt/`
4. Crie a pasta `abmepi`
5. Faça upload de todos os arquivos

### 3. Executar Deploy no Servidor

Conecte ao servidor via SSH e execute:

```bash
# Tornar scripts executáveis
chmod +x deploy.sh setup-ssl.sh backup-restore.sh quick-start.sh

# Executar deploy
./deploy.sh
```

### 4. Configurar Domínio (Opcional)

Se você tem um domínio:

```bash
# Configurar SSL
./setup-ssl.sh SEU_DOMINIO.COM admin@SEU_DOMINIO.COM
```

### 5. Configurar Email

Edite o arquivo `.env` no servidor:

```bash
nano .env
```

Configure suas credenciais de email.

## 🔧 Comandos Úteis no Servidor

### Verificar Status
```bash
# Status dos serviços
sudo systemctl status abmepi
sudo systemctl status nginx
sudo systemctl status postgresql

# Logs
sudo journalctl -u abmepi -f
```

### Backup e Restore
```bash
# Backup
./backup-restore.sh backup

# Listar backups
./backup-restore.sh list

# Restore
./backup-restore.sh restore /caminho/para/backup.tar.gz
```

### Reiniciar Serviços
```bash
# Reiniciar aplicação
sudo systemctl restart abmepi

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

## 🐳 Usando Docker (Alternativa)

Se preferir usar Docker:

```bash
# Construir e executar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## 📊 Monitoramento

### Verificar Recursos
```bash
# Uso de CPU e memória
htop

# Espaço em disco
df -h

# Uso de memória
free -h
```

### Verificar Logs
```bash
# Logs da aplicação
sudo journalctl -u abmepi -f

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## 🚨 Solução de Problemas

### Problema: Script não executa
```bash
# Verificar permissões
ls -la *.sh

# Tornar executável
chmod +x nome_do_script.sh
```

### Problema: Aplicação não inicia
```bash
# Verificar logs
sudo journalctl -u abmepi -f

# Verificar configuração
cd /opt/abmepi
source venv/bin/activate
python manage.py check --settings=abmepi.settings_production
```

### Problema: Banco de dados
```bash
# Verificar status
sudo systemctl status postgresql

# Verificar conexão
sudo -u postgres psql -c "SELECT version();"
```

## 📝 Checklist de Deploy

- [ ] Código enviado para o servidor
- [ ] Scripts tornados executáveis
- [ ] Deploy executado com sucesso
- [ ] Domínio configurado (se aplicável)
- [ ] SSL configurado (se aplicável)
- [ ] Email configurado
- [ ] Backup testado
- [ ] Monitoramento funcionando

## 🎉 Próximos Passos

1. **Teste o sistema** - Acesse a URL e teste todas as funcionalidades
2. **Configure backup** - Teste o sistema de backup
3. **Configure monitoramento** - Monitore recursos e logs
4. **Configure SSL** - Se tiver domínio, configure SSL
5. **Configure email** - Configure as credenciais de email

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs primeiro
2. Consulte a documentação
3. Verifique o status dos serviços
4. Execute os comandos de diagnóstico

O sistema estará pronto para uso em produção no Digital Ocean! 🚀
