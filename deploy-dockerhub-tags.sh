#!/bin/bash

# Script de Deploy para Docker Hub com Tags Específicas
echo "🐳 Deploy para Docker Hub - ABMEPI com Tags"
echo "==========================================="

# Configurações
DOCKER_USERNAME="erisman"
IMAGE_NAME="abmepi"
BASE_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

# Tags para deploy
TAGS=("latest" "v1.0" "production" "stable")

echo "📋 Configurações:"
echo "   Usuário: $DOCKER_USERNAME"
echo "   Imagem: $IMAGE_NAME"
echo "   Tags: ${TAGS[*]}"
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

# Construir a imagem base
echo "🔨 Construindo imagem Docker base..."
docker build -t "$BASE_IMAGE_NAME" .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir a imagem!"
    exit 1
fi

echo "✅ Imagem base construída com sucesso!"

# Criar tags e fazer push
for tag in "${TAGS[@]}"; do
    FULL_IMAGE_NAME="${BASE_IMAGE_NAME}:${tag}"
    
    echo "🏷️  Criando tag: $FULL_IMAGE_NAME"
    docker tag "$BASE_IMAGE_NAME" "$FULL_IMAGE_NAME"
    
    echo "🚀 Fazendo push: $FULL_IMAGE_NAME"
    docker push "$FULL_IMAGE_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Push de $FULL_IMAGE_NAME realizado com sucesso!"
    else
        echo "❌ Erro no push de $FULL_IMAGE_NAME!"
    fi
    
    echo ""
done

# Mostrar informações das imagens
echo "📊 Imagens criadas:"
docker images | grep "$IMAGE_NAME"

echo ""
echo "🌐 Imagens disponíveis em:"
echo "   https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
echo ""
echo "📋 Comandos para usar as imagens:"
for tag in "${TAGS[@]}"; do
    echo "   docker pull $BASE_IMAGE_NAME:$tag"
    echo "   docker run -p 8080:8080 $BASE_IMAGE_NAME:$tag"
done
echo ""
echo "✅ Deploy no Docker Hub com tags concluído!"
