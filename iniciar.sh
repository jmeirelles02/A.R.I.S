#!/bin/bash
echo ">> Iniciando A.R.I.S no modo Linux..."

# Ativar venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Erro: venv não encontrado. Execute ./setup.sh primeiro."
    exit 1
fi

# Roda o backend no background
python3 main.py &
BACKEND_PID=$!

sleep 3

# Carregar novo compilador Rust (rustup) caso exista
if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

cd Agent-ui
npm run tauri dev

# Finaliza o backend ao fechar o front-end
kill $BACKEND_PID
