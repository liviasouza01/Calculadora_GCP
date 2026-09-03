"""Base contract every GCP service calculator must implement.

This is the extension point of the whole app: to add a new GCP service you
subclass BaseCalculator, provide its `definition` (inputs + official prices)
and its `calculate` formula, then register it in `domain/calculators/registry.py`.
No API route or frontend component needs to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.schemas import CalculationResult, ServiceDefinition


class BaseCalculator(ABC):
    definition: ServiceDefinition

    @abstractmethod
    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        """Turn raw user inputs into a priced, itemized result."""
        raise NotImplementedError

    def get_number(self, inputs: dict[str, float | str], field_id: str) -> float:
        value = inputs.get(field_id, 0)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def get_string(self, inputs: dict[str, float | str], field_id: str, default: str = "") -> str:
        value = inputs.get(field_id, default)
        return str(value) if value is not None else default
