"""Processamento de tags ocultas geradas pelo LLM."""

import logging
import re
from typing import Callable

from src.calendar_service import criar_evento_calendario, remover_evento_calendario
from src.commands import executar_comando, executar_python
from src.config import TAGS_OCULTAS
from src.database import salvar_memoria
from src.finance import buscar_cotacao

logger = logging.getLogger(__name__)


def limpar_texto_para_fala(texto: str) -> str:
    """Remove todas as tags internas e formatação markdown do texto."""
    texto_limpo = texto
    for tag in TAGS_OCULTAS:
        texto_limpo = re.sub(
            rf"\[{tag}\].*?\[/{tag}\]", "", texto_limpo, flags=re.DOTALL
        )
    return re.sub(r"[*#_]", "", texto_limpo)


def processar_tags_ocultas(
    texto: str,
    usuario_atual: str,
    callback_falar: Callable[[str], None],
) -> None:
    """Extrai e executa todas as tags ocultas presentes na resposta do LLM."""
    comandos = re.findall(r"\[CMD\](.*?)\[/CMD\]", texto, flags=re.DOTALL)
    for cmd in comandos:
        logger.info("TAG [CMD]: %s", cmd.strip())
        print(f"\n[Executando comando: {cmd.strip()}]")
        saida = executar_comando(cmd.strip())
        if saida:
            print(f"[Saida do Sistema]: {saida.strip()}")

    blocos_python = re.findall(r"\[PYTHON\](.*?)\[/PYTHON\]", texto, flags=re.DOTALL)
    for codigo in blocos_python:
        logger.info("TAG [PYTHON]: %d caracteres", len(codigo.strip()))
        print("\n[Executando rotina de dados em Python...]")
        saida = executar_python(codigo.strip())
        if saida:
            print(f"[Saida do Script]:\n{saida.strip()}")

    memorias = re.findall(r"\[MEM\](.*?)\[/MEM\]", texto)
    for mem in memorias:
        logger.info("TAG [MEM]: %s", mem)
        print(f"\n[Gravando na memoria: {mem}]")
        salvar_memoria(usuario_atual, mem)

    financas = re.findall(r"\[FINANCE\](.*?)\[/FINANCE\]", texto)
    for ticker in financas:
        logger.info("TAG [FINANCE]: %s", ticker.strip())
        print(f"\n[Acessando Bolsa de Valores: {ticker.strip()}]")
        resultado_fin = buscar_cotacao(ticker.strip())
        print(f"[Mercado]: {resultado_fin}")
        callback_falar(resultado_fin)

    agendas = re.findall(r"\[AGENDA\](.*?)\[/AGENDA\]", texto)
    for ag in agendas:
        logger.info("TAG [AGENDA]: %s", ag.strip())
        print("\n[Acessando Google Calendar...]")
        resultado_ag = criar_evento_calendario(ag.strip())
        print(f"[Google]: {resultado_ag}")
        callback_falar(resultado_ag)

    desmarcacoes = re.findall(r"\[DESMARCAR\](.*?)\[/DESMARCAR\]", texto)
    for dm in desmarcacoes:
        logger.info("TAG [DESMARCAR]: %s", dm.strip())
        print("\n[Removendo evento do Google Calendar...]")
        resultado_dm = remover_evento_calendario(dm.strip())
        print(f"[Google]: {resultado_dm}")
        callback_falar(resultado_dm)
