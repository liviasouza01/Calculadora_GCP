from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class DataflowCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dataflow",
        name="Dataflow",
        category="Processamento e Analytics",
        description="Processamento de dados em lote e streaming (Apache Beam gerenciado).",
        fields=[
            FieldSchema(id="vcpu_hours", label="vCPU-horas", type="number", unit="vCPU-hora/mês", default=100, min=0),
            FieldSchema(
                id="memory_gb_hours", label="Memória", type="number", unit="GB-hora/mês", default=400, min=0
            ),
            FieldSchema(
                id="disk_gb_hours", label="Persistent Disk", type="number", unit="GB-hora/mês", default=200, min=0
            ),
        ],
        pricing_references=[
            to_reference(price) for price in [p.DATAFLOW_VCPU, p.DATAFLOW_MEMORY, p.DATAFLOW_PD]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        vcpu_hours = self.get_number(inputs, "vcpu_hours")
        memory_hours = self.get_number(inputs, "memory_gb_hours")
        disk_hours = self.get_number(inputs, "disk_gb_hours")

        line_items = [
            to_line_item(p.DATAFLOW_VCPU, vcpu_hours),
            to_line_item(p.DATAFLOW_MEMORY, memory_hours),
            to_line_item(p.DATAFLOW_PD, disk_hours),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                "Preços de Dataflow não puderam ser confirmados ao vivo na última pesquisa — confirme em cloud.google.com/dataflow/pricing.",
            ],
        )
