#!/bin/bash

# ----------------------------
# CONFIGURAÇÕES
# ----------------------------
REPO_URL="https://github.com/SeuUsuario/MeuProjeto.git"
PROJECT_DIR="$HOME/MeuProjeto"
BACKUP_DIR="$PROJECT_DIR/backup"
DATA_DIR="$PROJECT_DIR/data"        # Pasta onde você gera arquivos importantes
BRANCH="main"

# ----------------------------
# 1️⃣ Clonar ou atualizar o repositório
# ----------------------------
if [ -d "$PROJECT_DIR" ]; then
    echo "Repositório já existe. Atualizando..."
    cd "$PROJECT_DIR"
    git pull origin $BRANCH
else
    echo "Clonando repositório..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ----------------------------
# 2️⃣ Instalar dependências Python
# ----------------------------
if [ -f "requirements.txt" ]; then
    echo "Instalando dependências Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Arquivo requirements.txt não encontrado. Pulei instalação de pacotes."
fi

# ----------------------------
# 3️⃣ Criar pastas de backup e data
# ----------------------------
mkdir -p "$BACKUP_DIR"
mkdir -p "$DATA_DIR"
echo "Pastas de backup e data verificadas."

# ----------------------------
# 4️⃣ Backup automático dos arquivos de dados
# ----------------------------
echo "Fazendo backup automático dos arquivos de dados..."

cd "$PROJECT_DIR"
git add "$DATA_DIR"  # Adiciona novos arquivos de data
if ! git diff-index --quiet HEAD --; then
    git commit -m "Backup automático dos arquivos de dados"
    git push origin $BRANCH
    echo "Backup concluído e enviado para o GitHub!"
else
    echo "Nenhuma alteração nova para backup."
fi

echo "Setup e backup concluídos. Projeto pronto para uso!"
