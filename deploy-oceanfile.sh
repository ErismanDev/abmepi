#!/bin/bash

# Script de Deploy para Oceanfile - ABMEPI
# Este script prepara o projeto para deploy no Oceanfile

set -e

echo "🌊 Preparando deploy para Oceanfile..."

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Verificações básicas concluídas"

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando do exemplo..."
    if [ -f env.production.example ]; then
        cp env.production.example .env
        echo "📝 Arquivo .env criado. Configure as variáveis antes de continuar."
        echo "   Edite o arquivo .env com suas configurações de produção."
        exit 1
    else
        echo "❌ Arquivo env.production.example não encontrado."
        exit 1
    fi
fi

echo "✅ Arquivo .env encontrado"

# Testar build local
echo "🔨 Testando build local..."
docker-compose -f docker-compose.oceanfile.yml build

echo "✅ Build local bem-sucedido"

# Testar se a aplicação inicia
echo "🚀 Testando inicialização da aplicação..."
docker-compose -f docker-compose.oceanfile.yml up -d

# Aguardar a aplicação inicializar
echo "⏳ Aguardando aplicação inicializar..."
sleep 15

# Verificar se está funcionando
echo "🔍 Verificando se a aplicação está funcionando..."
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ Aplicação está funcionando corretamente!"
else
    echo "❌ Aplicação não está respondendo. Verifique os logs:"
    docker-compose -f docker-compose.oceanfile.yml logs web
    docker-compose -f docker-compose.oceanfile.yml down
    exit 1
fi

# Parar containers de teste
echo "🛑 Parando containers de teste..."
docker-compose -f docker-compose.oceanfile.yml down

echo ""
echo "🎉 Projeto pronto para deploy no Oceanfile!"
echo ""
echo "📋 Próximos passos:"
echo "1. Faça commit e push das mudanças:"
echo "   git add ."
echo "   git commit -m 'Preparação para deploy no Oceanfile'"
echo "   git push origin main"
echo ""
echo "2. No painel do Oceanfile:"
echo "   - Crie uma nova aplicação"
echo "   - Configure como 'Docker Compose'"
echo "   - Use o arquivo: docker-compose.oceanfile.yml"
echo "   - Configure as variáveis de ambiente do arquivo .env"
echo ""
echo "3. Configure o banco de dados PostgreSQL no Oceanfile"
echo ""
echo "4. Faça o deploy e monitore os logs"
echo ""
echo "📚 Para mais detalhes, consulte: DEPLOY_OCEANFILE.md"
