from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class AzureAdlsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_adls",
        name="Azure Data Lake Storage Gen2",
        category="Armazenamento",
        provider="azure",
        description="Data lake no Blob Storage com hierarchical namespace (Hot LRS, East US).",
        fields=[
            FieldSchema(id="storage_gb", label="Dados armazenados", type="number", unit="GB", default=1000, min=0),
        ],
        pricing_references=[to_reference(p.AZURE_ADLS_HOT)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AZURE_ADLS_HOT, self.get_number(inputs, "storage_gb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Operações de leitura/escrita e Cool/Archive não estão neste item."],
        )


class AzureSynapseCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_synapse_sql",
        name="Azure Synapse SQL (serverless)",
        category="Warehouse e consulta",
        provider="azure",
        description="Consultas SQL sob demanda sobre o data lake (TB processado).",
        fields=[
            FieldSchema(
                id="processed_tb",
                label="Dados processados",
                type="number",
                unit="TB/mês",
                default=2,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AZURE_SYNAPSE_SERVERLESS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AZURE_SYNAPSE_SERVERLESS, self.get_number(inputs, "processed_tb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Pool dedicado (DWU) é outra tabela. Storage: item ADLS."],
        )


class AzureEventHubsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_event_hubs",
        name="Azure Event Hubs",
        category="Ingestão e Streaming",
        provider="azure",
        description="Ingestão de eventos (Standard: throughput units + ingress).",
        fields=[
            FieldSchema(
                id="tu_hours",
                label="Throughput unit-horas",
                type="number",
                unit="TU-hora/mês",
                default=730,
                min=0,
                help="1 TU o mês inteiro ≈ 730 h.",
            ),
            FieldSchema(
                id="million_events",
                label="Eventos ingeridos",
                type="number",
                unit="milhões/mês",
                default=10,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AZURE_EVENTHUBS_TU), to_reference(p.AZURE_EVENTHUBS_INGRESS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AZURE_EVENTHUBS_TU, self.get_number(inputs, "tu_hours")),
            to_line_item(p.AZURE_EVENTHUBS_INGRESS, self.get_number(inputs, "million_events")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Capture e Premium/Dedicated não estão neste item."],
        )


class AzureDataFactoryCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_data_factory",
        name="Azure Data Factory",
        category="Orquestração",
        provider="azure",
        description="Pipelines de ingestão e transformação (activity runs + DIU de cópia).",
        fields=[
            FieldSchema(
                id="activity_runs",
                label="Activity runs",
                type="number",
                unit="runs/mês",
                default=10000,
                min=0,
            ),
            FieldSchema(
                id="diu_hours",
                label="DIU-horas de cópia",
                type="number",
                unit="DIU-hora/mês",
                default=40,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AZURE_ADF_ACTIVITY), to_reference(p.AZURE_ADF_DIU)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        runs = self.get_number(inputs, "activity_runs") / 1000
        line_items = [
            to_line_item(p.AZURE_ADF_ACTIVITY, runs),
            to_line_item(p.AZURE_ADF_DIU, self.get_number(inputs, "diu_hours")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Data Flows (Spark) e Self-hosted IR são cobrados à parte."],
        )


class AzureStreamAnalyticsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_stream_analytics",
        name="Azure Stream Analytics",
        category="Ingestão e Streaming",
        provider="azure",
        description="Processamento de stream SQL sobre Event Hubs/IoT Hub.",
        fields=[
            FieldSchema(
                id="su_hours",
                label="Streaming unit-horas",
                type="number",
                unit="SU-hora/mês",
                default=730,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AZURE_ASA_SU)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AZURE_ASA_SU, self.get_number(inputs, "su_hours"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Tier Standard. Cluster dedicado é outra tabela."],
        )


class AzureSynapseSparkCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_synapse_spark",
        name="Azure Synapse Spark",
        category="Processamento e Analytics",
        provider="azure",
        description="Apache Spark gerenciado no Synapse (vCore-hora).",
        fields=[
            FieldSchema(
                id="vcore_hours",
                label="vCore-horas",
                type="number",
                unit="vCore-hora/mês",
                default=200,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AZURE_SYNAPSE_SPARK)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AZURE_SYNAPSE_SPARK, self.get_number(inputs, "vcore_hours"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Pause automático reduz horas. Storage: ADLS."],
        )
