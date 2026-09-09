from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition


class DatabricksJobsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_jobs",
        name="Lakeflow Jobs",
        category="Processamento e Analytics",
        provider="databricks",
        description="Pipelines agendados (Jobs Compute classic, AWS Premium list).",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=200, min=0),
            FieldSchema(
                id="cloud_vm_hours",
                label="VM da nuvem",
                type="number",
                unit="instância-hora/mês",
                default=100,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.DBX_JOBS), to_reference(p.DBX_CLOUD_VM)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.DBX_JOBS, self.get_number(inputs, "dbus")),
            to_line_item(p.DBX_CLOUD_VM, self.get_number(inputs, "cloud_vm_hours")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Inclui uma referência de VM AWS para o compute clássico; ajuste ao provedor contratado."],
        )


class DatabricksAllPurposeCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_all_purpose",
        name="All-Purpose Compute",
        category="Processamento e Analytics",
        provider="databricks",
        description="Clusters interativos (notebooks, exploração).",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=80, min=0),
            FieldSchema(
                id="cloud_vm_hours",
                label="VM da nuvem",
                type="number",
                unit="instância-hora/mês",
                default=160,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.DBX_ALL_PURPOSE), to_reference(p.DBX_CLOUD_VM)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.DBX_ALL_PURPOSE, self.get_number(inputs, "dbus")),
            to_line_item(p.DBX_CLOUD_VM, self.get_number(inputs, "cloud_vm_hours")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Inclui uma referência de VM AWS. Prefira Jobs para batch."],
        )


class DatabricksSqlCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_sql",
        name="Databricks SQL",
        category="Warehouse e consulta",
        provider="databricks",
        description="SQL Warehouse para BI e ad-hoc (Classic ou Serverless).",
        fields=[
            FieldSchema(
                id="warehouse_type",
                label="Tipo",
                type="select",
                default="classic",
                options=[
                    FieldOption(value="classic", label="Classic (VM da nuvem à parte)"),
                    FieldOption(value="serverless", label="Serverless (VM inclusa)"),
                ],
            ),
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=100, min=0),
            FieldSchema(
                id="cloud_vm_hours",
                label="VM da nuvem (Classic)",
                type="number",
                unit="instância-hora/mês",
                default=100,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.DBX_SQL_CLASSIC),
            to_reference(p.DBX_SQL_SERVERLESS),
            to_reference(p.DBX_CLOUD_VM),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        kind = self.get_string(inputs, "warehouse_type", "classic")
        price = p.DBX_SQL_SERVERLESS if kind == "serverless" else p.DBX_SQL_CLASSIC
        line_items = [to_line_item(price, self.get_number(inputs, "dbus"))]
        if kind == "classic":
            line_items.append(to_line_item(p.DBX_CLOUD_VM, self.get_number(inputs, "cloud_vm_hours")))
        notes = (
            ["Serverless já embute a infraestrutura da nuvem."]
            if kind == "serverless"
            else ["Classic inclui uma referência de VM AWS; ajuste ao provedor contratado."]
        )
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=notes,
        )


class DatabricksDltCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_dlt",
        name="Lakeflow Declarative Pipelines",
        category="Ingestão e Streaming",
        provider="databricks",
        description="Pipelines declarativos (ex-Delta Live Tables), tier Core.",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=150, min=0),
            FieldSchema(
                id="cloud_vm_hours",
                label="VM da nuvem",
                type="number",
                unit="instância-hora/mês",
                default=100,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.DBX_DLT), to_reference(p.DBX_CLOUD_VM)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.DBX_DLT, self.get_number(inputs, "dbus")),
            to_line_item(p.DBX_CLOUD_VM, self.get_number(inputs, "cloud_vm_hours")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Inclui uma referência de VM AWS. Pro/Advanced e serverless usam outras taxas por DBU."],
        )


class DatabricksStorageCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_storage",
        name="Databricks Storage",
        category="Armazenamento",
        provider="databricks",
        description="Storage gerenciado da plataforma (DSU). O lake na nuvem entra na aba GCP/Azure/AWS.",
        fields=[
            FieldSchema(id="storage_gb", label="Dados gerenciados", type="number", unit="GB", default=1000, min=0),
        ],
        pricing_references=[to_reference(p.DBX_STORAGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.DBX_STORAGE, self.get_number(inputs, "storage_gb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Delta no S3/ADLS/GCS é cobrado no provedor de nuvem."],
        )
