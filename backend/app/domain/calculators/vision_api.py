from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


def _vision_thousands(units: float) -> float:
    return max(0.0, units - 1000) / 1000


class VisionApiCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="vision_api",
        name="Cloud Vision API",
        category="Visão computacional",
        description="Análise de imagens pré-treinada: labels, OCR, objetos e web detection.",
        fields=[
            FieldSchema(
                id="label_units",
                label="Label Detection",
                type="number",
                unit="imagens/mês",
                default=1000,
                min=0,
                help="Primeiras 1.000 unidades/mês são gratuitas. Cada feature na mesma imagem é uma unidade.",
            ),
            FieldSchema(
                id="ocr_units",
                label="Text / Document Text Detection (OCR)",
                type="number",
                unit="imagens/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="object_units",
                label="Object Localization",
                type="number",
                unit="imagens/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="web_units",
                label="Web Detection",
                type="number",
                unit="imagens/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.VISION_LABEL),
            to_reference(p.VISION_OCR),
            to_reference(p.VISION_OBJECT),
            to_reference(p.VISION_WEB),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.VISION_LABEL, _vision_thousands(self.get_number(inputs, "label_units"))),
            to_line_item(p.VISION_OCR, _vision_thousands(self.get_number(inputs, "ocr_units"))),
            to_line_item(p.VISION_OBJECT, _vision_thousands(self.get_number(inputs, "object_units"))),
            to_line_item(p.VISION_WEB, _vision_thousands(self.get_number(inputs, "web_units"))),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=[
                "Franquia de 1.000 unidades/mês por feature já descontada. Faixa 1.001–5.000.000.",
            ],
        )
