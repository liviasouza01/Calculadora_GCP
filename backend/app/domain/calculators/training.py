from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class TrainingCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="training",
        name="Training",
        category="IA e ML",
        description="Vertex AI Training: treino customizado de modelos (nó-hora n1-standard-4, us-central1).",
        fields=[
            FieldSchema(
                id="node_hours",
                label="Horas de nó de treino",
                type="number",
                unit="nó-hora/mês",
                default=10,
                min=0,
                help="Máquina n1-standard-4. GPUs e outros machine types são cobrados à parte na página oficial.",
            ),
        ],
        pricing_references=[to_reference(p.VERTEX_TRAINING_N1_STANDARD_4)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        hours = self.get_number(inputs, "node_hours")
        line_items = [to_line_item(p.VERTEX_TRAINING_N1_STANDARD_4, hours)]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Preço Default us-central1. Sem duração mínima; cobrança em incrementos de 30 s."],
        )
