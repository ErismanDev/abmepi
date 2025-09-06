# Deploy ABMEPI no Digital Ocean

Este guia completo irá te ajudar a fazer o deploy do sistema ABMEPI no Digital Ocean de forma segura e eficiente.

## 📋 Pré-requisitos

- Conta no Digital Ocean
- Domínio configurado (opcional, mas recomendado)
- Acesso SSH ao servidor
- Conhecimento básico de Linux

## 🚀 Passo a Passo

### 1. Criar Droplet no Digital Ocean

1. Acesse o [Digital Ocean](https://cloud.digitalocean.com/)
2. Clique em "Create" → "Droplets"
3. Escolha a imagem: **Ubuntu 22.04 LTS**
4. Escolha o plano: **Basic** (recomendado: 2GB RAM, 1 CPU, 50GB SSD)
5. Configure a autenticação SSH
6. Escolha um nome para o droplet (ex: `abmepi-server`)
7. Clique em "Create Droplet"

### 2. Conectar ao Servidor

```bash
ssh root@SEU_IP_DO_SERVIDOR
```

### 3. Preparar o Servidor

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Criar usuário não-root
adduser abmepi
usermod -aG sudo abmepi

# Configurar SSH para o usuário
cp -r ~/.ssh /home/abmepi/
chown -R abmepi:abmepi /home/abmepi/.ssh

# Sair e conectar com o usuário
exit
ssh abmepi@SEU_IP_DO_SERVIDOR
```

### 4. Fazer Upload do Código

#### Opção A: Via Git (Recomendado)
```bash
# Instalar Git
sudo apt install git -y

# Clonar repositório
git clone SEU_REPOSITORIO_GIT /opt/abmepi
cd /opt/abmepi
```

#### Opção B: Via SCP
```bash
# No seu computador local
scp -r . abmepi@SEU_IP_DO_SERVIDOR:/opt/abmepi/
```

### 5. Executar Script de Deploy

```bash
cd /opt/abmepi
chmod +x deploy.sh
./deploy.sh
```

O script irá:
- Instalar todas as dependências
- Configurar PostgreSQL
- Configurar Nginx
- Criar serviço systemd
- Configurar backup automático

### 6. Configurar Domínio (Opcional)

Se você tem um domínio:

1. Configure o DNS para apontar para o IP do servidor
2. Execute o script de SSL:

```bash
chmod +x setup-ssl.sh
./setup-ssl.sh SEU_DOMINIO.COM admin@SEU_DOMINIO.COM
```

### 7. Configurar Email

Edite o arquivo `.env` com suas credenciais de email:

```bash
nano .env
```

Configure:
- `EMAIL_HOST_USER`: Seu email
- `EMAIL_HOST_PASSWORD`: Senha de app do Gmail
- `ADMIN_EMAIL`: Email do administrador

### 8. Verificar Deploy

```bash
# Verificar status dos serviços
sudo systemctl status abmepi
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u abmepi -f
```

## 🔧 Configurações Avançadas

### Configurar Backup Automático

O backup automático já está configurado e roda diariamente. Para configurar manualmente:

```bash
# Executar backup manual
./backup-restore.sh backup

# Listar backups
./backup-restore.sh list

# Restaurar backup
./backup-restore.sh restore /opt/backups/abmepi/abmepi_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Configurar Monitoramento

```bash
# Instalar htop para monitoramento
sudo apt install htop -y

# Monitorar recursos
htop

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h
```

### Configurar Firewall

```bash
# Verificar status do firewall
sudo ufw status

# Configurar regras adicionais se necessário
sudo ufw allow 8080  # Para porta específica
```

## 📊 Monitoramento e Manutenção

### Comandos Úteis

```bash
# Reiniciar aplicação
sudo systemctl restart abmepi

# Ver logs da aplicação
sudo journalctl -u abmepi -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar status dos serviços
sudo systemctl status abmepi nginx postgresql

# Executar migrações
cd /opt/abmepi
source venv/bin/activate
python manage.py migrate --settings=abmepi.settings_production

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=abmepi.settings_production
```

### Backup e Restore

```bash
# Backup manual
./backup-restore.sh backup

# Restore de backup
./backup-restore.sh restore /caminho/para/backup.tar.gz

# Limpar backups antigos (mais de 30 dias)
./backup-restore.sh cleanup 30
```

## 🔒 Segurança

### Configurações de Segurança Implementadas

- ✅ Firewall configurado (portas 22, 80, 443)
- ✅ SSL/TLS com Let's Encrypt
- ✅ Headers de segurança no Nginx
- ✅ Rate limiting para API e login
- ✅ Usuário não-root para aplicação
- ✅ Backup automático diário
- ✅ Logs de auditoria

### Recomendações Adicionais

1. **Configurar fail2ban**:
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

2. **Configurar backup externo**:
```bash
# Configurar rsync para backup externo
rsync -avz /opt/backups/abmepi/ usuario@servidor-backup:/backup/abmepi/
```

3. **Monitorar logs de segurança**:
```bash
sudo tail -f /var/log/auth.log
sudo tail -f /var/log/nginx/access.log
```

## 🚨 Solução de Problemas

### Problemas Comuns

#### 1. Aplicação não inicia
```bash
# Verificar logs
sudo journalctl -u abmepi -f

# Verificar configuração
cd /opt/abmepi
source venv/bin/activate
python manage.py check --settings=abmepi.settings_production
```

#### 2. Erro de banco de dados
```bash
# Verificar status do PostgreSQL
sudo systemctl status postgresql

# Verificar conexão
sudo -u postgres psql -c "SELECT version();"
```

#### 3. Erro de arquivos estáticos
```bash
# Coletar arquivos estáticos
cd /opt/abmepi
source venv/bin/activate
python manage.py collectstatic --noinput --settings=abmepi.settings_production

# Verificar permissões
sudo chown -R abmepi:abmepi /opt/abmepi/staticfiles
```

#### 4. Erro de SSL
```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --dry-run
```

### Logs Importantes

- **Aplicação**: `sudo journalctl -u abmepi -f`
- **Nginx**: `/var/log/nginx/error.log`
- **PostgreSQL**: `/var/log/postgresql/postgresql-*.log`
- **Sistema**: `/var/log/syslog`

## 📈 Otimizações de Performance

### Configurações do Nginx

O arquivo `nginx.conf` já inclui:
- Compressão Gzip
- Cache de arquivos estáticos
- Rate limiting
- Headers de segurança

### Configurações do Django

O arquivo `settings_production.py` inclui:
- Cache configurado
- Logging otimizado
- Configurações de segurança
- Otimizações de banco de dados

### Monitoramento de Performance

```bash
# Instalar ferramentas de monitoramento
sudo apt install htop iotop nethogs -y

# Monitorar recursos
htop
iotop
nethogs
```

## 🔄 Atualizações

### Atualizar Aplicação

```bash
cd /opt/abmepi

# Fazer backup antes da atualização
./backup-restore.sh backup

# Atualizar código
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Executar migrações
python manage.py migrate --settings=abmepi.settings_production

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=abmepi.settings_production

# Reiniciar aplicação
sudo systemctl restart abmepi
```

### Atualizar Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Reiniciar se necessário
sudo reboot
```

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs primeiro
2. Consulte este documento
3. Verifique o status dos serviços
4. Execute os comandos de diagnóstico

## 📝 Checklist de Deploy

- [ ] Droplet criado no Digital Ocean
- [ ] Servidor configurado
- [ ] Código enviado para o servidor
- [ ] Script de deploy executado
- [ ] Domínio configurado (se aplicável)
- [ ] SSL configurado (se aplicável)
- [ ] Email configurado
- [ ] Backup testado
- [ ] Monitoramento configurado
- [ ] Segurança verificada

## 🎉 Conclusão

Após seguir este guia, você terá:

- ✅ Sistema ABMEPI rodando em produção
- ✅ SSL/TLS configurado
- ✅ Backup automático
- ✅ Monitoramento básico
- ✅ Segurança implementada
- ✅ Documentação completa

O sistema estará pronto para uso em produção no Digital Ocean!
