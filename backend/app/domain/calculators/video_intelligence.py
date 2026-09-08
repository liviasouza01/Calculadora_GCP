from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class VideoIntelligenceCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="video_intelligence",
        name="Video Intelligence API",
        category="Visão computacional",
        description="Anotação de vídeo armazenado: labels, shots, objetos e conteúdo explícito.",
        fields=[
            FieldSchema(
                id="label_minutes",
                label="Label detection",
                type="number",
                unit="minuto/mês",
                default=1000,
                min=0,
                help="Primeiros 1.000 minutos/mês são gratuitos. Frações arredondam para cima no faturamento real.",
            ),
            FieldSchema(
                id="shot_minutes",
                label="Shot detection",
                type="number",
                unit="minuto/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="object_minutes",
                label="Object tracking",
                type="number",
                unit="minuto/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="explicit_minutes",
                label="Explicit content detection",
                type="number",
                unit="minuto/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.VIDEO_LABEL),
            to_reference(p.VIDEO_SHOT),
            to_reference(p.VIDEO_OBJECT),
            to_reference(p.VIDEO_EXPLICIT),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        def billed(minutes: float) -> float:
            return max(0.0, minutes - 1000)

        line_items = [
            to_line_item(p.VIDEO_LABEL, billed(self.get_number(inputs, "label_minutes"))),
            to_line_item(p.VIDEO_SHOT, billed(self.get_number(inputs, "shot_minutes"))),
            to_line_item(p.VIDEO_OBJECT, billed(self.get_number(inputs, "object_minutes"))),
            to_line_item(p.VIDEO_EXPLICIT, billed(self.get_number(inputs, "explicit_minutes"))),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(item.subtotal for item in line_items), 2),
            notes=["Vídeo armazenado (não streaming). 1.000 min grátis por feature já descontados."],
        )
