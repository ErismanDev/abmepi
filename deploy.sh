#!/bin/bash

# Script de Deploy para ABMEPI
# Este script automatiza o processo de deploy em produção

set -e

echo "🚀 Iniciando deploy do ABMEPI..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando do exemplo..."
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

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional)
read -p "🗑️  Deseja remover imagens antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removendo imagens antigas..."
    docker-compose down --rmi all
fi

# Construir e iniciar os containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar o banco de dados estar pronto
echo "⏳ Aguardando banco de dados..."
sleep 10

# Executar migrações
echo "📊 Executando migrações..."
docker-compose exec web python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput

# Criar superusuário (opcional)
read -p "👤 Deseja criar um superusuário? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "👤 Criando superusuário..."
    docker-compose exec web python manage.py createsuperuser
fi

# Verificar status dos containers
echo "📊 Verificando status dos containers..."
docker-compose ps

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: http://localhost"
echo "📊 Para ver logs: docker-compose logs -f"
echo "🛑 Para parar: docker-compose down"
