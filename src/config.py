"""Configurações centralizadas e constantes do projeto."""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "")

VOZ_PADRAO: str = "pt-BR-AntonioNeural"
ARQUIVO_AUDIO_TEMP: str = "resposta.mp3"

PAUSA_RECONHECIMENTO: float = 2.0
TIMEOUT_ESCUTA: int = 5
DURACAO_AJUSTE_RUIDO: float = 0.5

MODELO_CHAT: str = "qwen2.5:latest"
MODELO_VISAO: str = "moondream"
MODELO_EMBEDDING: str = "nomic-embed-text"

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT: int = 120

PORTA_API: int = 5000

MAX_HISTORICO: int = 50
MAX_HISTORICO_LLM: int = 20

TAGS_OCULTAS: list[str] = [
    "CMD", "MEM", "PYTHON", "FINANCE", "AGENDA", "DESMARCAR",
    "CLIMA", "MEDIA", "EMAIL", "ABRIR",
]

GATILHOS_PESQUISA: list[str] = [
    "pesquise na", "busque na", "internet", "pesquise sobre", "notícia", "procurar na web"
]

# Palavras-chave que acionam o pipeline de visão (Moondream)
# Se qualquer uma aparecer no comando do usuário, a tela é capturada automaticamente
GATILHOS_VISAO: list[str] = [
    "minha tela", "na tela", "na minha tela", "a tela",
    "veja a tela", "olhe a tela", "olha a tela", "olha minha tela",
    "veja minha tela", "olhe minha tela",
    "o que tem na tela", "o que está na tela", "o que aparece na tela",
    "o que tá na tela", "o que ta na tela",
    "o que estou vendo", "o que eu estou vendo", "o que eu tô vendo",
    "o que eu to vendo",
    "screenshot", "print da tela", "captura de tela", "capturar tela",
    "analise a tela", "analisa a tela", "analise minha tela",
    "descreva a tela", "descreve a tela", "descreva minha tela",
    "leia a tela", "lê a tela", "ler a tela",
    "vendo na tela", "mostrando na tela", "aparecendo na tela",
    "o que você vê", "o que voce ve",
    "ver minha tela", "ver a tela",
]

COMANDOS_SAIDA: list[str] = ["sair", "exit", "quit", "fechar", "desligar"]

ESCOPOS_GOOGLE: list[str] = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
]
