from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition

# n1-standard-4: 4 vCPU, 15 GiB
_N1_STANDARD_4_VCPU = 4
_N1_STANDARD_4_GIB = 15


class VertexWorkbenchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="vertex_workbench",
        name="Vertex Workbench",
        category="IA e ML",
        description="Notebooks gerenciados (n1-standard-4, us-central1, inclui taxa de gerenciamento Vertex).",
        fields=[
            FieldSchema(
                id="instances",
                label="Instâncias",
                type="number",
                unit="unidades",
                default=1,
                min=0,
            ),
            FieldSchema(
                id="hours",
                label="Horas ligadas",
                type="number",
                unit="hora/mês",
                default=160,
                min=0,
                help="Notebook ligado o mês inteiro ≈ 730 h. Disco persistente é cobrado à parte no Compute Engine.",
            ),
        ],
        pricing_references=[
            to_reference(p.VERTEX_WORKBENCH_N1_VCPU),
            to_reference(p.VERTEX_WORKBENCH_N1_MEMORY),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        hours = self.get_number(inputs, "instances") * self.get_number(inputs, "hours")
        line_items = [
            to_line_item(p.VERTEX_WORKBENCH_N1_VCPU, hours * _N1_STANDARD_4_VCPU),
            to_line_item(p.VERTEX_WORKBENCH_N1_MEMORY, hours * _N1_STANDARD_4_GIB),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Máquina n1-standard-4. GPUs e disco não estão neste item."],
        )
