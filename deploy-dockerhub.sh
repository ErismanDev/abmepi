#!/bin/bash

# Script de Deploy para Docker Hub
echo "🐳 Deploy para Docker Hub - ABMEPI"
echo "=================================="

# Configurações
DOCKER_USERNAME="erisman"
IMAGE_NAME="abmepi"
TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "📋 Configurações:"
echo "   Usuário: $DOCKER_USERNAME"
echo "   Imagem: $IMAGE_NAME"
echo "   Tag: $TAG"
echo "   Nome completo: $FULL_IMAGE_NAME"
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "📥 Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Verificar se está logado no Docker Hub
echo "🔐 Verificando login no Docker Hub..."
if ! docker info | grep -q "Username"; then
    echo "❌ Não está logado no Docker Hub!"
    echo "🔑 Execute: docker login"
    echo "   Usuário: $DOCKER_USERNAME"
    exit 1
fi

echo "✅ Logado no Docker Hub!"

# Construir a imagem
echo "🔨 Construindo imagem Docker..."
docker build -t "$FULL_IMAGE_NAME" .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir a imagem!"
    exit 1
fi

echo "✅ Imagem construída com sucesso!"

# Fazer push para o Docker Hub
echo "🚀 Fazendo push para o Docker Hub..."
docker push "$FULL_IMAGE_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao fazer push!"
    exit 1
fi

echo "✅ Push realizado com sucesso!"

# Mostrar informações da imagem
echo ""
echo "📊 Informações da imagem:"
docker images | grep "$IMAGE_NAME"

echo ""
echo "🌐 Imagem disponível em:"
echo "   https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
echo ""
echo "📋 Comandos para usar a imagem:"
echo "   docker pull $FULL_IMAGE_NAME"
echo "   docker run -p 8080:8080 $FULL_IMAGE_NAME"
echo ""
echo "✅ Deploy no Docker Hub concluído!"
