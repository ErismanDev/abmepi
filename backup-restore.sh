#!/bin/bash

# Script de Backup e Restore - ABMEPI
# Uso: ./backup-restore.sh backup|restore [arquivo_backup]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Configurações
PROJECT_DIR="/opt/abmepi"
BACKUP_DIR="/opt/backups/abmepi"
DB_NAME="abmepi_prod"
DB_USER="abmepi_user"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Função de backup
backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/abmepi_backup_$timestamp"
    
    log "Iniciando backup do sistema ABMEPI..."
    
    # Backup do banco de dados
    log "Fazendo backup do banco de dados..."
    cd $PROJECT_DIR
    source venv/bin/activate
    python manage.py dumpdata --settings=abmepi.settings_production > "${backup_file}.json"
    
    # Backup dos arquivos de mídia
    log "Fazendo backup dos arquivos de mídia..."
    tar -czf "${backup_file}_media.tar.gz" -C $PROJECT_DIR media/
    
    # Backup dos logs
    log "Fazendo backup dos logs..."
    tar -czf "${backup_file}_logs.tar.gz" -C $PROJECT_DIR logs/
    
    # Backup da configuração
    log "Fazendo backup da configuração..."
    cp .env "${backup_file}_env"
    
    # Criar arquivo de metadados
    cat > "${backup_file}_metadata.txt" << EOF
Backup ABMEPI - $timestamp
Data: $(date)
Versão: $(python manage.py --version --settings=abmepi.settings_production)
Banco: $DB_NAME
Usuário: $DB_USER
Diretório: $PROJECT_DIR
EOF
    
    # Criar arquivo compactado final
    log "Criando arquivo de backup final..."
    cd $BACKUP_DIR
    tar -czf "abmepi_backup_$timestamp.tar.gz" \
        "abmepi_backup_$timestamp.json" \
        "abmepi_backup_$timestamp_media.tar.gz" \
        "abmepi_backup_$timestamp_logs.tar.gz" \
        "abmepi_backup_$timestamp_env" \
        "abmepi_backup_$timestamp_metadata.txt"
    
    # Remover arquivos temporários
    rm -f "abmepi_backup_$timestamp.json" \
          "abmepi_backup_$timestamp_media.tar.gz" \
          "abmepi_backup_$timestamp_logs.tar.gz" \
          "abmepi_backup_$timestamp_env" \
          "abmepi_backup_$timestamp_metadata.txt"
    
    log "✅ Backup concluído: abmepi_backup_$timestamp.tar.gz"
    log "📁 Localização: $BACKUP_DIR/abmepi_backup_$timestamp.tar.gz"
    
    # Mostrar tamanho do backup
    local size=$(du -h "$BACKUP_DIR/abmepi_backup_$timestamp.tar.gz" | cut -f1)
    log "📊 Tamanho do backup: $size"
}

# Função de restore
restore() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        error "Arquivo de backup não especificado"
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Arquivo de backup não encontrado: $backup_file"
    fi
    
    log "Iniciando restore do sistema ABMEPI..."
    log "Arquivo de backup: $backup_file"
    
    # Parar serviços
    log "Parando serviços..."
    sudo systemctl stop abmepi
    sudo systemctl stop nginx
    
    # Extrair backup
    local temp_dir="/tmp/abmepi_restore_$(date +%s)"
    mkdir -p $temp_dir
    cd $temp_dir
    
    log "Extraindo arquivo de backup..."
    tar -xzf "$backup_file"
    
    # Verificar se os arquivos existem
    local json_file=$(ls abmepi_backup_*_*.json 2>/dev/null | head -1)
    local media_file=$(ls abmepi_backup_*_*_media.tar.gz 2>/dev/null | head -1)
    local logs_file=$(ls abmepi_backup_*_*_logs.tar.gz 2>/dev/null | head -1)
    local env_file=$(ls abmepi_backup_*_*_env 2>/dev/null | head -1)
    
    if [ -z "$json_file" ]; then
        error "Arquivo de dados do banco não encontrado no backup"
    fi
    
    # Backup de segurança do estado atual
    log "Criando backup de segurança do estado atual..."
    local safety_backup="$BACKUP_DIR/safety_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$safety_backup" -C $PROJECT_DIR media/ logs/ .env
    
    # Restore do banco de dados
    log "Restaurando banco de dados..."
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Limpar banco atual
    python manage.py flush --noinput --settings=abmepi.settings_production
    
    # Restaurar dados
    python manage.py loaddata "$temp_dir/$json_file" --settings=abmepi.settings_production
    
    # Restore dos arquivos de mídia
    if [ -n "$media_file" ]; then
        log "Restaurando arquivos de mídia..."
        tar -xzf "$temp_dir/$media_file" -C $PROJECT_DIR
    fi
    
    # Restore dos logs
    if [ -n "$logs_file" ]; then
        log "Restaurando logs..."
        tar -xzf "$temp_dir/$logs_file" -C $PROJECT_DIR
    fi
    
    # Restore da configuração (opcional)
    if [ -n "$env_file" ]; then
        log "Restaurando configuração..."
        cp "$temp_dir/$env_file" $PROJECT_DIR/.env
    fi
    
    # Executar migrações
    log "Executando migrações..."
    python manage.py migrate --settings=abmepi.settings_production
    
    # Coletar arquivos estáticos
    log "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --settings=abmepi.settings_production
    
    # Limpar arquivos temporários
    rm -rf $temp_dir
    
    # Iniciar serviços
    log "Iniciando serviços..."
    sudo systemctl start abmepi
    sudo systemctl start nginx
    
    log "✅ Restore concluído com sucesso!"
    log "📁 Backup de segurança criado em: $safety_backup"
}

# Função para listar backups
list_backups() {
    log "Listando backups disponíveis:"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lah "$BACKUP_DIR"/*.tar.gz 2>/dev/null | while read line; do
            echo "  $line"
        done
    else
        warning "Diretório de backup não encontrado: $BACKUP_DIR"
    fi
}

# Função para limpar backups antigos
cleanup_backups() {
    local days=${1:-30}
    log "Removendo backups mais antigos que $days dias..."
    
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$days -delete
        log "✅ Limpeza concluída"
    else
        warning "Diretório de backup não encontrado: $BACKUP_DIR"
    fi
}

# Função principal
main() {
    case "$1" in
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        list)
            list_backups
            ;;
        cleanup)
            cleanup_backups "$2"
            ;;
        *)
            echo "Uso: $0 {backup|restore|list|cleanup} [arquivo_backup|dias]"
            echo ""
            echo "Comandos:"
            echo "  backup                    - Criar backup do sistema"
            echo "  restore <arquivo>         - Restaurar sistema do backup"
            echo "  list                      - Listar backups disponíveis"
            echo "  cleanup [dias]            - Remover backups antigos (padrão: 30 dias)"
            echo ""
            echo "Exemplos:"
            echo "  $0 backup"
            echo "  $0 restore /opt/backups/abmepi/abmepi_backup_20240101_120000.tar.gz"
            echo "  $0 list"
            echo "  $0 cleanup 7"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
