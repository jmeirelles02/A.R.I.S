"""Schemas Pydantic para validação da resposta estruturada do LLM."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ValidationError


class SystemAction(BaseModel):
    """Ação que o sistema deve executar após processar a resposta."""

    type: str = Field(pattern="^(CMD|FINANCE|AGENDA|NONE)$")
    payload: Optional[Dict[str, Any]] = None
    confidence: float = Field(ge=0.0, le=1.0)


class SystemResponse(BaseModel):
    """Resposta estruturada obrigatória do modelo Qwen."""

    response: str
    action: SystemAction


def validar_resposta_llm(json_bruto: dict) -> SystemResponse:
    """Valida e converte a saída JSON do Qwen contra o schema Pydantic.

    Args:
        json_bruto: Dicionário parseado da resposta do modelo.

    Returns:
        SystemResponse validado.

    Raises:
        ValidationError: Se o JSON não corresponder ao schema.
    """
    return SystemResponse.model_validate(json_bruto)
