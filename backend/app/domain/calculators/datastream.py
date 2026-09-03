from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class DatastreamCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="datastream",
        name="Datastream",
        category="Ingestão e Streaming",
        description="Change Data Capture (CDC) gerenciado a partir de bancos de dados para o BigQuery/GCS.",
        fields=[
            FieldSchema(
                id="cdc_gib_per_month",
                label="Dados de CDC processados",
                type="number",
                unit="GiB/mês",
                default=100,
                min=0,
            ),
            FieldSchema(
                id="backfill_gib_per_month",
                label="Dados de backfill (carga inicial)",
                type="number",
                unit="GiB/mês",
                default=0,
                min=0,
                help="Primeiros 500 GiB/mês são gratuitos.",
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [p.DATASTREAM_CDC_TIER1, p.DATASTREAM_CDC_TIER2, p.DATASTREAM_BACKFILL]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        cdc_gib = self.get_number(inputs, "cdc_gib_per_month")
        backfill_gib = self.get_number(inputs, "backfill_gib_per_month")

        tier1_gib = min(cdc_gib, 2500)
        tier2_gib = max(0.0, cdc_gib - 2500)
        billable_backfill = max(0.0, backfill_gib - 500)

        line_items = [
            to_line_item(p.DATASTREAM_CDC_TIER1, tier1_gib),
            to_line_item(p.DATASTREAM_CDC_TIER2, tier2_gib),
            to_line_item(p.DATASTREAM_BACKFILL, billable_backfill),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                "Primeiros 500 GiB/mês de backfill são gratuitos, já descontados acima.",
                "Preços de Datastream não puderam ser confirmados ao vivo na última pesquisa — confirme em cloud.google.com/datastream/pricing.",
            ],
        )
