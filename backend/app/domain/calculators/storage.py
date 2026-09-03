from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition

_REGION_OPTIONS = [FieldOption(value=region_id, label=label) for region_id, label in p.REGIONS]
_DESTINATION_OPTIONS = [
    FieldOption(value="worldwide", label="Mundial (excl. Ásia/Austrália/China)"),
    FieldOption(value="asia", label="Ásia (excl. China)"),
    FieldOption(value="australia", label="Austrália"),
    FieldOption(value="china", label="China (excl. Hong Kong)"),
]


class StorageCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="storage",
        name="Cloud Storage",
        category="Armazenamento",
        description="Armazenamento de objetos (data lake, buckets de staging, backups).",
        fields=[
            FieldSchema(
                id="region",
                label="Região",
                type="select",
                default="us",
                options=_REGION_OPTIONS,
            ),
            FieldSchema(
                id="storage_class",
                label="Classe de armazenamento",
                type="select",
                default="standard",
                options=[
                    FieldOption(value="standard", label="Standard"),
                    FieldOption(value="nearline", label="Nearline"),
                    FieldOption(value="coldline", label="Coldline"),
                    FieldOption(value="archive", label="Archive"),
                ],
            ),
            FieldSchema(id="storage_gb", label="Dados armazenados", type="number", unit="GB", default=1000, min=0),
            FieldSchema(
                id="class_a_ops_thousands",
                label="Operações Classe A (write/list)",
                type="number",
                unit="milhares de operações/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="class_b_ops_thousands",
                label="Operações Classe B (read/get)",
                type="number",
                unit="milhares de operações/mês",
                default=0,
                min=0,
            ),
            FieldSchema(
                id="egress_destination",
                label="Destino do egress",
                type="select",
                default="worldwide",
                options=_DESTINATION_OPTIONS,
                help="O Google cobra egress por continente de destino, não por par origem/destino livre.",
            ),
            FieldSchema(
                id="egress_gb",
                label="Egress para internet",
                type="number",
                unit="GB/mês",
                default=0,
                min=0,
                help="Primeiros 100GB/mês são gratuitos.",
            ),
        ],
        pricing_references=[
            to_reference(price)
            for region_prices in p.STORAGE_PRICES.values()
            for price in region_prices.values()
        ]
        + [to_reference(price) for price in p.STORAGE_CLASS_A_OPS.values()]
        + [to_reference(price) for price in p.STORAGE_CLASS_B_OPS.values()]
        + [to_reference(price) for price in p.STORAGE_EGRESS_BY_DESTINATION.values()],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        region = self.get_string(inputs, "region", "us")
        storage_class = self.get_string(inputs, "storage_class", "standard")
        region_prices = p.STORAGE_PRICES.get(region, p.STORAGE_PRICES["us"])
        storage_price = region_prices.get(storage_class, region_prices["standard"])
        class_a_price = p.STORAGE_CLASS_A_OPS.get(storage_class, p.STORAGE_CLASS_A_OPS["standard"])
        class_b_price = p.STORAGE_CLASS_B_OPS.get(storage_class, p.STORAGE_CLASS_B_OPS["standard"])

        destination = self.get_string(inputs, "egress_destination", "worldwide")
        egress_price = p.STORAGE_EGRESS_BY_DESTINATION.get(
            destination, p.STORAGE_EGRESS_BY_DESTINATION["worldwide"]
        )

        storage_gb = self.get_number(inputs, "storage_gb")
        class_a_thousands = self.get_number(inputs, "class_a_ops_thousands")
        class_b_thousands = self.get_number(inputs, "class_b_ops_thousands")
        egress_gb = self.get_number(inputs, "egress_gb")
        billable_egress = max(0.0, egress_gb - 100)

        line_items = [
            to_line_item(storage_price, storage_gb),
            to_line_item(class_a_price, class_a_thousands),
            to_line_item(class_b_price, class_b_thousands),
            to_line_item(egress_price, billable_egress),
        ]
        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=[
                "Egress: primeiros 100GB/mês grátis, já descontados acima.",
                "Preço de egress simplificado para a primeira faixa (até 10TiB/mês); acima disso o GB fica mais barato — veja as notas na fonte oficial.",
            ],
        )
