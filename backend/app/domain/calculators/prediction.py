from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class PredictionCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="prediction",
        name="Prediction",
        category="IA e ML",
        description="Vertex AI Prediction: endpoint online (nó-hora n1-standard-4, us-central1).",
        fields=[
            FieldSchema(
                id="node_hours",
                label="Horas de nó de predição",
                type="number",
                unit="nó-hora/mês",
                default=730,
                min=0,
                help="Endpoint ligado o mês inteiro ≈ 730 h. Batch prediction usa outra tabela na página oficial.",
            ),
        ],
        pricing_references=[to_reference(p.VERTEX_PREDICTION_N1_STANDARD_4)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        hours = self.get_number(inputs, "node_hours")
        line_items = [to_line_item(p.VERTEX_PREDICTION_N1_STANDARD_4, hours)]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Preço Default us-central1 para predição online n1-standard-4."],
        )
