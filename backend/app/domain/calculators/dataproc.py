from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition


class DataprocCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dataproc",
        name="Dataproc",
        category="Processamento e Analytics",
        description="Managed Service for Apache Spark: clusters (taxa por vCPU) ou serverless (DCU).",
        fields=[
            FieldSchema(
                id="mode",
                label="Modo",
                type="select",
                default="clusters",
                options=[
                    FieldOption(value="clusters", label="Clusters (taxa de gerenciamento)"),
                    FieldOption(value="serverless", label="Serverless (DCU standard)"),
                ],
            ),
            FieldSchema(
                id="vcpu_hours",
                label="vCPU-horas do cluster",
                type="number",
                unit="vCPU-hora/mês",
                default=14600,
                min=0,
                help="Usado no modo clusters. Ex.: 20 vCPU × 730 h = 14.600. Compute Engine é cobrado à parte.",
            ),
            FieldSchema(
                id="dcu_hours",
                label="DCU-horas serverless",
                type="number",
                unit="DCU-hora/mês",
                default=0,
                min=0,
                help="Usado no modo serverless, tier standard (US$ 0,06/DCU-hora).",
            ),
        ],
        pricing_references=[
            to_reference(p.DATAPROC_CLUSTER_FEE),
            to_reference(p.DATAPROC_SERVERLESS_DCU),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        mode = self.get_string(inputs, "mode", "clusters")
        if mode == "serverless":
            line_items = [to_line_item(p.DATAPROC_SERVERLESS_DCU, self.get_number(inputs, "dcu_hours"))]
            notes = ["Tier standard us-central1. Premium e shuffle são cobrados à parte."]
        else:
            line_items = [to_line_item(p.DATAPROC_CLUSTER_FEE, self.get_number(inputs, "vcpu_hours"))]
            notes = ["Só a taxa Dataproc (US$ 0,01/vCPU-hora). VMs e disco entram em Compute Engine."]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=notes,
        )
