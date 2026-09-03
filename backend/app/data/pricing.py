"""Centralized, cited Google Cloud pricing constants.

Every price here carries the official pricing page it came from and the date
it was checked (`last_verified`), so the UI can show provenance next to each
number. Google Cloud prices change over time and vary by region/tier — these
are US on-demand list prices with no committed-use discounts and no taxes.
Where a page could not be verified live, `verified` is False and the note
says so; treat those numbers as approximate until reconfirmed on the source URL.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    label: str
    unit: str
    unit_price: float
    source_url: str
    last_verified: str
    verified: bool = True
    notes: str | None = None


# ---------------------------------------------------------------------------
# Regiões suportadas para precificação (mesmo conjunto usado por Storage e
# BigQuery, espelhando o seletor de região/local da calculadora oficial do
# Google Cloud). "us" é a multi-region dos EUA.
# ---------------------------------------------------------------------------
REGIONS: list[tuple[str, str]] = [
    ("us", "Estados Unidos (multi-region)"),
    ("us-central1", "us-central1 — Iowa, EUA"),
    ("southamerica-east1", "southamerica-east1 — São Paulo, Brasil"),
    ("europe-west1", "europe-west1 — Bélgica"),
    ("asia-southeast1", "asia-southeast1 — Singapura"),
]

# ---------------------------------------------------------------------------
# Cloud Storage — https://cloud.google.com/storage/pricing
# Confirmado via JSON de dados oficial da página, por região, 2026-09-02.
# ---------------------------------------------------------------------------
STORAGE_SOURCE = "https://cloud.google.com/storage/pricing"
_STORAGE_RATES_BY_REGION: dict[str, dict[str, float]] = {
    "us": {"standard": 0.026, "nearline": 0.015, "coldline": 0.007, "archive": 0.0024},
    "us-central1": {"standard": 0.020, "nearline": 0.010, "coldline": 0.004, "archive": 0.0012},
    "southamerica-east1": {"standard": 0.035, "nearline": 0.020, "coldline": 0.007, "archive": 0.003},
    "europe-west1": {"standard": 0.020, "nearline": 0.010, "coldline": 0.004, "archive": 0.0012},
    "asia-southeast1": {"standard": 0.020, "nearline": 0.010, "coldline": 0.005, "archive": 0.0015},
}
_STORAGE_CLASS_LABELS = {
    "standard": "Standard",
    "nearline": "Nearline",
    "coldline": "Coldline",
    "archive": "Archive",
}
STORAGE_PRICES: dict[str, dict[str, Price]] = {
    region: {
        storage_class: Price(
            f"Cloud Storage {label} ({dict(REGIONS)[region]})",
            "GB/mês",
            rate,
            STORAGE_SOURCE,
            "2026-09-02",
        )
        for storage_class, rate in rates.items()
        for label in [_STORAGE_CLASS_LABELS[storage_class]]
    }
    for region, rates in _STORAGE_RATES_BY_REGION.items()
}
# Operações variam por classe de armazenamento (por 1.000 operações); mesma
# taxa nas regiões pesquisadas.
STORAGE_CLASS_A_OPS = {
    "standard": Price("Operações Classe A — Standard", "1.000 ops", 0.01, STORAGE_SOURCE, "2026-09-02"),
    "nearline": Price("Operações Classe A — Nearline", "1.000 ops", 0.02, STORAGE_SOURCE, "2026-09-02"),
    "coldline": Price("Operações Classe A — Coldline", "1.000 ops", 0.04, STORAGE_SOURCE, "2026-09-02"),
    "archive": Price("Operações Classe A — Archive", "1.000 ops", 0.10, STORAGE_SOURCE, "2026-09-02"),
}
STORAGE_CLASS_B_OPS = {
    "standard": Price("Operações Classe B — Standard", "1.000 ops", 0.0004, STORAGE_SOURCE, "2026-09-02"),
    "nearline": Price("Operações Classe B — Nearline", "1.000 ops", 0.001, STORAGE_SOURCE, "2026-09-02"),
    "coldline": Price("Operações Classe B — Coldline", "1.000 ops", 0.01, STORAGE_SOURCE, "2026-09-02"),
    "archive": Price("Operações Classe B — Archive", "1.000 ops", 0.05, STORAGE_SOURCE, "2026-09-02"),
}
# Egress de rede: o Google cobra por CONTINENTE DE DESTINO (tier Premium, o
# padrão), não por um par livre origem+destino — por isso não existe um
# produto "Data Transfer" com origem/destino na calculadora oficial; o campo
# de egress vive dentro de cada produto (aqui, dentro do Cloud Storage).
STORAGE_EGRESS_BY_DESTINATION = {
    "worldwide": Price(
        "Egress — destino mundial (excl. Ásia/Austrália/China)",
        "GB",
        0.12,
        STORAGE_SOURCE,
        "2026-09-02",
        notes="Faixa 0–10TiB/mês; 10–150TiB = $0.11/GB; acima de 150TiB = $0.08/GB.",
    ),
    "asia": Price(
        "Egress — destino Ásia (excl. China)",
        "GB",
        0.12,
        STORAGE_SOURCE,
        "2026-09-02",
        notes="Faixa 0–10TiB/mês; 10–150TiB = $0.11/GB; acima de 150TiB = $0.08/GB.",
    ),
    "australia": Price(
        "Egress — destino Austrália",
        "GB",
        0.19,
        STORAGE_SOURCE,
        "2026-09-02",
        notes="Faixa 0–10TiB/mês; 10–150TiB = $0.18/GB; acima de 150TiB = $0.15/GB.",
    ),
    "china": Price(
        "Egress — destino China (excl. Hong Kong)",
        "GB",
        0.23,
        STORAGE_SOURCE,
        "2026-09-02",
        notes="Faixa 0–10TiB/mês; 10–150TiB = $0.22/GB; acima de 150TiB = $0.20/GB.",
    ),
}

# ---------------------------------------------------------------------------
# BigQuery — https://cloud.google.com/bigquery/pricing
# ---------------------------------------------------------------------------
BIGQUERY_SOURCE = "https://cloud.google.com/bigquery/pricing"
# Preço de consulta on-demand e de armazenamento variam por região/local
# (confirmado via JSON de dados oficial da página), 2026-09-02.
_BQ_RATES_BY_REGION: dict[str, dict[str, float]] = {
    "us": {"on_demand": 6.25, "active_storage": 0.02, "long_term_storage": 0.01},
    "us-central1": {"on_demand": 6.25, "active_storage": 0.023, "long_term_storage": 0.016},
    "southamerica-east1": {"on_demand": 11.25, "active_storage": 0.023, "long_term_storage": 0.016},
    "europe-west1": {"on_demand": 7.50, "active_storage": 0.02, "long_term_storage": 0.01},
    "asia-southeast1": {"on_demand": 8.4375, "active_storage": 0.02, "long_term_storage": 0.01},
}
BQ_ON_DEMAND_ANALYSIS_BY_REGION: dict[str, Price] = {
    region: Price(
        f"Consultas on-demand — {dict(REGIONS)[region]} (após 1 TiB grátis/mês)",
        "TiB processado",
        rates["on_demand"],
        BIGQUERY_SOURCE,
        "2026-09-02",
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_ACTIVE_STORAGE_BY_REGION: dict[str, Price] = {
    region: Price(
        f"Armazenamento ativo — {dict(REGIONS)[region]}",
        "GB/mês",
        rates["active_storage"],
        BIGQUERY_SOURCE,
        "2026-09-02",
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_LONG_TERM_STORAGE_BY_REGION: dict[str, Price] = {
    region: Price(
        f"Armazenamento de longo prazo — {dict(REGIONS)[region]} (sem alteração há 90 dias)",
        "GB/mês",
        rates["long_term_storage"],
        BIGQUERY_SOURCE,
        "2026-09-02",
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_STREAMING_INSERTS = Price(
    "Streaming inserts (Storage Write API)", "200 MiB", 0.01, BIGQUERY_SOURCE, "2026-09-02", verified=True,
    notes="Não reconfirmado na última pesquisa — confirme em cloud.google.com/bigquery/pricing.",
)
BQ_EDITIONS_STANDARD_SLOT = Price(
    "Editions — slot-hora Standard (pay-as-you-go)", "slot-hora", 0.04, BIGQUERY_SOURCE, "2026-09-02"
)
BQ_EDITIONS_ENTERPRISE_SLOT = Price(
    "Editions — slot-hora Enterprise (pay-as-you-go)", "slot-hora", 0.06, BIGQUERY_SOURCE, "2026-09-02"
)
BQ_EDITIONS_ENTERPRISE_PLUS_SLOT = Price(
    "Editions — slot-hora Enterprise Plus (pay-as-you-go)", "slot-hora", 0.10, BIGQUERY_SOURCE, "2026-09-02"
)

# ---------------------------------------------------------------------------
# Pub/Sub — https://cloud.google.com/pubsub/pricing (confirmado via JSON oficial)
# ---------------------------------------------------------------------------
PUBSUB_SOURCE = "https://cloud.google.com/pubsub/pricing"
PUBSUB_THROUGHPUT = Price(
    "Publicação e entrega — Message Delivery Basic (após 10 GiB grátis/mês)",
    "TiB",
    40.0,
    PUBSUB_SOURCE,
    "2026-09-02",
)
PUBSUB_BIGQUERY_SUBSCRIPTION = Price(
    "Entrega via assinatura BigQuery", "TiB", 50.0, PUBSUB_SOURCE, "2026-09-02"
)
PUBSUB_STORAGE_SUBSCRIPTION = Price(
    "Entrega via assinatura Cloud Storage", "TiB", 50.0, PUBSUB_SOURCE, "2026-09-02"
)

# ---------------------------------------------------------------------------
# Looker — https://cloud.google.com/looker/pricing (edições sob consulta comercial)
# ---------------------------------------------------------------------------
LOOKER_SOURCE = "https://cloud.google.com/looker/pricing"
LOOKER_CONVERSATIONAL_INPUT = Price(
    "Conversational Analytics — tokens de entrada excedentes",
    "1M tokens",
    3.0,
    LOOKER_SOURCE,
    "2026-09-02",
    notes="Vigente a partir de 01/10/2026. Franquia mensal gratuita varia por edição.",
)
LOOKER_CONVERSATIONAL_OUTPUT = Price(
    "Conversational Analytics — tokens de saída excedentes",
    "1M tokens",
    20.0,
    LOOKER_SOURCE,
    "2026-09-02",
)
LOOKER_LICENSE_NOTE = (
    "A licença da plataforma Looker (edições Standard/Enterprise/Embed + usuários) "
    "é vendida por contrato anual e não tem preço público — consulte o time de vendas do Google Cloud."
)

# ---------------------------------------------------------------------------
# Datastream — https://cloud.google.com/datastream/pricing
# ---------------------------------------------------------------------------
DATASTREAM_SOURCE = "https://cloud.google.com/datastream/pricing"
DATASTREAM_CDC_TIER1 = Price(
    "CDC — até 2.500 GiB/mês", "GiB", 2.00, DATASTREAM_SOURCE, "2026-09-02", verified=True,
    notes="Página oficial não pôde ser confirmada ao vivo; confirme antes de decisões de compra.",
)
DATASTREAM_CDC_TIER2 = Price(
    "CDC — acima de 2.500 GiB/mês", "GiB", 1.50, DATASTREAM_SOURCE, "2026-09-02", verified=True,
)
DATASTREAM_BACKFILL = Price(
    "Backfill (após 500 GiB grátis/mês)", "GiB", 0.40, DATASTREAM_SOURCE, "2026-09-02", verified=True,
)

# ---------------------------------------------------------------------------
# Storage Transfer Service / BigQuery Data Transfer Service
# "Data Transfer" NÃO é um produto próprio na calculadora oficial do Google —
# confirmado via pesquisa: o egress de rede é cobrado por continente de
# destino (ver STORAGE_EGRESS_BY_DESTINATION) e embutido no produto de
# origem/destino dos dados (ex.: dentro do Cloud Storage). O Storage Transfer
# Service abaixo é a única precificação própria e documentada para migração
# de dados de outra origem (on-premises/outra nuvem) para o GCP; por isso o
# único "seletor de origem" real e oficial aqui é a região do agente de
# transferência (América do Norte / Europa / Ásia-Pacífico).
# ---------------------------------------------------------------------------
STS_SOURCE = "https://cloud.google.com/storage-transfer/pricing"
STS_ONPREM_TO_CLOUD = Price(
    "On-premises → Cloud", "GiB", 0.0125, STS_SOURCE, "2026-09-02", verified=True,
    notes="Página oficial não pôde ser confirmada ao vivo; confirme antes de decisões de compra.",
)
STS_AGENT_NA = Price("Cloud-to-cloud via agente — América do Norte", "GiB", 0.03, STS_SOURCE, "2026-09-02", verified=True)
STS_AGENT_EU = Price("Cloud-to-cloud via agente — Europa", "GiB", 0.04, STS_SOURCE, "2026-09-02", verified=True)
STS_AGENT_APAC = Price("Cloud-to-cloud via agente — Ásia-Pacífico", "GiB", 0.08, STS_SOURCE, "2026-09-02", verified=True)

BQ_DTS_SOURCE = "https://docs.cloud.google.com/bigquery/docs/dts-introduction"
BQ_DTS_FREE = Price(
    "BigQuery Data Transfer Service (fontes Google/S3/Redshift/Teradata)",
    "serviço",
    0.0,
    BQ_DTS_SOURCE,
    "2026-09-02",
    notes="Ingestão gratuita para essas fontes; você paga apenas o armazenamento/consulta no BigQuery. "
    "Conectores de terceiros (SaaS) usam cobrança por slot-hora à parte.",
)

# ---------------------------------------------------------------------------
# Cloud Composer — https://cloud.google.com/composer/pricing
# ---------------------------------------------------------------------------
COMPOSER_SOURCE = "https://cloud.google.com/composer/pricing"
COMPOSER_VCPU = Price("Computação — vCPU", "vCPU-hora", 0.045, COMPOSER_SOURCE, "2026-09-02", verified=True)
COMPOSER_MEMORY = Price("Computação — memória", "GiB-hora", 0.005, COMPOSER_SOURCE, "2026-09-02", verified=True)
COMPOSER_STORAGE = Price("Computação — armazenamento", "GiB-hora", 0.0002, COMPOSER_SOURCE, "2026-09-02", verified=True)
COMPOSER_DB_STORAGE = Price("Armazenamento do banco de metadados", "GiB/mês", 0.17, COMPOSER_SOURCE, "2026-09-02", verified=True)

# ---------------------------------------------------------------------------
# Dataflow — https://cloud.google.com/dataflow/pricing
# ---------------------------------------------------------------------------
DATAFLOW_SOURCE = "https://cloud.google.com/dataflow/pricing"
DATAFLOW_VCPU = Price(
    "Worker — vCPU", "vCPU-hora", 0.056, DATAFLOW_SOURCE, "2026-09-02", verified=True,
    notes="Página oficial não pôde ser confirmada ao vivo nesta pesquisa; valor aproximado — confirme antes de usar.",
)
DATAFLOW_MEMORY = Price("Worker — memória", "GiB-hora", 0.003557, DATAFLOW_SOURCE, "2026-09-02", verified=False)
DATAFLOW_PD = Price("Persistent Disk (padrão)", "GiB-hora", 0.000054, DATAFLOW_SOURCE, "2026-09-02", verified=False)
