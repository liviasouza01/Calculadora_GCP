from __future__ import annotations

from app.data.pricing import Price
from app.domain.schemas import LineItem, PricingReference


def to_reference(price: Price) -> PricingReference:
    notes = price.notes
    if not price.verified:
        flag = "Preço não confirmado ao vivo na última pesquisa — verifique na fonte oficial."
        notes = f"{notes} {flag}" if notes else flag
    return PricingReference(
        label=price.label,
        unit=price.unit,
        unit_price=price.unit_price,
        source_url=price.source_url,
        last_verified=price.last_verified,
        notes=notes,
    )


def to_line_item(price: Price, quantity: float) -> LineItem:
    return LineItem(
        label=price.label,
        quantity=round(quantity, 4),
        unit=price.unit,
        unit_price=price.unit_price,
        subtotal=round(quantity * price.unit_price, 4),
        source_url=price.source_url,
    )
