from __future__ import annotations

from fastapi import APIRouter, HTTPException

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
