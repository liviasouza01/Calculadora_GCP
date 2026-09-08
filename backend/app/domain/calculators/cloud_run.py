from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class CloudRunCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="cloud_run",
        name="Cloud Run",
        category="Compute",
        description="Servir APIs de inferência (visão, Vertex). CPU alocada no request, us-central1.",
        fields=[
            FieldSchema(
                id="vcpu_hours",
                label="vCPU-horas",
                type="number",
                unit="vCPU-hora/mês",
                default=50,
                min=0,
            ),
            FieldSchema(
                id="memory_gib_hours",
                label="Memória",
                type="number",
                unit="GiB-hora/mês",
                default=50,
                min=0,
            ),
            FieldSchema(
                id="requests_millions",
                label="Requisições",
                type="number",
                unit="milhões/mês",
                default=2,
                min=0,
                help="Primeiros 2 milhões/mês são gratuitos.",
            ),
        ],
        pricing_references=[
            to_reference(p.CLOUD_RUN_VCPU),
            to_reference(p.CLOUD_RUN_MEMORY),
            to_reference(p.CLOUD_RUN_REQUESTS),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        requests = max(0.0, self.get_number(inputs, "requests_millions") - 2)
        line_items = [
            to_line_item(p.CLOUD_RUN_VCPU, self.get_number(inputs, "vcpu_hours")),
            to_line_item(p.CLOUD_RUN_MEMORY, self.get_number(inputs, "memory_gib_hours")),
            to_line_item(p.CLOUD_RUN_REQUESTS, requests),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["CPU always-on e GPU no Cloud Run têm outras tabelas na página oficial."],
        )
