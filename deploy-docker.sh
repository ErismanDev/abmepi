#!/bin/bash

# Script de Deploy Docker para DigitalOcean
echo "🐳 Iniciando deploy Docker para DigitalOcean..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    exit 1
fi

# Verificar se docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas
echo "🧹 Removendo imagens antigas..."
docker-compose down --rmi all

# Construir novas imagens
echo "🔨 Construindo novas imagens..."
docker-compose build --no-cache

# Iniciar containers
echo "🚀 Iniciando containers..."
docker-compose up -d

# Verificar status
echo "📊 Verificando status dos containers..."
docker-compose ps

# Executar migrações
echo "🗄️ Executando migrações..."
docker-compose exec web python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput

# Verificar logs
echo "📋 Logs dos containers:"
docker-compose logs --tail=50

echo "✅ Deploy Docker concluído!"
echo "🌐 Aplicação disponível em: http://localhost:8080"
echo "📊 Para ver logs: docker-compose logs -f"
echo "🛑 Para parar: docker-compose down"
