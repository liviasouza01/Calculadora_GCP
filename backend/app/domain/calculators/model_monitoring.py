from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class ModelMonitoringCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="model_monitoring",
        name="Vertex Model Monitoring",
        category="IA e ML",
        description="Drift e qualidade do modelo em produção: GB de treino + logs de predição analisados.",
        fields=[
            FieldSchema(
                id="analyzed_gb",
                label="Dados analisados",
                type="number",
                unit="GB/mês",
                default=5,
                min=0,
                help="Dataset de treino (setup, uma vez) + janelas de prediction logs convertidas para TfRecord.",
            ),
        ],
        pricing_references=[to_reference(p.VERTEX_MODEL_MONITORING)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.VERTEX_MODEL_MONITORING, self.get_number(inputs, "analyzed_gb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["BigQuery usado para logs de predição entra no item BigQuery."],
        )
