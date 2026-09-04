"""Executa o root_agent com Runner + sessão in-memory, como no tutorial ADK."""

from __future__ import annotations

import io
import os
import uuid
from dataclasses import dataclass

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent.agent import root_agent

APP_NAME = "calculadora_gcp"
ALLOWED_CONVERSATION = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_ARCHITECTURE = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
MAX_FILE_BYTES = 12 * 1024 * 1024
MAX_FILES = 20


@dataclass
class AgentFillResult:
    filled_services: dict[str, dict[str, float | str]]
    summary: str


@dataclass
class Attachment:
    name: str
    data: bytes


def _extension(filename: str) -> str:
    name = (filename or "").lower()
    dot = name.rfind(".")
    return name[dot:] if dot >= 0 else ""


def _extract_docx_text(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _conversation_parts(filename: str, data: bytes) -> list[types.Part]:
    ext = _extension(filename)
    mime = ALLOWED_CONVERSATION.get(ext)
    if mime is None:
        raise ValueError(
            "A transcrição deve ser PDF, TXT ou Word (.docx)."
        )
    if ext == ".docx":
        text = _extract_docx_text(data)
        if not text:
            raise ValueError("O arquivo Word está vazio.")
        return [
            types.Part(text=f"Transcrição extraída de {filename}:\n{text}"),
        ]
    if ext == ".txt":
        return [types.Part(text=f"Transcrição ({filename}):\n{data.decode('utf-8', errors='replace')}")]
    return [
        types.Part(text=f"Transcrição em PDF anexada: {filename}"),
        types.Part(inline_data=types.Blob(mime_type=mime, data=data)),
    ]


def _architecture_parts(filename: str, data: bytes) -> list[types.Part]:
    ext = _extension(filename)
    mime = ALLOWED_ARCHITECTURE.get(ext)
    if mime is None:
        raise ValueError("O desenho de arquitetura deve ser PNG ou JPG.")
    return [
        types.Part(text=f"Desenho de arquitetura anexado: {filename}"),
        types.Part(inline_data=types.Blob(mime_type=mime, data=data)),
    ]


def _require_api_key() -> None:
    if not os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper() not in {
        "TRUE",
        "1",
    }:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY (Google AI Studio) ou autenticação Vertex "
            "(GOOGLE_GENAI_USE_VERTEXAI=TRUE + projeto GCP)."
        )


def _validate_size(name: str, data: bytes) -> None:
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(f"O arquivo '{name}' ultrapassa o limite de 12 MB.")


async def run_fill_agent(
    *,
    conversations: list[Attachment],
    architectures: list[Attachment] | None = None,
    notes: str = "",
) -> AgentFillResult:
    _require_api_key()
    architectures = architectures or []
    if not conversations:
        raise ValueError("Anexe ao menos uma transcrição (PDF, TXT ou Word).")
    total_files = len(conversations) + len(architectures)
    if total_files > MAX_FILES:
        raise ValueError(f"No máximo {MAX_FILES} anexos por envio.")

    for item in conversations + architectures:
        _validate_size(item.name, item.data)

    names = [item.name for item in conversations] + [item.name for item in architectures]
    parts: list[types.Part] = [
        types.Part(
            text=(
                "Preencha a calculadora com base em todos estes anexos: "
                + ", ".join(names)
                + ". "
                + (f"Notas extras do usuário: {notes}" if notes.strip() else "")
            )
        )
    ]
    for item in conversations:
        parts.extend(_conversation_parts(item.name, item.data))
    for item in architectures:
        parts.extend(_architecture_parts(item.name, item.data))

    session_service = InMemorySessionService()
    user_id = "calculator-user"
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    content = types.Content(role="user", parts=parts)

    summary = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            texts = [part.text for part in event.content.parts if getattr(part, "text", None)]
            summary = "\n".join(texts).strip()

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    filled = {}
    if session is not None:
        filled = session.state.get("filled_services", {}) or {}

    return AgentFillResult(filled_services=filled, summary=summary)
