from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class AutomlVisionCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="automl_vision",
        name="Vertex AutoML Vision",
        category="Visão computacional",
        description="Treino e predição de modelos de classificação/detecção de imagem no Vertex AI (AutoML).",
        fields=[
            FieldSchema(
                id="training_hours",
                label="Horas de treino AutoML",
                type="number",
                unit="hora/mês",
                default=8,
                min=0,
                help="Classificação de imagem, us-central1.",
            ),
            FieldSchema(
                id="prediction_node_hours",
                label="Horas de nó de predição online",
                type="number",
                unit="nó-hora/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.AUTOML_VISION_TRAINING),
            to_reference(p.AUTOML_VISION_PREDICTION),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AUTOML_VISION_TRAINING, self.get_number(inputs, "training_hours")),
            to_line_item(p.AUTOML_VISION_PREDICTION, self.get_number(inputs, "prediction_node_hours")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Modelos customizados no Vertex usam também os itens Training e Prediction (n1-standard-4)."],
        )
