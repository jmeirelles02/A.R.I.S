"""Estado global thread-safe do Zeno."""

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class EstadoZeno:
    """Armazena o estado atual do assistente com acesso thread-safe."""

    _lock: Lock = field(default_factory=Lock, repr=False)
    status: str = "ONLINE"
    usuario: str = "Aguardando comando..."
    zeno: str = "Sistemas iniciados."

    def atualizar(self, **kwargs: str) -> None:
        with self._lock:
            for chave, valor in kwargs.items():
                if hasattr(self, chave) and chave != "_lock":
                    setattr(self, chave, valor)

    def to_dict(self) -> dict[str, str]:
        with self._lock:
            return {
                "status": self.status,
                "usuario": self.usuario,
                "zeno": self.zeno,
            }


estado = EstadoZeno()
