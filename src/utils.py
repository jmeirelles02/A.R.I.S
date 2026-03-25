"""Funções utilitárias gerais."""

import os


def obter_caminho_desktop() -> str:
    """Detecta o caminho correto da Área de Trabalho no Windows."""
    caminho_usuario = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    caminhos = [
        os.path.join(caminho_usuario, "OneDrive", "Área de Trabalho"),
        os.path.join(caminho_usuario, "OneDrive", "Desktop"),
        os.path.join(caminho_usuario, "Desktop"),
        os.path.join(caminho_usuario, "Área de Trabalho"),
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    return os.path.join(caminho_usuario, "Desktop")
