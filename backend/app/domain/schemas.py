"""Shared domain schemas used across every service calculator.

Keeping these generic (instead of one bespoke schema per GCP service) is what
lets the API and the frontend stay service-agnostic: adding a new GCP
service later only means adding a new calculator module, not new endpoints
or new UI components.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

FieldType = Literal["number", "select"]


class FieldOption(BaseModel):
    value: str
    label: str


class FieldSchema(BaseModel):
    """Describes one input the user must fill in, generically enough that
    the frontend can render it without knowing which GCP service it belongs to.
    """

    id: str
    label: str
    type: FieldType
    unit: Optional[str] = None
    default: float | str | None = None
    min: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[FieldOption]] = None
    help: Optional[str] = None


class PricingReference(BaseModel):
    """One official Google Cloud price point, always carrying its source
    so the UI can show "where this number came from" next to the result.
    """

    label: str
    unit: str
    unit_price: float
    source_url: str
    last_verified: str
    notes: Optional[str] = None


CloudProvider = Literal["gcp", "azure", "aws", "databricks"]


class ServiceDefinition(BaseModel):
    id: str
    name: str
    category: str
    description: str
    fields: list[FieldSchema]
    pricing_references: list[PricingReference]
    provider: CloudProvider = "gcp"


class LineItem(BaseModel):
    label: str
    quantity: float
    unit: str
    unit_price: float
    subtotal: float
    source_url: str


class CalculationResult(BaseModel):
    service_id: str
    currency: str = "USD"
    line_items: list[LineItem]
    total: float
    notes: list[str] = Field(default_factory=list)


class ProjectCalculationItem(BaseModel):
    service_id: str
    inputs: dict[str, float | str]


class ProjectCalculationRequest(BaseModel):
    items: list[ProjectCalculationItem]


class ProjectCalculationResult(BaseModel):
    currency: str = "USD"
    results: list[CalculationResult]
    grand_total: float
