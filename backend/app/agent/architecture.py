"""Gera diagrama de arquitetura a partir da proposta preenchida."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from google import genai
from google.genai import types

from app.domain.calculators.registry import get_calculator

IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
REFERENCE_PNG = Path(__file__).resolve().parent / "assets" / "gcp_architecture_reference.png"

GCP_LAYOUT = (
    "Siga EXATAMENTE o padrão visual da imagem de referência (arquitetura GCP em colunas): "
    "fundo branco, colunas verticais com cabeçalhos coloridos, caixas com ícones oficiais do Google Cloud, "
    "setas azuis da esquerda para a direita, texto em português. "
    "Colunas típicas: Fontes de Dados (cinza), Ingestão / Eventos (roxo), "
    "Lakehouse – Armazenamento com medalhão Bronze / Prata / Ouro (verde), "
    "Transformação / Orquestração (azul), Dados & IA (amarelo), Consumo / Visualização (vermelho). "
    "Barras horizontais embaixo: Governança, Catálogo e Segurança; "
    "Operação, Observabilidade e Infraestrutura. "
    "Não inclua Cloud KMS. Não invente um estilo livre: replique este layout em colunas. "
    "Adapte os serviços das caixas à proposta abaixo, mantendo o mesmo desenho."
)


def _providers(filled: dict[str, dict[str, float | str]]) -> set[str]:
    found: set[str] = set()
    for service_id in filled:
        calculator = get_calculator(service_id)
        if calculator is not None:
            found.add(calculator.definition.provider)
    return found


def generate_architecture_png(
    summary: str,
    filled: dict[str, dict[str, float | str]],
) -> str | None:
    names: list[str] = []
    for service_id in filled:
        calculator = get_calculator(service_id)
        if calculator is None:
            continue
        names.append(f"{calculator.definition.provider}: {calculator.definition.name}")
    if not names and not summary.strip():
        return None

    listed = ", ".join(names[:50]) or "plataforma de dados"
    providers = _providers(filled)
    gcp_only = not providers or providers <= {"gcp"}

    if gcp_only:
        prompt = (
            f"{GCP_LAYOUT} "
            f"Serviços desta proposta: {listed}. "
            f"Texto da proposta: {summary[:1800]}"
        )
    else:
        prompt = (
            "Professional multi-cloud architecture diagram, white background, labeled boxes, "
            "arrows left to right, Portuguese labels. Group by provider. "
            f"Services: {listed}. Proposal: {summary[:1800]}"
        )

    parts: list[types.Part] = []
    if gcp_only and REFERENCE_PNG.exists():
        parts.append(
            types.Part(
                inline_data=types.Blob(mime_type="image/png", data=REFERENCE_PNG.read_bytes())
            )
        )
        parts.append(
            types.Part(
                text="Use esta imagem como padrão visual obrigatório. Gere um diagrama NOVO com os serviços da proposta."
            )
        )
    parts.append(types.Part(text=prompt))

    client = genai.Client()
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=parts,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )
    if not response.candidates:
        return None
    content = response.candidates[0].content
    if content is None or not content.parts:
        return None
    for part in content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is None or not getattr(inline, "data", None):
            continue
        data = inline.data
        if isinstance(data, str):
            return data
        return base64.b64encode(data).decode("ascii")
    return None
