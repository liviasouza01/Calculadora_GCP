from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agent.runner import Attachment, run_fill_agent
from app.domain.calculators.registry import get_calculator, list_definitions
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
    conversations: list[UploadFile] = File(...),
    architectures: list[UploadFile] | None = File(None),
    notes: str = Form(""),
) -> dict:
    conversation_files = await _read_uploads(conversations)
    if not conversation_files:
        raise HTTPException(
            status_code=400,
            detail="Anexe ao menos uma transcrição da conversa (PDF, TXT ou Word).",
        )
    architecture_files = await _read_uploads(architectures)

    try:
        result = await run_fill_agent(
            conversations=conversation_files,
            architectures=architecture_files,
            notes=notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao executar o agente: {exc}") from exc

    if not result.filled_services:
        raise HTTPException(
            status_code=422,
            detail=result.summary or "O agente não identificou serviços para preencher.",
        )

    return {
        "filled_services": result.filled_services,
        "summary": result.summary,
    }
