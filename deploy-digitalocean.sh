#!/bin/bash

# Script de Deploy Automatizado para DigitalOcean
echo "🚀 Deploy Automatizado para DigitalOcean App Platform"
echo "=================================================="

# Verificar se doctl está instalado
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl não está instalado!"
    echo "📥 Instale com: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Verificar se está autenticado
if ! doctl account get &> /dev/null; then
    echo "❌ Não está autenticado no DigitalOcean!"
    echo "🔑 Execute: doctl auth init"
    exit 1
fi

# Verificar se o app existe
APP_NAME="abmepi"
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "❌ App '$APP_NAME' não encontrado!"
    echo "🔧 Crie o app primeiro no painel do DigitalOcean"
    exit 1
fi

echo "✅ App encontrado: $APP_NAME (ID: $APP_ID)"

# Fazer deploy
echo "🚀 Iniciando deploy..."
doctl apps create-deployment "$APP_ID" --force-rebuild

# Aguardar deploy
echo "⏳ Aguardando deploy completar..."
doctl apps get-deployment "$APP_ID" --format ID,Status --no-header

# Verificar status
echo "📊 Verificando status do app..."
doctl apps get "$APP_ID" --format Name,DefaultIngress,ActiveDeployment.Status

# Mostrar logs
echo "📋 Logs do deploy:"
doctl apps logs "$APP_ID" --type=build --tail=50

echo "✅ Deploy concluído!"
echo "🌐 Acesse: https://lobster-app-pqkby.ondigitalocean.app/"
