"""Gera diagrama de arquitetura a partir da proposta preenchida."""

from __future__ import annotations

import base64
import os

from google import genai
from google.genai import types

from app.domain.calculators.registry import get_calculator

IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")


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
    prompt = (
        "Professional cloud architecture diagram for a data, ML and computer vision project. "
        "Clean white background, rounded boxes, clear arrows for data flow, readable labels, "
        "no watermark, no marketing text. Group by cloud when more than one provider appears. "
        f"Services to include: {listed}. "
        f"Proposal: {summary[:1800]}"
    )
    client = genai.Client()
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
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
