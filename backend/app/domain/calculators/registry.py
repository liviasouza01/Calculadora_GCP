"""Central registry mapping a service id to its calculator instance.

The API layer only ever talks to this module, never to individual
calculator classes directly, so wiring a new service in is a one-line change.
"""
from __future__ import annotations

from app.domain.calculators.base import BaseCalculator
from app.domain.calculators.bigquery import BigQueryCalculator
from app.domain.calculators.composer import ComposerCalculator
from app.domain.calculators.dataflow import DataflowCalculator
from app.domain.calculators.data_transfer import DataTransferCalculator
from app.domain.calculators.datastream import DatastreamCalculator
from app.domain.calculators.looker import LookerCalculator
from app.domain.calculators.pubsub import PubSubCalculator
from app.domain.calculators.storage import StorageCalculator

_CALCULATORS: list[BaseCalculator] = [
    StorageCalculator(),
    BigQueryCalculator(),
    LookerCalculator(),
    DatastreamCalculator(),
    PubSubCalculator(),
    DataTransferCalculator(),
    DataflowCalculator(),
    ComposerCalculator(),
]

REGISTRY: dict[str, BaseCalculator] = {calc.definition.id: calc for calc in _CALCULATORS}


def list_definitions():
    return [calc.definition for calc in _CALCULATORS]


def get_calculator(service_id: str) -> BaseCalculator | None:
    return REGISTRY.get(service_id)
