"""Busca de informações na internet via DuckDuckGo."""

import logging

from ddgs import DDGS

logger = logging.getLogger(__name__)


def buscar_na_internet(consulta: str) -> str:
    """Pesquisa na web e retorna resultados compilados em texto."""
    try:
        resultados = DDGS().text(consulta, region="br-pt", timelimit="w", max_results=3)
        if not resultados:
            resultados = DDGS().text(consulta, region="br-pt", timelimit="m", max_results=3)
        if not resultados:
            return "Nenhuma informacao recente encontrada."

        texto_compilado = "Dados extraidos da internet:\n"
        for r in resultados:
            texto_compilado += f"* Titulo: {r['title']}\n  Resumo: {r['body']}\n"
        return texto_compilado
    except Exception as e:
        logger.error("Falha na conexão com a rede externa: %s", e)
        return f"Falha na conexao com a rede externa: {e}"
