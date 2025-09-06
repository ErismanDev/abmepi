# 🔄 Sistema de Backup ABMEPI

Este documento explica como usar o sistema de backup automatizado para o projeto ABMEPI.

## 📋 Arquivos de Backup Criados

### 1. Backup Manual (já criado)
- **`backup_abmepi.backup`** - Backup completo do banco PostgreSQL
- **`INSTRUCOES_BACKUP.md`** - Instruções detalhadas para restauração

### 2. Script de Backup Automatizado
- **`backup_database.py`** - Script Python para backups automáticos
- **`README_BACKUP.md`** - Este arquivo de documentação

## 🚀 Como Usar o Script de Backup

### Backup Simples
```bash
python backup_database.py
```

### Listar Backups Existentes
```bash
python backup_database.py list
```

### Limpar Backups Antigos
```bash
# Limpar backups com mais de 30 dias (padrão)
python backup_database.py clean

# Limpar backups com mais de 7 dias
python backup_database.py clean 7
```

### Ver Ajuda
```bash
python backup_database.py help
```

## 📁 Estrutura dos Backups Automatizados

Quando você executa o script, ele cria uma pasta `backups/` com:

```
backups/
├── backup_abmepi_20241201_143022.backup    # Backup do banco
├── backup_abmepi_20241201_143022_files.zip # Arquivos do projeto
└── backup_abmepi_20241201_143022_instrucoes.md # Instruções
```

## 🔧 O que o Script Faz

### 1. Backup do Banco de Dados
- Usa `pg_dump` para criar backup completo
- Formato personalizado (.backup) para eficiência
- Inclui todas as tabelas, dados e estrutura

### 2. Backup dos Arquivos
- Cria arquivo ZIP com código fonte
- Inclui pastas principais do projeto
- Exclui arquivos desnecessários (cache, logs, etc.)

### 3. Documentação Automática
- Gera instruções específicas para cada backup
- Inclui timestamp e informações do backup
- Passos detalhados para restauração

## 📥 Como Restaurar em Outro PC

### Pré-requisitos
- PostgreSQL instalado e rodando
- Python 3.8+ instalado
- Acesso ao arquivo de backup

### Passos de Restauração

#### 1. Restaurar o Banco
```bash
# Criar banco
createdb -U postgres abmepi

# Restaurar backup
pg_restore -U postgres -d abmepi backup_abmepi_YYYYMMDD_HHMMSS.backup
```

#### 2. Extrair Arquivos
```bash
# Extrair arquivos do projeto
unzip backup_abmepi_YYYYMMDD_HHMMSS_files.zip
```

#### 3. Configurar Ambiente
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
cp env.example .env
# Editar .env com configurações corretas

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

#### 4. Testar
```bash
python manage.py runserver
```

## ⚠️ Considerações Importantes

### Segurança
- **NUNCA** compartilhe backups com dados sensíveis
- Use senhas fortes para o banco de dados
- Considere criptografar backups importantes

### Performance
- Backups podem ser grandes dependendo dos dados
- Execute backups em horários de baixo uso
- Monitore o espaço em disco

### Frequência
- **Desenvolvimento**: Backup antes de mudanças importantes
- **Produção**: Backup diário ou semanal
- **Teste**: Backup antes de atualizações

## 🆘 Solução de Problemas

### Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
pg_ctl status

# Testar conexão
psql -U postgres -d abmepi
```

### Erro de Permissões
```bash
# Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE abmepi TO postgres;
```

### Erro de Dependências
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências uma por uma
pip install django
pip install psycopg2-binary
# etc...
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do PostgreSQL
2. Verifique os logs do Django
3. Confirme as configurações de conexão
4. Teste comandos básicos do PostgreSQL

## 🔄 Agendamento de Backups

### Windows (Agendador de Tarefas)
```cmd
# Criar tarefa agendada
schtasks /create /tn "Backup ABMEPI" /tr "python C:\projetos\abmepi\backup_database.py" /sc daily /st 02:00
```

### Linux/Mac (Cron)
```bash
# Editar crontab
crontab -e

# Adicionar linha para backup diário às 2h
0 2 * * * cd /caminho/para/abmepi && python backup_database.py
```

---

**Última atualização:** $(Get-Date -Format "dd/MM/yyyy HH:mm")
**Versão do script:** 1.0
**Compatibilidade:** PostgreSQL 12+, Python 3.8+
