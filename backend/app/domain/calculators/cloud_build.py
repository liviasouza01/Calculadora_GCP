from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class CloudBuildCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="cloud_build",
        name="Cloud Build",
        category="CI/CD",
        description="Builds gerenciados. Máquina padrão e2-standard-2.",
        fields=[
            FieldSchema(
                id="build_minutes",
                label="Minutos de build",
                type="number",
                unit="minuto/mês",
                default=2500,
                min=0,
                help="Primeiros 2.500 minutos/mês por conta de faturamento são gratuitos.",
            ),
        ],
        pricing_references=[to_reference(p.BUILD_E2_STANDARD_2)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        billed = max(0.0, self.get_number(inputs, "build_minutes") - 2500)
        line_items = [to_line_item(p.BUILD_E2_STANDARD_2, billed)]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Franquia de 2.500 min/mês já descontada. Private pool tem outra tabela."],
        )
