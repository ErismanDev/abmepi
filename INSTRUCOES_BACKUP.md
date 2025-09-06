# Instruções para Restaurar Backup do Banco ABMEPI

## Arquivos de Backup Criados

- **`backup_abmepi.backup`** - Backup completo do banco PostgreSQL (formato personalizado)
- **`requirements.txt`** - Dependências Python do projeto
- **`env.example`** - Exemplo de variáveis de ambiente

## Pré-requisitos no Novo PC

### 1. Instalar PostgreSQL
- Baixe e instale o PostgreSQL 12 ou superior
- Durante a instalação, anote a senha do usuário `postgres`
- Certifique-se de que o serviço PostgreSQL está rodando

### 2. Instalar Python
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 3. Instalar Git (opcional)
- Para clonar o repositório do projeto

## Passos para Restaurar o Banco

### 1. Criar o Banco de Dados
```bash
# Conectar ao PostgreSQL como superusuário
psql -U postgres

# Criar o banco de dados
CREATE DATABASE abmepi;

# Verificar se foi criado
\l

# Sair do psql
\q
```

### 2. Restaurar o Backup
```bash
# Restaurar o backup (substitua 'senha' pela senha real do postgres)
pg_restore -h localhost -U postgres -d abmepi backup_abmepi.backup
```

### 3. Verificar a Restauração
```bash
# Conectar ao banco restaurado
psql -U postgres -d abmepi

# Listar as tabelas
\dt

# Verificar o número de registros em algumas tabelas principais
SELECT COUNT(*) FROM core_usuario;
SELECT COUNT(*) FROM associados_associado;

# Sair do psql
\q
```

## Configurar o Projeto Django

### 1. Clonar/Copiar o Projeto
```bash
# Se tiver o código fonte
git clone <url-do-repositorio>
cd abmepi

# Ou copiar a pasta do projeto
```

### 2. Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar o arquivo de exemplo
cp env.example .env

# Editar o arquivo .env com as configurações corretas
# Especialmente as configurações do banco de dados
```

### 5. Aplicar Migrações (se necessário)
```bash
python manage.py migrate
```

### 6. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 7. Testar a Aplicação
```bash
python manage.py runserver
```

## Configurações Importantes

### Banco de Dados
No arquivo `abmepi/settings.py`, certifique-se de que as configurações do banco estão corretas:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'abmepi',
        'USER': 'postgres',
        'PASSWORD': 'sua_senha_aqui',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Arquivos de Mídia
- Copie a pasta `media/` para o novo PC
- Certifique-se de que o caminho `MEDIA_ROOT` está correto

## Solução de Problemas Comuns

### Erro de Conexão com Banco
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais de acesso
- Teste a conexão com `psql -U postgres -d abmepi`

### Erro de Permissões
- Verifique se o usuário `postgres` tem permissões adequadas
- Execute `GRANT ALL PRIVILEGES ON DATABASE abmepi TO postgres;`

### Erro de Dependências
- Atualize o pip: `pip install --upgrade pip`
- Instale as dependências uma por uma se necessário

## Contato e Suporte

Em caso de problemas durante a restauração, verifique:
1. Logs do PostgreSQL
2. Logs do Django
3. Configurações de firewall/antivírus
4. Permissões de usuário do sistema

---

**Data do Backup:** $(Get-Date -Format "dd/MM/yyyy HH:mm")
**Versão do PostgreSQL:** Verificar com `psql --version`
**Tamanho do Backup:** $(Get-Item backup_abmepi.backup).Length bytes
