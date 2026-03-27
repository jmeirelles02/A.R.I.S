"""Execução de comandos do sistema e scripts Python."""

import logging
import os
import re
import subprocess
import sys

logger = logging.getLogger(__name__)

COMANDOS_BLOQUEADOS: list[str] = [
    r"\bdel\b", r"\brmdir\b", r"\brd\b", r"\bformat\b",
    r"\bshutdown\b", r"\brestart\b", r"\breg\b\s+(delete|add)",
    r"\bnet\s+user\b", r"\bnet\s+localgroup\b",
    r"\btakeown\b", r"\bicacls\b",
    r"powershell\s+-enc", r"powershell\s+-e\b",
    r"\brm\s+-rf\b", r"\bmkfs\b",
    r"Invoke-WebRequest", r"Invoke-RestMethod",
    r"DownloadString", r"DownloadFile",
    r"\bcertutil\b.*-urlcache",
    r"\bwmic\b.*delete", r"\bwmic\b.*call\s+terminate",
    r"\btaskkill\b",
]

IMPORTS_BLOQUEADOS: list[str] = [
    r"\bimport\s+shutil\b", r"\bshutil\.rmtree\b",
    r"\bos\.remove\b", r"\bos\.rmdir\b", r"\bos\.unlink\b",
    r"\bos\.system\b", r"\bsubprocess\b",
    r"\bimport\s+socket\b", r"\bimport\s+http\b",
    r"\bimport\s+urllib\b", r"\bimport\s+requests\b",
    r"\bopen\s*\(.*,\s*['\"]w['\"]", r"\bpathlib\.Path.*unlink\b",
]


def comando_e_seguro(comando: str) -> tuple[bool, str]:
    """Verifica se o comando não contém padrões perigosos."""
    comando_lower = comando.lower()
    for padrao in COMANDOS_BLOQUEADOS:
        if re.search(padrao, comando_lower, re.IGNORECASE):
            return False, f"Comando bloqueado por segurança: padrão '{padrao}' detectado."
    return True, ""


def codigo_python_e_seguro(codigo: str) -> tuple[bool, str]:
    """Verifica se o código Python não contém operações perigosas."""
    for padrao in IMPORTS_BLOQUEADOS:
        if re.search(padrao, codigo, re.IGNORECASE):
            return False, f"Código bloqueado por segurança: padrão '{padrao}' detectado."
    return True, ""


def executar_comando(comando: str) -> str:
    """Executa um comando no shell do Windows com validação de segurança."""
    seguro, motivo = comando_e_seguro(comando)
    if not seguro:
        logger.warning("Comando bloqueado: %s | Motivo: %s", comando, motivo)
        return f"Bloqueado: {motivo}"

    logger.info("CMD executado: %s", comando)
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return resultado.stdout
    except subprocess.TimeoutExpired:
        return "Erro: O comando bloqueou o sistema e foi cancelado por tempo excedido."
    except subprocess.CalledProcessError as erro:
        return erro.stderr


def executar_python(codigo: str) -> str:
    """Salva e executa um script Python temporário com validação de segurança."""
    seguro, motivo = codigo_python_e_seguro(codigo)
    if not seguro:
        logger.warning("Código Python bloqueado | Motivo: %s", motivo)
        return f"Bloqueado: {motivo}"

    logger.info("PYTHON executado: %d caracteres", len(codigo))
    caminho = os.path.join(os.environ.get("TEMP", os.getcwd()), "aris_script.py")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(codigo)
    try:
        resultado = subprocess.run(
            [sys.executable, caminho],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return resultado.stdout if resultado.stdout else "Executado sem saida visual."
    except subprocess.TimeoutExpired:
        return "Erro de Timeout."
    except subprocess.CalledProcessError as e:
        return e.stderr
