-- Script de configuração do banco de dados para o sistema ABMEPI
-- Execute este script no PostgreSQL para criar o banco e usuário

-- 1. Criar o banco de dados
CREATE DATABASE abmepi_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 2. Criar usuário específico para o sistema (opcional, mas recomendado)
CREATE USER abmepi_user WITH PASSWORD 'sua_senha_aqui';

-- 3. Conceder privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE abmepi_db TO abmepi_user;

-- 4. Conectar ao banco criado
\c abmepi_db;

-- 5. Conceder privilégios adicionais (se necessário)
GRANT CREATE ON SCHEMA public TO abmepi_user;
GRANT USAGE ON SCHEMA public TO abmepi_user;

-- 6. Configurações de extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 7. Configurações de performance (opcional)
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.max = 10000;

-- 8. Configurações de conexão (opcional)
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';

-- 9. Recarregar configurações
SELECT pg_reload_conf();

-- 10. Verificar configurações
SELECT name, setting, unit, context, short_desc
FROM pg_settings 
WHERE name IN ('max_connections', 'shared_buffers', 'effective_cache_size');

-- Comentários sobre as configurações:
-- - max_connections: Número máximo de conexões simultâneas
-- - shared_buffers: Memória compartilhada para cache de dados
-- - effective_cache_size: Estimativa da memória disponível para cache
-- - pg_stat_statements: Extensão para monitoramento de performance

-- Após executar este script:
-- 1. Configure o arquivo .env com as credenciais
-- 2. Execute: python manage.py migrate
-- 3. Execute: python manage.py createsuperuser
-- 4. Execute: python manage.py runserver

-- Para verificar se tudo está funcionando:
-- \dt  -- Lista todas as tabelas
-- \du  -- Lista todos os usuários
-- \l   -- Lista todos os bancos
