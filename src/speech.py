"""Síntese e reconhecimento de voz (TTS e STT)."""

import logging
import os
import subprocess

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
except Exception:
    HAS_KEYBOARD = False

import pygame
import speech_recognition as sr

from src.config import (
    ARQUIVO_AUDIO_TEMP,
    DURACAO_AJUSTE_RUIDO,
    PAUSA_RECONHECIMENTO,
    TIMEOUT_ESCUTA,
    VOZ_PADRAO,
)
from src.state import estado
from src.tags import limpar_texto_para_fala

logger = logging.getLogger(__name__)


def falar(texto: str) -> None:
    """Converte texto em fala usando edge-tts e reproduz via pygame."""
    texto_limpo = limpar_texto_para_fala(texto)
    if not texto_limpo.strip():
        return

    estado.atualizar(status="FALANDO...")

    try:
        subprocess.run(
            [
                "edge-tts",
                "--voice", VOZ_PADRAO,
                "--text", texto_limpo,
                "--write-media", ARQUIVO_AUDIO_TEMP,
            ],
            check=True,
        )
        pygame.mixer.music.load(ARQUIVO_AUDIO_TEMP)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if HAS_KEYBOARD:
                try:
                    if keyboard.is_pressed("space"):
                        pygame.mixer.music.stop()
                        print("\n[A.R.I.S interrompido]")
                        break
                except Exception:
                    pass
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        if os.path.exists(ARQUIVO_AUDIO_TEMP):
            os.remove(ARQUIVO_AUDIO_TEMP)
    except FileNotFoundError:
        logger.error("edge-tts não encontrado. Verifique a instalação.")
    except pygame.error as e:
        logger.error("Erro do pygame ao reproduzir áudio: %s", e)
    except Exception as e:
        logger.error("Erro de áudio: %s", e)


def ouvir() -> str:
    """Captura áudio do microfone e converte em texto via Google Speech."""
    reconhecedor = sr.Recognizer()
    reconhecedor.pause_threshold = PAUSA_RECONHECIMENTO
    with sr.Microphone() as fonte:
        estado.atualizar(status="OUVINDO...")
        print("\n[A.R.I.S ouvindo...]")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=DURACAO_AJUSTE_RUIDO)
        try:
            audio = reconhecedor.listen(fonte, timeout=TIMEOUT_ESCUTA)
            texto = reconhecedor.recognize_google(audio, language="pt-BR")
            print(f"Voce (Voz): {texto}")
            return texto
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            logger.warning("Erro no reconhecimento de voz: %s", e)
            return ""
