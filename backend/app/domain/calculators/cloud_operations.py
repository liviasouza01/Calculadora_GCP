from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, LineItem, ServiceDefinition


class CloudOperationsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="cloud_operations",
        name="Cloud Operations",
        category="Observabilidade",
        description="Logging, Monitoring e Trace (Google Cloud Observability).",
        fields=[
            FieldSchema(
                id="logging_gib",
                label="Cloud Logging — volume ingerido",
                type="number",
                unit="GiB/mês",
                default=50,
                min=0,
                help="Primeiros 50 GiB/projeto/mês são gratuitos.",
            ),
            FieldSchema(
                id="monitoring_mib",
                label="Cloud Monitoring — métricas ingeridas",
                type="number",
                unit="MiB/mês",
                default=150,
                min=0,
                help="Primeiros 150 MiB/conta são gratuitos. Taxa da 1ª faixa cobrada.",
            ),
            FieldSchema(
                id="trace_million_spans",
                label="Cloud Trace — spans ingeridos",
                type="number",
                unit="milhões de spans/mês",
                default=0,
                min=0,
                help="Primeiros 2,5 milhões de spans/conta são gratuitos.",
            ),
        ],
        pricing_references=[
            to_reference(p.OPS_LOGGING_INGEST),
            to_reference(p.OPS_MONITORING_INGEST),
            to_reference(p.OPS_TRACE_INGEST),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        logging_gib = max(0.0, self.get_number(inputs, "logging_gib") - 50)
        monitoring_mib = max(0.0, self.get_number(inputs, "monitoring_mib") - 150)
        trace_millions = max(0.0, self.get_number(inputs, "trace_million_spans") - 2.5)
        line_items: list[LineItem] = [
            to_line_item(p.OPS_LOGGING_INGEST, logging_gib),
            to_line_item(p.OPS_MONITORING_INGEST, monitoring_mib),
            to_line_item(p.OPS_TRACE_INGEST, trace_millions),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=[
                "Franquias gratuitas já descontadas. Error Reporting não tem cobrança própria.",
            ],
        )
