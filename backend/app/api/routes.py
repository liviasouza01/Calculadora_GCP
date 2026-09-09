from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agent.architecture import generate_architecture_png
from app.agent.runner import Attachment, run_fill_agent
from app.domain.calculators.registry import get_calculator, list_definitions
from app.domain.shares import load_share, save_share
from app.domain.schemas import (
    CalculationResult,
    ProjectCalculationRequest,
    ProjectCalculationResult,
    ServiceDefinition,
)

router = APIRouter(prefix="/api")


@router.get("/services", response_model=list[ServiceDefinition])
def get_services() -> list[ServiceDefinition]:
    return list_definitions()


@router.get("/services/{service_id}", response_model=ServiceDefinition)
def get_service(service_id: str) -> ServiceDefinition:
    calculator = get_calculator(service_id)
    if calculator is None:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service_id}'")
    return calculator.definition


@router.post("/services/{service_id}/calculate", response_model=CalculationResult)
def calculate_service(service_id: str, inputs: dict[str, float | str]) -> CalculationResult:
    calculator = get_calculator(service_id)
    if calculator is None:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service_id}'")
    return calculator.calculate(inputs)


@router.post("/calculate/project", response_model=ProjectCalculationResult)
def calculate_project(request: ProjectCalculationRequest) -> ProjectCalculationResult:
    results: list[CalculationResult] = []
    for item in request.items:
        calculator = get_calculator(item.service_id)
        if calculator is None:
            raise HTTPException(status_code=404, detail=f"Unknown service '{item.service_id}'")
        results.append(calculator.calculate(item.inputs))

    grand_total = sum(result.total for result in results)
    return ProjectCalculationResult(results=results, grand_total=grand_total)


async def _read_uploads(files: list[UploadFile] | None) -> list[Attachment]:
    attachments: list[Attachment] = []
    for upload in files or []:
        data = await upload.read()
        if not data:
            continue
        attachments.append(Attachment(name=upload.filename or "arquivo", data=data))
    return attachments


@router.post("/agent/fill")
async def fill_from_briefing(
    files: list[UploadFile] | None = File(default=None),
    notes: str = Form(""),
    intent: str = Form("context"),
    source_provider: str = Form("gcp"),
    target_provider: str = Form("gcp"),
    want_architecture: str = Form("false"),
) -> dict:
    uploaded = await _read_uploads(files)
    if not uploaded and not notes.strip():
        raise HTTPException(
            status_code=400,
            detail="Descreva o projeto ou anexe arquivos (PDF, TXT, CSV, Excel, Word, PNG ou JPG).",
        )
    if intent in {"compare", "complement"} and not uploaded:
        raise HTTPException(
            status_code=400,
            detail="Anexe a calculadora atual (PDF, print, CSV, Excel, Word ou TXT).",
        )
    allowed = {"gcp", "azure", "aws", "databricks", "multicloud"}
    if source_provider not in allowed or target_provider not in allowed:
        raise HTTPException(status_code=400, detail="Provedor inválido.")
    if intent not in {"context", "compare", "complement"}:
        raise HTTPException(status_code=400, detail="Objetivo inválido.")
    if (
        intent == "compare"
        and source_provider == target_provider
        and source_provider != "multicloud"
    ):
        raise HTTPException(status_code=400, detail="Para comparar, escolha outra nuvem de destino.")

    try:
        result = await run_fill_agent(
            files=uploaded,
            notes=notes,
            intent=intent,
            source_provider=source_provider,
            target_provider=target_provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao executar o agente: {exc}") from exc

    if intent in {"compare", "complement"}:
        if not result.filled_as_is and not result.filled_to_be:
            raise HTTPException(
                status_code=422,
                detail=result.summary or "O agente não identificou o AS IS nem o TO-BE.",
            )
    elif not result.filled_services:
        raise HTTPException(
            status_code=422,
            detail=result.summary or "O agente não identificou serviços para preencher.",
        )

    architecture_image = None
    if want_architecture.strip().lower() in {"1", "true", "yes", "on"}:
        try:
            architecture_image = generate_architecture_png(
                result.summary,
                result.filled_to_be or result.filled_services,
            )
        except Exception:
            architecture_image = None

    return {
        "filled_services": result.filled_services,
        "filled_as_is": result.filled_as_is,
        "filled_to_be": result.filled_to_be,
        "summary": result.summary,
        "architecture_image": architecture_image,
    }


@router.post("/shares")
def create_share(payload: dict) -> dict:
    enabled = payload.get("enabled") or {}
    presets = payload.get("presets") or {}
    if not isinstance(enabled, dict) or not isinstance(presets, dict):
        raise HTTPException(status_code=400, detail="Payload inválido.")
    if not any(enabled.values()):
        raise HTTPException(status_code=400, detail="Marque ao menos um serviço para compartilhar.")
    share_id = save_share({"enabled": enabled, "presets": presets})
    return {"id": share_id, "path": f"/s/{share_id}"}


@router.get("/shares/{share_id}")
def get_share(share_id: str) -> dict:
    data = load_share(share_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Link mágico inválido ou expirado.")
    return {
        "id": data.get("id", share_id),
        "enabled": data.get("enabled") or {},
        "presets": data.get("presets") or {},
    }
