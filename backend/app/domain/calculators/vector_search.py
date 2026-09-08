from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class VectorSearchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="vector_search",
        name="Vertex Vector Search",
        category="IA e ML",
        description="Índice ANN para embeddings (serving e2-standard-2 + build de índice, us-central1).",
        fields=[
            FieldSchema(
                id="node_hours",
                label="Horas de nó de serving",
                type="number",
                unit="nó-hora/mês",
                default=730,
                min=0,
                help="1 nó e2-standard-2 o mês inteiro ≈ 730 h. QPS alto exige mais nós.",
            ),
            FieldSchema(
                id="index_gib",
                label="Dados processados no build/update",
                type="number",
                unit="GiB/mês",
                default=1,
                min=0,
                help="Tamanho ≈ vetores × dimensões × 4 bytes. Cobrado a cada rebuild.",
            ),
        ],
        pricing_references=[
            to_reference(p.VERTEX_VECTOR_E2_STANDARD_2),
            to_reference(p.VERTEX_VECTOR_INDEX_BUILD),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.VERTEX_VECTOR_E2_STANDARD_2, self.get_number(inputs, "node_hours")),
            to_line_item(p.VERTEX_VECTOR_INDEX_BUILD, self.get_number(inputs, "index_gib")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Streaming inserts (US$ 0,45/GiB) e CUs storage-optimized não estão neste item."],
        )
