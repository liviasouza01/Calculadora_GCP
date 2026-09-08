from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class SecretManagerCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="secret_manager",
        name="Secret Manager",
        category="Segurança",
        description="Armazenamento e acesso a secrets.",
        fields=[
            FieldSchema(
                id="active_versions",
                label="Versões ativas",
                type="number",
                unit="versões",
                default=6,
                min=0,
                help="Primeiras 6 versões/mês são gratuitas.",
            ),
            FieldSchema(
                id="access_operations",
                label="Operações de acesso",
                type="number",
                unit="ops/mês",
                default=10000,
                min=0,
                help="Primeiras 10.000 são gratuitas.",
            ),
        ],
        pricing_references=[to_reference(p.SECRET_VERSION), to_reference(p.SECRET_ACCESS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        versions = max(0.0, self.get_number(inputs, "active_versions") - 6)
        access_blocks = max(0.0, self.get_number(inputs, "access_operations") - 10_000) / 10_000
        line_items = [
            to_line_item(p.SECRET_VERSION, versions),
            to_line_item(p.SECRET_ACCESS, access_blocks),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Franquias Always Free já descontadas."],
        )
