from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.calculators.base import BaseCalculator
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


def _result(service_id: str, line_items, notes: list[str] | None = None) -> CalculationResult:
    return CalculationResult(
        service_id=service_id,
        line_items=line_items,
        total=round(sum(item.subtotal for item in line_items), 2),
        notes=notes or [],
    )


class DatabricksModelServingCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_model_serving",
        name="Databricks Model Serving",
        category="Machine Learning",
        provider="databricks",
        description="Inferência serverless para modelos e endpoints.",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=730, min=0)
        ],
        pricing_references=[to_reference(p.DBX_MODEL_SERVING)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.DBX_MODEL_SERVING, self.get_number(inputs, "dbus"))],
        )


class DatabricksVectorSearchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_vector_search",
        name="Databricks Vector Search",
        category="Machine Learning",
        provider="databricks",
        description="Índice vetorial gerenciado para aplicações de IA.",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=730, min=0)
        ],
        pricing_references=[to_reference(p.DBX_VECTOR_SEARCH)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.DBX_VECTOR_SEARCH, self.get_number(inputs, "dbus"))],
        )


class DatabricksMonitoringCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dbx_lakehouse_monitoring",
        name="Databricks Lakehouse Monitoring",
        category="Machine Learning",
        provider="databricks",
        description="Monitoramento de qualidade e drift de dados e modelos.",
        fields=[
            FieldSchema(id="dbus", label="DBUs", type="number", unit="DBU/mês", default=100, min=0)
        ],
        pricing_references=[to_reference(p.DBX_LAKEHOUSE_MONITORING)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.DBX_LAKEHOUSE_MONITORING, self.get_number(inputs, "dbus"))],
        )
