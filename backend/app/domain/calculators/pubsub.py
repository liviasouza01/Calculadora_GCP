from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, LineItem, ServiceDefinition


class PubSubCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="pubsub",
        name="Pub/Sub",
        category="Ingestão e Streaming",
        description="Mensageria assíncrona para pipelines de eventos em tempo real.",
        fields=[
            FieldSchema(
                id="throughput_gib_per_month",
                label="Volume publicado + entregue",
                type="number",
                unit="GiB/mês",
                default=100,
                min=0,
                help="Primeiros 10 GiB/mês são gratuitos.",
            ),
        ],
        pricing_references=[to_reference(p.PUBSUB_THROUGHPUT)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        throughput_gib = self.get_number(inputs, "throughput_gib_per_month")
        free_gib = min(10.0, throughput_gib)
        billable_gib = max(0.0, throughput_gib - 10)
        billable_tib = billable_gib / 1024

        line_items = [
            LineItem(
                label="Franquia gratuita (primeiros 10 GiB/mês)",
                quantity=round(free_gib, 4),
                unit="GiB",
                unit_price=0.0,
                subtotal=0.0,
                source_url=p.PUBSUB_SOURCE,
            ),
            to_line_item(p.PUBSUB_THROUGHPUT, billable_tib),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                (
                    f"{throughput_gib:g} GiB informados − {free_gib:g} GiB grátis "
                    f"= {billable_gib:g} GiB cobrados. "
                    f"O Google cobra por TiB (1 TiB = 1024 GiB), então "
                    f"{billable_gib:g} / 1024 = {billable_tib:.4f} TiB × US$ 40."
                ),
            ],
        )
