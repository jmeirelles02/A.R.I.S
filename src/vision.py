"""Captura de tela e conversão para Base64 usando Pillow."""

import base64
import io
import logging
import platform

logger = logging.getLogger(__name__)


def capturar_tela_base64() -> str | None:
    """Captura a tela inteira e retorna como string Base64 (PNG).

    Utiliza PIL.ImageGrab no Windows/macOS e fallback via subprocess
    no Linux (que não suporta ImageGrab nativamente sem display X11).

    Returns:
        String Base64 da imagem PNG ou None se a captura falhar.
    """
    try:
        sistema = platform.system()

        if sistema == "Linux":
            imagem = _capturar_linux()
        else:
            from PIL import ImageGrab
            imagem = ImageGrab.grab()

        if imagem is None:
            logger.warning("Captura de tela retornou None.")
            return None

        buffer = io.BytesIO()
        imagem.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        b64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
        logger.info(
            "Tela capturada com sucesso (%dx%d, %d bytes B64).",
            imagem.width,
            imagem.height,
            len(b64_string),
        )
        return b64_string

    except ImportError as e:
        logger.error("Pillow não instalado ou módulo ausente: %s", e)
        return None
    except Exception as e:
        logger.error("Falha na captura de tela: %s", e)
        return None


def _capturar_linux():
    """Captura de tela no Linux usando ferramentas disponíveis.

    Tenta, nesta ordem:
    1. PIL.ImageGrab (requer xdisplay no Pillow >= 9.2)
    2. subprocess + scrot
    3. subprocess + gnome-screenshot
    """
    # Tentativa 1: Pillow nativo (experimental em Linux)
    try:
        from PIL import ImageGrab
        imagem = ImageGrab.grab()
        if imagem is not None:
            return imagem
    except Exception:
        pass

    # Tentativa 2: scrot via pipe
    try:
        import subprocess
        from PIL import Image

        resultado = subprocess.run(
            ["scrot", "-o", "/tmp/aris_screenshot.png"],
            capture_output=True,
            timeout=5,
        )
        if resultado.returncode == 0:
            return Image.open("/tmp/aris_screenshot.png")
    except Exception:
        pass

    # Tentativa 3: gnome-screenshot
    try:
        import subprocess
        from PIL import Image

        resultado = subprocess.run(
            ["gnome-screenshot", "-f", "/tmp/aris_screenshot.png"],
            capture_output=True,
            timeout=5,
        )
        if resultado.returncode == 0:
            return Image.open("/tmp/aris_screenshot.png")
    except Exception:
        pass

    logger.warning("Nenhuma ferramenta de screenshot disponível no Linux.")
    return None


def imagem_base64_de_bytes(dados_bytes: bytes) -> str:
    """Converte bytes de imagem brutos em string Base64.

    Args:
        dados_bytes: Bytes da imagem (PNG/JPEG).

    Returns:
        String Base64 da imagem.
    """
    return base64.b64encode(dados_bytes).decode("utf-8")
