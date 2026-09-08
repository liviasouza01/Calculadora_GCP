from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition


class FeatureStoreCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="feature_store",
        name="Vertex Feature Store",
        category="IA e ML",
        description=(
            "Feature engineering e serving online (Feature Store novo, us-central1). "
            "Offline fica no BigQuery — some o item BigQuery à parte."
        ),
        fields=[
            FieldSchema(
                id="processing_node_hours",
                label="Horas de nó de feature engineering",
                type="number",
                unit="nó-hora/mês",
                default=300,
                min=0,
                help="Ingestão, transformação e monitoramento. ~1 nó-hora por 100 MiB ingeridos.",
            ),
            FieldSchema(
                id="serving_mode",
                label="Serving online",
                type="select",
                default="optimized",
                options=[
                    FieldOption(value="none", label="Só offline (BigQuery)"),
                    FieldOption(value="optimized", label="Optimized (baixa latência / embeddings)"),
                    FieldOption(value="bigtable", label="Bigtable"),
                ],
            ),
            FieldSchema(
                id="serving_node_hours",
                label="Horas de nó de serving",
                type="number",
                unit="nó-hora/mês",
                default=1460,
                min=0,
                help="Réplicas × 730 h. Optimized cobra no mínimo 2 réplicas.",
            ),
            FieldSchema(
                id="bigtable_storage_gib",
                label="Armazenamento Bigtable",
                type="number",
                unit="GiB",
                default=0,
                min=0,
                help="Só no modo Bigtable. Custo ≈ GiB × 730 h.",
            ),
        ],
        pricing_references=[
            to_reference(p.VERTEX_FEATURE_PROCESSING),
            to_reference(p.VERTEX_FEATURE_OPTIMIZED_SERVING),
            to_reference(p.VERTEX_FEATURE_BIGTABLE_SERVING),
            to_reference(p.VERTEX_FEATURE_BIGTABLE_STORAGE),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        mode = self.get_string(inputs, "serving_mode", "optimized")
        line_items = [
            to_line_item(p.VERTEX_FEATURE_PROCESSING, self.get_number(inputs, "processing_node_hours")),
        ]
        serving_hours = self.get_number(inputs, "serving_node_hours")
        if mode == "optimized":
            line_items.append(to_line_item(p.VERTEX_FEATURE_OPTIMIZED_SERVING, serving_hours))
        elif mode == "bigtable":
            line_items.append(to_line_item(p.VERTEX_FEATURE_BIGTABLE_SERVING, serving_hours))
            storage_gib = self.get_number(inputs, "bigtable_storage_gib")
            line_items.append(to_line_item(p.VERTEX_FEATURE_BIGTABLE_STORAGE, storage_gib * 730))
        notes = [
            "Feature engineering = nós de data processing. Storage e queries offline: item BigQuery.",
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=notes,
        )
