from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class LookerCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="looker",
        name="Looker",
        category="Visualização e BI",
        description=(
            "Plataforma de BI corporativo. A licença de edição/usuários é vendida sob consulta "
            "comercial; o único custo variável publicado é o excedente de tokens do Conversational Analytics."
        ),
        fields=[
            FieldSchema(
                id="extra_input_tokens_millions",
                label="Tokens de entrada excedentes (Conversational Analytics)",
                type="number",
                unit="milhões de tokens/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="extra_output_tokens_millions",
                label="Tokens de saída excedentes (Conversational Analytics)",
                type="number",
                unit="milhões de tokens/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.LOOKER_CONVERSATIONAL_INPUT),
            to_reference(p.LOOKER_CONVERSATIONAL_OUTPUT),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        extra_input = self.get_number(inputs, "extra_input_tokens_millions")
        extra_output = self.get_number(inputs, "extra_output_tokens_millions")

        line_items = [
            to_line_item(p.LOOKER_CONVERSATIONAL_INPUT, extra_input),
            to_line_item(p.LOOKER_CONVERSATIONAL_OUTPUT, extra_output),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[p.LOOKER_LICENSE_NOTE],
        )
