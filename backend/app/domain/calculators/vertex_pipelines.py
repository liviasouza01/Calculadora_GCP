from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class VertexPipelinesCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="vertex_pipelines",
        name="Vertex Pipelines",
        category="IA e ML",
        description="Orquestração de treino, feature engineering e deploy (taxa por run).",
        fields=[
            FieldSchema(
                id="pipeline_runs",
                label="Execuções de pipeline",
                type="number",
                unit="runs/mês",
                default=30,
                min=0,
                help="US$ 0,03 por run. VMs, Dataflow e Feature Store dos componentes entram nos outros itens.",
            ),
        ],
        pricing_references=[to_reference(p.VERTEX_PIPELINE_RUN)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.VERTEX_PIPELINE_RUN, self.get_number(inputs, "pipeline_runs"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Só a taxa de execução. Some Training, Dataflow ou Feature Store usados pelos steps."],
        )
