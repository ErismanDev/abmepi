#!/usr/bin/env python3
"""
Script para backup automático do banco de dados ABMEPI
"""

import os
import subprocess
import datetime
import zipfile
from pathlib import Path

def criar_backup():
    """Cria backup completo do banco de dados e arquivos importantes"""
    
    # Configurações
    DB_NAME = "abmepi"
    DB_USER = "postgres"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    # Criar pasta de backup se não existir
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_abmepi_{timestamp}"
    
    print(f"🔄 Iniciando backup do banco {DB_NAME}...")
    
    try:
        # Backup do banco PostgreSQL
        db_backup_file = backup_dir / f"{backup_name}.backup"
        
        cmd = [
            "pg_dump",
            "-h", DB_HOST,
            "-U", DB_USER,
            "-d", DB_NAME,
            "-F", "c",  # Formato personalizado
            "-f", str(db_backup_file)
        ]
        
        print(f"📊 Criando backup do banco: {db_backup_file}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao criar backup do banco:")
            print(f"   {result.stderr}")
            return False
        
        print(f"✅ Backup do banco criado com sucesso!")
        
        # Backup dos arquivos importantes
        files_to_backup = [
            "requirements.txt",
            "env.example",
            "manage.py",
            "README.md",
            "setup.py"
        ]
        
        # Adicionar pastas importantes
        folders_to_backup = [
            "abmepi",
            "core",
            "associados",
            "financeiro",
            "administrativo",
            "beneficios",
            "psicologia",
            "hotel_transito",
            "app",
            "templates",
            "static"
        ]
        
        # Criar arquivo ZIP com arquivos importantes
        zip_backup_file = backup_dir / f"{backup_name}_files.zip"
        
        print(f"📁 Criando backup dos arquivos: {zip_backup_file}")
        
        with zipfile.ZipFile(zip_backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adicionar arquivos
            for file_name in files_to_backup:
                if Path(file_name).exists():
                    zipf.write(file_name)
                    print(f"   ✅ Adicionado: {file_name}")
                else:
                    print(f"   ⚠️  Arquivo não encontrado: {file_name}")
            
            # Adicionar pastas
            for folder_name in folders_to_backup:
                folder_path = Path(folder_name)
                if folder_path.exists() and folder_path.is_dir():
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = Path(root) / file
                            # Excluir arquivos desnecessários
                            if not any(exclude in str(file_path) for exclude in [
                                '__pycache__', '.pyc', '.pyo', '.pyd',
                                '.git', '.venv', 'venv', 'node_modules',
                                '*.log', '*.tmp', '*.bak'
                            ]):
                                zipf.write(file_path)
                    print(f"   ✅ Adicionada pasta: {folder_name}")
                else:
                    print(f"   ⚠️  Pasta não encontrada: {folder_name}")
        
        print(f"✅ Backup dos arquivos criado com sucesso!")
        
        # Criar arquivo de instruções
        instructions_file = backup_dir / f"{backup_name}_instrucoes.md"
        
        instructions_content = f"""# Instruções para Restaurar Backup ABMEPI

**Data do Backup:** {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Arquivos de Backup:**
- `{backup_name}.backup` - Backup completo do banco PostgreSQL
- `{backup_name}_files.zip` - Arquivos do projeto

## Passos para Restaurar:

### 1. Restaurar o Banco
```bash
# Criar banco
createdb -U postgres abmepi

# Restaurar backup
pg_restore -U postgres -d abmepi {backup_name}.backup
```

### 2. Extrair Arquivos
```bash
# Extrair arquivos do projeto
unzip {backup_name}_files.zip
```

### 3. Configurar Ambiente
```bash
# Criar ambiente virtual
python -m venv venv
venv\\Scripts\\activate  # Windows
source venv/bin/activate # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com configurações corretas

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### 4. Testar
```bash
python manage.py runserver
```

---
**Backup criado automaticamente pelo script backup_database.py**
"""
        
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions_content)
        
        print(f"📝 Arquivo de instruções criado: {instructions_file}")
        
        # Estatísticas finais
        db_size = db_backup_file.stat().st_size / (1024 * 1024)  # MB
        zip_size = zip_backup_file.stat().st_size / (1024 * 1024)  # MB
        
        print(f"\n🎉 Backup concluído com sucesso!")
        print(f"📊 Tamanho do backup do banco: {db_size:.2f} MB")
        print(f"📁 Tamanho do backup dos arquivos: {zip_size:.2f} MB")
        print(f"📂 Pasta de backup: {backup_dir.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o backup: {e}")
        return False

def listar_backups():
    """Lista todos os backups disponíveis"""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        print("❌ Nenhum backup encontrado.")
        return
    
    print("📋 Backups disponíveis:")
    print("-" * 50)
    
    backups = []
    for file in backup_dir.glob("backup_abmepi_*"):
        if file.suffix in ['.backup', '.zip']:
            timestamp = file.stem.replace('backup_abmepi_', '')
            try:
                dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                backups.append((dt, file))
            except:
                continue
    
    # Ordenar por data (mais recente primeiro)
    backups.sort(reverse=True)
    
    for dt, file in backups:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"📅 {dt.strftime('%d/%m/%Y %H:%M:%S')} - {file.name} ({size_mb:.2f} MB)")

def limpar_backups_antigos(dias=30):
    """Remove backups mais antigos que X dias"""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        return
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=dias)
    removed_count = 0
    
    print(f"🧹 Removendo backups mais antigos que {dias} dias...")
    
    for file in backup_dir.glob("backup_abmepi_*"):
        timestamp = file.stem.replace('backup_abmepi_', '')
        try:
            dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            if dt < cutoff_date:
                file.unlink()
                removed_count += 1
                print(f"   🗑️  Removido: {file.name}")
        except:
            continue
    
    print(f"✅ {removed_count} backups antigos removidos.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list" or command == "listar":
            listar_backups()
        elif command == "clean" or command == "limpar":
            dias = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            limpar_backups_antigos(dias)
        elif command == "help" or command == "ajuda":
            print("""
🔧 Script de Backup ABMEPI

Uso:
  python backup_database.py          # Criar backup
  python backup_database.py list     # Listar backups
  python backup_database.py clean    # Limpar backups antigos (30 dias)
  python backup_database.py clean 7  # Limpar backups antigos (7 dias)
  python backup_database.py help     # Mostrar esta ajuda

Comandos:
  list/listar    - Lista todos os backups disponíveis
  clean/limpar   - Remove backups antigos (padrão: 30 dias)
  help/ajuda     - Mostra esta mensagem de ajuda
            """)
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("Use 'python backup_database.py help' para ver os comandos disponíveis.")
    else:
        # Comando padrão: criar backup
        success = criar_backup()
        if success:
            print("\n💡 Dica: Use 'python backup_database.py list' para ver todos os backups")
            print("💡 Dica: Use 'python backup_database.py clean' para limpar backups antigos")
        else:
            sys.exit(1)
