from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition

_REGION_OPTIONS = [FieldOption(value=region_id, label=label) for region_id, label in p.REGIONS]


class BigQueryCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="bigquery",
        name="BigQuery",
        category="Processamento e Analytics",
        description="Data warehouse serverless: armazenamento e consultas on-demand.",
        fields=[
            FieldSchema(
                id="region",
                label="Região / local do dataset",
                type="select",
                default="us",
                options=_REGION_OPTIONS,
            ),
            FieldSchema(
                id="pricing_model",
                label="Modelo de cobrança de consultas",
                type="select",
                default="on_demand",
                options=[
                    FieldOption(value="on_demand", label="Sob demanda (por TiB processado)"),
                    FieldOption(value="enterprise", label="BigQuery Enterprise (Editions, por slot-hora)"),
                ],
                help="Enterprise é capacidade reservada pay-as-you-go; sob demanda cobra por dado processado.",
            ),
            FieldSchema(
                id="query_tib_per_month",
                label="Dados processados em consultas",
                type="number",
                unit="TiB/mês",
                default=5,
                min=0,
                help="Usado apenas no modelo sob demanda. Primeiro 1 TiB/mês é gratuito.",
            ),
            FieldSchema(
                id="enterprise_slot_hours",
                label="Capacidade Enterprise utilizada",
                type="number",
                unit="slot-hora/mês",
                default=0,
                min=0,
                help="Usado apenas no modelo BigQuery Enterprise.",
            ),
            FieldSchema(
                id="active_storage_gb",
                label="Armazenamento ativo",
                type="number",
                unit="GB",
                default=500,
                min=0,
            ),
            FieldSchema(
                id="long_term_storage_gb",
                label="Armazenamento de longo prazo",
                type="number",
                unit="GB",
                default=0,
                min=0,
                help="Tabelas/partições sem alteração há 90+ dias.",
            ),
            FieldSchema(
                id="streaming_inserts_gb",
                label="Streaming inserts",
                type="number",
                unit="GB/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [
                *p.BQ_ON_DEMAND_ANALYSIS_BY_REGION.values(),
                *p.BQ_ACTIVE_STORAGE_BY_REGION.values(),
                *p.BQ_LONG_TERM_STORAGE_BY_REGION.values(),
                p.BQ_STREAMING_INSERTS,
                p.BQ_EDITIONS_STANDARD_SLOT,
                p.BQ_EDITIONS_ENTERPRISE_SLOT,
                p.BQ_EDITIONS_ENTERPRISE_PLUS_SLOT,
            ]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        region = self.get_string(inputs, "region", "us")
        active_storage_price = p.BQ_ACTIVE_STORAGE_BY_REGION.get(region, p.BQ_ACTIVE_STORAGE_BY_REGION["us"])
        long_term_storage_price = p.BQ_LONG_TERM_STORAGE_BY_REGION.get(
            region, p.BQ_LONG_TERM_STORAGE_BY_REGION["us"]
        )

        pricing_model = self.get_string(inputs, "pricing_model", "on_demand")
        active_storage_gb = self.get_number(inputs, "active_storage_gb")
        long_term_storage_gb = self.get_number(inputs, "long_term_storage_gb")
        streaming_gb = self.get_number(inputs, "streaming_inserts_gb")

        line_items = [
            to_line_item(active_storage_price, active_storage_gb),
            to_line_item(long_term_storage_price, long_term_storage_gb),
            to_line_item(p.BQ_STREAMING_INSERTS, streaming_gb / 0.2),
        ]
        notes = []

        if pricing_model == "enterprise":
            slot_hours = self.get_number(inputs, "enterprise_slot_hours")
            line_items.insert(0, to_line_item(p.BQ_EDITIONS_ENTERPRISE_SLOT, slot_hours))
            notes.append("Modelo BigQuery Enterprise (Editions): capacidade pay-as-you-go por slot-hora, sem desconto de compromisso de uso.")
        else:
            on_demand_price = p.BQ_ON_DEMAND_ANALYSIS_BY_REGION.get(region, p.BQ_ON_DEMAND_ANALYSIS_BY_REGION["us"])
            query_tib = self.get_number(inputs, "query_tib_per_month")
            billable_tib = max(0.0, query_tib - 1)
            line_items.insert(0, to_line_item(on_demand_price, billable_tib))
            notes.append("Primeiro 1 TiB de consultas por mês é gratuito, já descontado acima.")

        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=notes,
        )
