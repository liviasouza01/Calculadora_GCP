from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class ComposerCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="composer",
        name="Cloud Composer",
        category="Orquestração",
        description="Apache Airflow gerenciado para orquestrar pipelines de dados.",
        fields=[
            FieldSchema(id="vcpu_hours", label="vCPU-horas", type="number", unit="vCPU-hora/mês", default=200, min=0),
            FieldSchema(
                id="memory_gib_hours", label="Memória", type="number", unit="GiB-hora/mês", default=400, min=0
            ),
            FieldSchema(
                id="storage_gib_hours", label="Armazenamento (workers)", type="number", unit="GiB-hora/mês", default=100, min=0
            ),
            FieldSchema(
                id="db_storage_gb", label="Banco de metadados", type="number", unit="GB", default=10, min=0
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [p.COMPOSER_VCPU, p.COMPOSER_MEMORY, p.COMPOSER_STORAGE, p.COMPOSER_DB_STORAGE]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        vcpu_hours = self.get_number(inputs, "vcpu_hours")
        memory_hours = self.get_number(inputs, "memory_gib_hours")
        storage_hours = self.get_number(inputs, "storage_gib_hours")
        db_storage_gb = self.get_number(inputs, "db_storage_gb")

        line_items = [
            to_line_item(p.COMPOSER_VCPU, vcpu_hours),
            to_line_item(p.COMPOSER_MEMORY, memory_hours),
            to_line_item(p.COMPOSER_STORAGE, storage_hours),
            to_line_item(p.COMPOSER_DB_STORAGE, db_storage_gb),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                "Preços de Cloud Composer não puderam ser confirmados ao vivo na última pesquisa — confirme em cloud.google.com/composer/pricing.",
            ],
        )
