from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition

_AGENT_REGION_PRICES = {
    "na": p.STS_AGENT_NA,
    "eu": p.STS_AGENT_EU,
    "apac": p.STS_AGENT_APAC,
}


class DataTransferCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="data_transfer",
        name="Data Transfer (Storage Transfer / BigQuery DTS)",
        category="Ingestão e Streaming",
        description=(
            "\"Data Transfer\" não é um produto próprio na calculadora oficial do Google: o egress de "
            "rede é cobrado por continente de destino (veja o campo de egress dentro do Cloud Storage). "
            "Aqui modelamos a única precificação própria e documentada para mover dados de outra origem "
            "para o GCP: Storage Transfer Service (origem = on-premises ou outra nuvem) e BigQuery Data "
            "Transfer Service (ingestão agendada, gratuita para as fontes suportadas)."
        ),
        fields=[
            FieldSchema(
                id="onprem_to_cloud_gb",
                label="Origem: on-premises → Destino: Cloud Storage",
                type="number",
                unit="GB/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="agent_region",
                label="Origem: região do agente de transferência (cloud-to-cloud)",
                type="select",
                default="na",
                options=[
                    FieldOption(value="na", label="América do Norte"),
                    FieldOption(value="eu", label="Europa"),
                    FieldOption(value="apac", label="Ásia-Pacífico"),
                ],
            ),
            FieldSchema(
                id="agent_cloud_to_cloud_gib",
                label="Cloud-to-cloud via agente (ex.: S3 → GCS por rede privada)",
                type="number",
                unit="GiB/mês",
                default=0,
                min=0,
                help="Transferências GCS↔GCS ou S3→GCS via API nativa são gratuitas (não incluir aqui).",
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [
                p.STS_ONPREM_TO_CLOUD,
                p.STS_AGENT_NA,
                p.STS_AGENT_EU,
                p.STS_AGENT_APAC,
                p.BQ_DTS_FREE,
            ]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        onprem_gb = self.get_number(inputs, "onprem_to_cloud_gb")
        region = self.get_string(inputs, "agent_region", "na")
        agent_gib = self.get_number(inputs, "agent_cloud_to_cloud_gib")
        agent_price = _AGENT_REGION_PRICES.get(region, p.STS_AGENT_NA)

        line_items = [
            to_line_item(p.STS_ONPREM_TO_CLOUD, onprem_gb),
            to_line_item(agent_price, agent_gib),
            to_line_item(p.BQ_DTS_FREE, 1),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                "O Google não expõe um seletor livre de origem+destino para transferência: a cobrança de rede é por continente de DESTINO (ver Cloud Storage → egress) ou, aqui, pela região do agente de origem no Storage Transfer Service.",
                "Transferências GCS↔GCS ou via API nativa (S3, Azure Blob) são gratuitas — você paga só o armazenamento de destino.",
                "BigQuery Data Transfer Service é gratuito para as fontes suportadas listadas; conectores de terceiros usam cobrança por slot-hora à parte.",
                "Preços de Storage Transfer Service não puderam ser confirmados ao vivo na última pesquisa — confirme em cloud.google.com/storage-transfer/pricing.",
            ],
        )
