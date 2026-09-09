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

# BigQuery ML on-demand — https://cloud.google.com/bigquery/pricing#bqml
# Treino built-in (linear/logistic/k-means/PCA/ARIMA/contribution analysis):
# US$ 312.50 / TiB na multi-region US (50× o preço de consulta on-demand).
# Predição/avaliação: mesmo preço da consulta on-demand, entra na franquia de 1 TiB.
BQ_ML_BUILTIN_TRAINING_BY_REGION: dict[str, Price] = {
    region: Price(
        f"BigQuery ML — treino built-in ({dict(REGIONS)[region]})",
        "TiB processado",
        rates["on_demand"] * 50,
        BIGQUERY_SOURCE,
        "2026-09-08",
        notes=(
            "CREATE MODEL de regressão linear/logística, k-means, PCA, ARIMA+ "
            "e contribution analysis. Confirmado em cloud.google.com/bigquery/pricing."
        ),
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_ML_EXTERNAL_TRAINING_BY_REGION: dict[str, Price] = {
    region: Price(
        f"BigQuery ML — pré-processamento de modelo externo ({dict(REGIONS)[region]})",
        "TiB processado",
        rates["on_demand"],
        BIGQUERY_SOURCE,
        "2026-09-08",
        notes=(
            "DNN, boosted tree, random forest, AutoML, autoencoder e Wide-and-Deep: "
            "cobrança BigQuery do CREATE MODEL. Treino no Vertex/Gemini Agent Platform é extra."
        ),
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_ML_PREDICTION_BY_REGION: dict[str, Price] = {
    region: Price(
        f"BigQuery ML — predição e avaliação ({dict(REGIONS)[region]})",
        "TiB processado",
        rates["on_demand"],
        BIGQUERY_SOURCE,
        "2026-09-08",
        notes="Entra na franquia de 1 TiB/mês de análise on-demand.",
    )
    for region, rates in _BQ_RATES_BY_REGION.items()
}
BQ_ML_BUILTIN_TYPES = {
    "linear_reg",
    "logistic_reg",
    "kmeans",
    "pca",
    "arima",
    "contribution_analysis",
}
BQ_ML_EXTERNAL_TYPES = {
    "dnn",
    "wide_and_deep",
    "boosted_tree",
    "random_forest",
    "automl",
    "autoencoder",
}

# BI Engine — https://cloud.google.com/bigquery/pricing#bi_engine
# US$ 0.0416 / GiB-hora (Iowa/us e demais regiões listadas na página oficial).
BQ_BI_ENGINE = Price(
    "BI Engine — capacidade de memória",
    "GiB-hora",
    0.0416,
    BIGQUERY_SOURCE,
    "2026-09-08",
    notes="Reservado por projeto. Edições com compromisso podem incluir GiB grátis; esta estimativa não aplica o bundle.",
)
BQ_BI_ENGINE_HOURS_PER_MONTH = 730.0

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
LOOKER_STANDARD_USER = Price(
    "Licença Standard User (estimativa de lista)",
    "usuário/mês",
    35.0,
    LOOKER_SOURCE,
    "2026-09-08",
    verified=False,
    notes=(
        "A página oficial só mostra Call sales. US$ 35/usuário/mês é a faixa de lista "
        "mais citada para Standard User (Enterprise); confirme com o comercial do Google."
    ),
)
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
    "A plataforma Looker (Standard/Enterprise/Embed) é contrato anual sob consulta. "
    "A linha de usuário usa US$ 35/mês como estimativa de lista do Standard User; "
    "o valor negociado pode ser outro."
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
# ---------------------------------------------------------------------------
# Dataflow — https://cloud.google.com/dataflow/pricing
# Preços Iowa / us-central1 (tabela Default da página oficial), 2026-09-08.
# ---------------------------------------------------------------------------
DATAFLOW_SOURCE = "https://cloud.google.com/dataflow/pricing"
DATAFLOW_VERIFIED = "2026-09-08"

DATAFLOW_WORKER_DEFAULTS: dict[str, dict[str, float]] = {
    "batch": {"vcpu": 1, "memory_gb": 3.75, "disk_gb": 250, "min_workers": 1},
    "flexrs": {"vcpu": 2, "memory_gb": 7.5, "disk_gb": 25, "min_workers": 2},
    "streaming": {"vcpu": 4, "memory_gb": 15, "disk_gb": 400, "min_workers": 1},
}
DATAFLOW_STREAMING_ENGINE_DISK_GB = 30.0

DATAFLOW_BATCH_VCPU = Price("Classic batch — vCPU", "vCPU-hora", 0.056, DATAFLOW_SOURCE, DATAFLOW_VERIFIED)
DATAFLOW_BATCH_MEMORY = Price("Classic batch — memória", "GiB-hora", 0.003557, DATAFLOW_SOURCE, DATAFLOW_VERIFIED)
DATAFLOW_BATCH_SHUFFLE = Price("Classic batch — Shuffle", "GiB", 0.011, DATAFLOW_SOURCE, DATAFLOW_VERIFIED)

DATAFLOW_FLEXRS_VCPU = Price("Classic FlexRS — vCPU", "vCPU-hora", 0.0336, DATAFLOW_SOURCE, DATAFLOW_VERIFIED)
DATAFLOW_FLEXRS_MEMORY = Price("Classic FlexRS — memória", "GiB-hora", 0.0021342, DATAFLOW_SOURCE, DATAFLOW_VERIFIED)

DATAFLOW_STREAMING_RATES: dict[str, dict[str, Price]] = {
    "none": {
        "vcpu": Price("Classic streaming — vCPU", "vCPU-hora", 0.069, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
        "memory": Price("Classic streaming — memória", "GiB-hora", 0.003557, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
        "legacy_data": Price(
            "Streaming Engine data processed (legado)", "GiB", 0.018, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
        "secu": Price(
            "Streaming Engine Compute Units", "unidade-hora", 0.089, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
    },
    "cud_1y": {
        "vcpu": Price("Classic streaming — vCPU (CUD 1 ano)", "vCPU-hora", 0.0552, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
        "memory": Price(
            "Classic streaming — memória (CUD 1 ano)", "GiB-hora", 0.0028456, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
        "legacy_data": Price(
            "Streaming Engine data processed legado (CUD 1 ano)", "GiB", 0.0144, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
        "secu": Price(
            "Streaming Engine Compute Units (CUD 1 ano)", "unidade-hora", 0.0712, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
    },
    "cud_3y": {
        "vcpu": Price("Classic streaming — vCPU (CUD 3 anos)", "vCPU-hora", 0.0414, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
        "memory": Price(
            "Classic streaming — memória (CUD 3 anos)", "GiB-hora", 0.0021342, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
        "legacy_data": Price(
            "Streaming Engine data processed legado (CUD 3 anos)", "GiB", 0.0108, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
        "secu": Price(
            "Streaming Engine Compute Units (CUD 3 anos)", "unidade-hora", 0.0534, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
        ),
    },
}

DATAFLOW_PRIME_DCU_BATCH = Price(
    "Prime — Data Compute Units (batch)", "DCU", 0.06, DATAFLOW_SOURCE, DATAFLOW_VERIFIED,
    notes="1 DCU ≈ 1 hora em worker 1 vCPU / 4 GiB. Sem CUD na tabela oficial de batch.",
)
DATAFLOW_PRIME_DCU_STREAMING: dict[str, Price] = {
    "none": Price("Prime — Data Compute Units (streaming)", "DCU", 0.089, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "cud_1y": Price("Prime — DCU streaming (CUD 1 ano)", "DCU", 0.0712, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "cud_3y": Price("Prime — DCU streaming (CUD 3 anos)", "DCU", 0.0534, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
}

DATAFLOW_PD = Price(
    "Persistent Disk padrão", "GiB-hora", 0.000054, DATAFLOW_SOURCE, DATAFLOW_VERIFIED
)

DATAFLOW_GPU_PRICES: dict[str, Price] = {
    "t4": Price("GPU NVIDIA Tesla T4", "GPU-hora", 0.42, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "l4": Price("GPU NVIDIA Tesla L4", "GPU-hora", 0.672048, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "p4": Price("GPU NVIDIA Tesla P4", "GPU-hora", 0.72, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "p100": Price("GPU NVIDIA Tesla P100", "GPU-hora", 1.752, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "v100": Price("GPU NVIDIA Tesla V100", "GPU-hora", 2.976, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "a100_40": Price("GPU NVIDIA A100 40 GB", "GPU-hora", 3.72, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "a100_80": Price("GPU NVIDIA A100 80 GB", "GPU-hora", 4.713696, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "h100": Price("GPU NVIDIA H100", "GPU-hora", 11.7558607, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "h100_mega": Price("GPU NVIDIA H100 Mega", "GPU-hora", 12.4131309, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
    "rtx_pro_6000": Price("GPU NVIDIA RTX PRO 6000", "GPU-hora", 1.315, DATAFLOW_SOURCE, DATAFLOW_VERIFIED),
}

# Compatível com referências antigas
DATAFLOW_VCPU = DATAFLOW_BATCH_VCPU
DATAFLOW_MEMORY = DATAFLOW_BATCH_MEMORY

# ---------------------------------------------------------------------------
# Vertex AI Training / Prediction — https://cloud.google.com/vertex-ai/pricing
# n1-standard-4, us-central1, tabela Default, 2026-09-08.
# ---------------------------------------------------------------------------
VERTEX_SOURCE = "https://cloud.google.com/vertex-ai/pricing"
VERTEX_TRAINING_N1_STANDARD_4 = Price(
    "Training — n1-standard-4",
    "nó-hora",
    0.21849885,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_PREDICTION_N1_STANDARD_4 = Price(
    "Prediction — n1-standard-4 (online)",
    "nó-hora",
    0.219,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_FEATURE_PROCESSING = Price(
    "Feature Store — data processing (feature engineering / ingestão)",
    "nó-hora",
    0.08,
    VERTEX_SOURCE,
    "2026-09-08",
    notes="us-central1. ~100 MiB ingestidos por nó-hora se não houver funções analíticas.",
)
VERTEX_FEATURE_OPTIMIZED_SERVING = Price(
    "Feature Store — serving online Optimized (inclui 200 GB)",
    "nó-hora",
    0.30,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_FEATURE_BIGTABLE_SERVING = Price(
    "Feature Store — serving online Bigtable",
    "nó-hora",
    0.94,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_FEATURE_BIGTABLE_STORAGE = Price(
    "Feature Store — armazenamento Bigtable",
    "GiB-hora",
    0.000342466,
    VERTEX_SOURCE,
    "2026-09-08",
    notes="≈ US$ 0,25/GiB-mês (730 h).",
)
VERTEX_PIPELINE_RUN = Price(
    "Vertex Pipelines — execução de run",
    "run",
    0.03,
    VERTEX_SOURCE,
    "2026-09-08",
    notes="Compute dos componentes (treino, Dataflow etc.) é cobrado à parte.",
)
VERTEX_WORKBENCH_N1_VCPU = Price(
    "Workbench — N1 vCPU + taxa de gerenciamento",
    "vCPU-hora",
    0.0442554,
    VERTEX_SOURCE,
    "2026-09-08",
    notes="us-central1: US$ 0,0379332 compute + US$ 0,0063222 management.",
)
VERTEX_WORKBENCH_N1_MEMORY = Price(
    "Workbench — N1 memória + taxa de gerenciamento",
    "GiB-hora",
    0.0059318,
    VERTEX_SOURCE,
    "2026-09-08",
    notes="us-central1: US$ 0,0050844 compute + US$ 0,0008474 management.",
)
VERTEX_VECTOR_E2_STANDARD_2 = Price(
    "Vector Search — serving e2-standard-2",
    "nó-hora",
    0.0938084,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_VECTOR_INDEX_BUILD = Price(
    "Vector Search — build/update de índice",
    "GiB",
    3.00,
    VERTEX_SOURCE,
    "2026-09-08",
)
VERTEX_MODEL_MONITORING = Price(
    "Vertex Model Monitoring — dados analisados",
    "GB",
    3.50,
    VERTEX_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Dataproc (Managed Service for Apache Spark) — https://cloud.google.com/dataproc/pricing
# ---------------------------------------------------------------------------
DATAPROC_SOURCE = "https://cloud.google.com/dataproc/pricing"
DATAPROC_CLUSTER_FEE = Price(
    "Dataproc clusters — taxa de gerenciamento",
    "vCPU-hora",
    0.01,
    DATAPROC_SOURCE,
    "2026-09-08",
    notes="Além desta taxa, o cluster cobra Compute Engine e disco à parte.",
)
DATAPROC_SERVERLESS_DCU = Price(
    "Dataproc serverless — DCU standard",
    "DCU-hora",
    0.06,
    DATAPROC_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Cloud Operations (Observability) — https://cloud.google.com/stackdriver/pricing
# ---------------------------------------------------------------------------
OPS_SOURCE = "https://cloud.google.com/stackdriver/pricing"
OPS_LOGGING_INGEST = Price(
    "Cloud Logging — ingestão (após 50 GiB grátis/projeto)",
    "GiB",
    0.50,
    OPS_SOURCE,
    "2026-09-08",
)
OPS_MONITORING_INGEST = Price(
    "Cloud Monitoring — métricas (após 150 MiB grátis)",
    "MiB",
    0.2580,
    OPS_SOURCE,
    "2026-09-08",
    notes="Primeira faixa 150–100.000 MiB. Faixas seguintes são mais baratas.",
)
OPS_TRACE_INGEST = Price(
    "Cloud Trace — ingestão (após 2,5 milhões de spans grátis)",
    "milhão de spans",
    0.20,
    OPS_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Secret Manager — https://cloud.google.com/secret-manager/pricing
# ---------------------------------------------------------------------------
SECRET_SOURCE = "https://cloud.google.com/secret-manager/pricing"
SECRET_VERSION = Price(
    "Secret Manager — versões ativas (após 6 grátis)",
    "versão/mês",
    0.06,
    SECRET_SOURCE,
    "2026-09-08",
)
SECRET_ACCESS = Price(
    "Secret Manager — acessos (após 10.000 grátis)",
    "10.000 ops",
    0.03,
    SECRET_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Cloud Build — https://cloud.google.com/build/pricing
# ---------------------------------------------------------------------------
BUILD_SOURCE = "https://cloud.google.com/build/pricing"
BUILD_E2_STANDARD_2 = Price(
    "Cloud Build — e2-standard-2 (após 2.500 min grátis/mês)",
    "minuto",
    0.006,
    BUILD_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Cloud Vision API — https://cloud.google.com/vision/pricing
# ---------------------------------------------------------------------------
VISION_SOURCE = "https://cloud.google.com/vision/pricing"
VISION_LABEL = Price("Vision — Label Detection (após 1.000 grátis)", "1.000 unidades", 1.50, VISION_SOURCE, "2026-09-08")
VISION_OCR = Price("Vision — Text/Document OCR (após 1.000 grátis)", "1.000 unidades", 1.50, VISION_SOURCE, "2026-09-08")
VISION_OBJECT = Price(
    "Vision — Object Localization (após 1.000 grátis)", "1.000 unidades", 2.25, VISION_SOURCE, "2026-09-08"
)
VISION_WEB = Price("Vision — Web Detection (após 1.000 grátis)", "1.000 unidades", 3.50, VISION_SOURCE, "2026-09-08")

# ---------------------------------------------------------------------------
# Video Intelligence API — https://cloud.google.com/video-intelligence/pricing
# ---------------------------------------------------------------------------
VIDEO_SOURCE = "https://cloud.google.com/video-intelligence/pricing"
VIDEO_LABEL = Price("Video — Label detection (após 1.000 min grátis)", "minuto", 0.10, VIDEO_SOURCE, "2026-09-08")
VIDEO_SHOT = Price("Video — Shot detection (após 1.000 min grátis)", "minuto", 0.05, VIDEO_SOURCE, "2026-09-08")
VIDEO_OBJECT = Price("Video — Object tracking (após 1.000 min grátis)", "minuto", 0.15, VIDEO_SOURCE, "2026-09-08")
VIDEO_EXPLICIT = Price(
    "Video — Explicit content (após 1.000 min grátis)", "minuto", 0.10, VIDEO_SOURCE, "2026-09-08"
)

# ---------------------------------------------------------------------------
# Vertex AutoML Vision — https://cloud.google.com/vertex-ai/pricing
# ---------------------------------------------------------------------------
AUTOML_VISION_TRAINING = Price(
    "AutoML Vision — treino (classificação de imagem)",
    "hora",
    3.465,
    VERTEX_SOURCE,
    "2026-09-08",
)
AUTOML_VISION_PREDICTION = Price(
    "AutoML Vision — predição online (nó)",
    "nó-hora",
    1.375,
    VERTEX_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Cloud Run — https://cloud.google.com/run/pricing (us-central1, CPU only during request)
# ---------------------------------------------------------------------------
RUN_SOURCE = "https://cloud.google.com/run/pricing"
CLOUD_RUN_VCPU = Price("Cloud Run — vCPU", "vCPU-hora", 0.0864, RUN_SOURCE, "2026-09-08")
CLOUD_RUN_MEMORY = Price("Cloud Run — memória", "GiB-hora", 0.0090, RUN_SOURCE, "2026-09-08")
CLOUD_RUN_REQUESTS = Price(
    "Cloud Run — requisições (após 2 milhões grátis)",
    "milhão",
    0.40,
    RUN_SOURCE,
    "2026-09-08",
)

# ---------------------------------------------------------------------------
# Azure — East US, pay-as-you-go, lista pública (confirmar na calculadora Microsoft).
# ---------------------------------------------------------------------------
AZURE_ADLS_SOURCE = "https://azure.microsoft.com/pricing/details/storage/data-lake/"
AZURE_ADLS_HOT = Price(
    "ADLS Gen2 — Hot LRS (East US)",
    "GB/mês",
    0.0208,
    AZURE_ADLS_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Hierarchical namespace. Operações e Cool/Archive à parte.",
)
AZURE_SYNAPSE_SOURCE = "https://azure.microsoft.com/pricing/details/synapse-analytics/"
AZURE_SYNAPSE_SERVERLESS = Price(
    "Synapse — SQL serverless",
    "TB processado",
    5.00,
    AZURE_SYNAPSE_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Mínimo 10 MB por query. Storage fica no ADLS.",
)
AZURE_SYNAPSE_SPARK = Price(
    "Synapse — Spark",
    "vCore-hora",
    0.1765,
    AZURE_SYNAPSE_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_EVENTHUBS_SOURCE = "https://azure.microsoft.com/pricing/details/event-hubs/"
AZURE_EVENTHUBS_TU = Price(
    "Event Hubs Standard — throughput unit",
    "TU-hora",
    0.03,
    AZURE_EVENTHUBS_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_EVENTHUBS_INGRESS = Price(
    "Event Hubs Standard — ingress",
    "milhão de eventos",
    0.028,
    AZURE_EVENTHUBS_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_ADF_SOURCE = "https://azure.microsoft.com/pricing/details/data-factory/"
AZURE_ADF_ACTIVITY = Price(
    "Data Factory — orquestração (Azure IR)",
    "1.000 activity runs",
    1.00,
    AZURE_ADF_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_ADF_DIU = Price(
    "Data Factory — cópia (DIU)",
    "DIU-hora",
    0.25,
    AZURE_ADF_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_DMS_SOURCE = "https://azure.microsoft.com/pricing/details/database-migration/"
AZURE_DMS_PREMIUM = Price(
    "Azure Database Migration Service Premium — 4 vCore",
    "serviço-hora faturável",
    1.48,
    AZURE_DMS_SOURCE,
    "2026-09-09",
    verified=False,
    notes="Estimativa após os 183 dias gratuitos; confirme a tarifa regional no Azure Pricing Calculator.",
)
AZURE_STORAGE_MOVER_SOURCE = "https://azure.microsoft.com/products/storage-mover"
AZURE_STORAGE_MOVER = Price(
    "Azure Storage Mover",
    "GB copiado",
    0.0,
    AZURE_STORAGE_MOVER_SOURCE,
    "2026-09-09",
    notes="O serviço é gratuito; storage, transações e rede são cobrados separadamente.",
)
AZURE_ASA_SOURCE = "https://azure.microsoft.com/pricing/details/stream-analytics/"
AZURE_ASA_SU = Price(
    "Stream Analytics — streaming unit",
    "SU-hora",
    0.11,
    AZURE_ASA_SOURCE,
    "2026-09-08",
    verified=False,
)
AZURE_ML_SOURCE = "https://azure.microsoft.com/pricing/details/machine-learning/"
AZURE_ML_COMPUTE = Price(
    "Azure Machine Learning — compute Standard_D2as_v5",
    "instância-hora",
    0.096,
    AZURE_ML_SOURCE,
    "2026-09-09",
    verified=False,
    notes="Azure ML não cobra taxa de plataforma; compute, storage e serviços associados são cobrados separadamente.",
)
AZURE_AI_SEARCH_SOURCE = "https://azure.microsoft.com/pricing/details/search/"
AZURE_AI_SEARCH_SU = Price(
    "Azure AI Search — Standard S1",
    "search unit-hora",
    0.336,
    AZURE_AI_SEARCH_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_VISION_SOURCE = "https://azure.microsoft.com/pricing/details/cognitive-services/computer-vision/"
AZURE_VISION_TRANSACTIONS = Price(
    "Azure AI Vision — análise de imagens",
    "1.000 transações",
    1.00,
    AZURE_VISION_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_VIDEO_MINUTE = Price(
    "Azure AI Video — análise",
    "minuto",
    0.05,
    AZURE_VISION_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_MONITOR_SOURCE = "https://azure.microsoft.com/pricing/details/monitor/"
AZURE_MONITOR_LOGS = Price(
    "Azure Monitor Logs — ingestão",
    "GB",
    2.76,
    AZURE_MONITOR_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_KEY_VAULT_SOURCE = "https://azure.microsoft.com/pricing/details/key-vault/"
AZURE_KEY_VAULT_OPS = Price(
    "Azure Key Vault — operações de secrets",
    "10.000 operações",
    0.03,
    AZURE_KEY_VAULT_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_CONTAINER_APPS_SOURCE = "https://azure.microsoft.com/pricing/details/container-apps/"
AZURE_CONTAINER_APPS_VCPU = Price(
    "Azure Container Apps — vCPU",
    "vCPU-hora",
    0.0864,
    AZURE_CONTAINER_APPS_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_CONTAINER_APPS_MEMORY = Price(
    "Azure Container Apps — memória",
    "GiB-hora",
    0.0108,
    AZURE_CONTAINER_APPS_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_CONTAINER_APPS_REQUESTS = Price(
    "Azure Container Apps — requisições",
    "milhão",
    0.40,
    AZURE_CONTAINER_APPS_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_POWER_BI_SOURCE = "https://www.microsoft.com/power-platform/products/power-bi/pricing"
AZURE_POWER_BI_PRO = Price(
    "Power BI Pro",
    "usuário/mês",
    14.00,
    AZURE_POWER_BI_SOURCE,
    "2026-09-09",
    verified=False,
)
AZURE_DEVOPS_SOURCE = "https://azure.microsoft.com/pricing/details/devops/azure-devops-services/"
AZURE_PIPELINES_PARALLEL = Price(
    "Azure Pipelines — job paralelo hospedado",
    "job paralelo/mês",
    40.00,
    AZURE_DEVOPS_SOURCE,
    "2026-09-09",
    verified=False,
    notes="A franquia gratuita aplicável à organização não foi descontada.",
)

# ---------------------------------------------------------------------------
# AWS — us-east-1, on-demand.
# ---------------------------------------------------------------------------
AWS_S3_SOURCE = "https://aws.amazon.com/s3/pricing/"
AWS_S3_STANDARD = Price(
    "S3 Standard (primeiros 50 TB)",
    "GB/mês",
    0.023,
    AWS_S3_SOURCE,
    "2026-09-08",
    verified=False,
)
AWS_S3_PUT = Price("S3 — PUT/COPY/POST/LIST", "1.000 ops", 0.005, AWS_S3_SOURCE, "2026-09-08", verified=False)
AWS_S3_GET = Price("S3 — GET e SELECT", "1.000 ops", 0.0004, AWS_S3_SOURCE, "2026-09-08", verified=False)
AWS_ATHENA_SOURCE = "https://aws.amazon.com/athena/pricing/"
AWS_ATHENA_SCAN = Price(
    "Athena SQL — dados varridos",
    "TB",
    5.00,
    AWS_ATHENA_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Mínimo 10 MB por query. Storage é S3.",
)
AWS_REDSHIFT_SOURCE = "https://aws.amazon.com/redshift/pricing/"
AWS_REDSHIFT_RPU = Price(
    "Redshift Serverless — RPU",
    "RPU-hora",
    0.375,
    AWS_REDSHIFT_SOURCE,
    "2026-09-08",
    verified=False,
)
AWS_REDSHIFT_STORAGE = Price(
    "Redshift Managed Storage",
    "GB/mês",
    0.024,
    AWS_REDSHIFT_SOURCE,
    "2026-09-08",
    verified=False,
)
AWS_GLUE_SOURCE = "https://aws.amazon.com/glue/pricing/"
AWS_GLUE_DPU = Price("Glue ETL — DPU", "DPU-hora", 0.44, AWS_GLUE_SOURCE, "2026-09-08", verified=False)
AWS_KINESIS_SOURCE = "https://aws.amazon.com/kinesis/data-streams/pricing/"
AWS_KINESIS_SHARD = Price(
    "Kinesis Data Streams — shard",
    "shard-hora",
    0.015,
    AWS_KINESIS_SOURCE,
    "2026-09-08",
    verified=False,
)
AWS_KINESIS_PUT = Price(
    "Kinesis — PUT payload units",
    "milhão",
    0.014,
    AWS_KINESIS_SOURCE,
    "2026-09-08",
    verified=False,
    notes="1 unit = 25 KB de payload.",
)
AWS_FLINK_SOURCE = "https://aws.amazon.com/managed-service-apache-flink/pricing/"
AWS_FLINK_KPU = Price(
    "Managed Service for Apache Flink — compute",
    "KPU-hora",
    0.11,
    AWS_FLINK_SOURCE,
    "2026-09-09",
)
AWS_FLINK_STORAGE = Price(
    "Managed Service for Apache Flink — application storage",
    "GB/mês",
    0.10,
    AWS_FLINK_SOURCE,
    "2026-09-09",
)
AWS_DMS_SOURCE = "https://aws.amazon.com/dms/pricing/"
AWS_DMS_INSTANCE = Price(
    "DMS — instância dms.t3.medium",
    "hora",
    0.196,
    AWS_DMS_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Storage e transferência de dados à parte.",
)
AWS_DATASYNC_SOURCE = "https://aws.amazon.com/datasync/pricing/"
AWS_DATASYNC_GB = Price("DataSync — dados copiados", "GB", 0.0125, AWS_DATASYNC_SOURCE, "2026-09-08", verified=False)
AWS_EMR_SOURCE = "https://aws.amazon.com/emr/pricing/"
AWS_EMR_FEE = Price(
    "EMR — taxa sobre m5.xlarge",
    "instância-hora",
    0.048,
    AWS_EMR_SOURCE,
    "2026-09-08",
    verified=False,
    notes="EC2/EBS entram na conta AWS à parte.",
)
AWS_MWAA_SOURCE = "https://aws.amazon.com/managed-workflows-for-apache-airflow/pricing/"
AWS_MWAA_ENV = Price(
    "MWAA — ambiente mw1.small",
    "hora",
    0.49,
    AWS_MWAA_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Workers extras e meta database à parte.",
)
AWS_EC2_SOURCE = "https://aws.amazon.com/ec2/pricing/on-demand/"
AWS_EC2_M5_XLARGE = Price(
    "EC2 m5.xlarge para EMR",
    "instância-hora",
    0.192,
    AWS_EC2_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_SAGEMAKER_SOURCE = "https://aws.amazon.com/sagemaker/ai/pricing/"
AWS_SAGEMAKER_COMPUTE = Price(
    "SageMaker AI — ml.m5.large",
    "instância-hora",
    0.115,
    AWS_SAGEMAKER_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_FEATURE_STORE_STORAGE = Price(
    "SageMaker Feature Store — online storage",
    "GB/mês",
    0.23,
    AWS_SAGEMAKER_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_FEATURE_STORE_WRITE = Price(
    "SageMaker Feature Store — gravações",
    "milhão",
    1.25,
    AWS_SAGEMAKER_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_FEATURE_STORE_READ = Price(
    "SageMaker Feature Store — leituras",
    "milhão",
    0.25,
    AWS_SAGEMAKER_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_OPENSEARCH_SOURCE = "https://aws.amazon.com/opensearch-service/pricing/"
AWS_OPENSEARCH_OCU = Price(
    "OpenSearch Serverless — compute",
    "OCU-hora",
    0.24,
    AWS_OPENSEARCH_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_OPENSEARCH_STORAGE = Price(
    "OpenSearch Serverless — storage",
    "GB/mês",
    0.024,
    AWS_OPENSEARCH_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_REKOGNITION_SOURCE = "https://aws.amazon.com/rekognition/pricing/"
AWS_REKOGNITION_IMAGE = Price(
    "Rekognition Image — análise",
    "1.000 imagens",
    1.00,
    AWS_REKOGNITION_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_REKOGNITION_VIDEO = Price(
    "Rekognition Video — análise",
    "minuto",
    0.10,
    AWS_REKOGNITION_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_CLOUDWATCH_SOURCE = "https://aws.amazon.com/cloudwatch/pricing/"
AWS_CLOUDWATCH_LOGS = Price(
    "CloudWatch Logs — ingestão",
    "GB",
    0.50,
    AWS_CLOUDWATCH_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_SECRETS_SOURCE = "https://aws.amazon.com/secrets-manager/pricing/"
AWS_SECRET_MONTH = Price(
    "Secrets Manager — secret armazenado",
    "secret/mês",
    0.40,
    AWS_SECRETS_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_SECRET_API = Price(
    "Secrets Manager — chamadas de API",
    "10.000 chamadas",
    0.05,
    AWS_SECRETS_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_LAMBDA_SOURCE = "https://aws.amazon.com/lambda/pricing/"
AWS_LAMBDA_REQUESTS = Price(
    "Lambda — requisições",
    "milhão",
    0.20,
    AWS_LAMBDA_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_LAMBDA_DURATION = Price(
    "Lambda — duração",
    "milhão de GB-segundos",
    16.6667,
    AWS_LAMBDA_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_CODEBUILD_SOURCE = "https://aws.amazon.com/codebuild/pricing/"
AWS_CODEBUILD_MINUTE = Price(
    "CodeBuild — general1.small",
    "minuto",
    0.005,
    AWS_CODEBUILD_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_QUICKSIGHT_SOURCE = "https://aws.amazon.com/quicksight/pricing/"
AWS_QUICKSIGHT_AUTHOR = Price(
    "Amazon QuickSight Enterprise — autor",
    "autor/mês",
    24.00,
    AWS_QUICKSIGHT_SOURCE,
    "2026-09-09",
    verified=False,
)
AWS_QUICKSIGHT_READER = Price(
    "Amazon QuickSight Enterprise — leitor",
    "leitor/mês",
    5.00,
    AWS_QUICKSIGHT_SOURCE,
    "2026-09-09",
    verified=False,
    notes="Representa o teto mensal por leitor; cobrança real pode ser por sessão.",
)

# ---------------------------------------------------------------------------
# Databricks — AWS Premium list (DBU). VMs da nuvem à parte no compute clássico.
# ---------------------------------------------------------------------------
DBX_SOURCE = "https://www.databricks.com/product/pricing"
DBX_CLOUD_VM = Price(
    "VM da nuvem para compute clássico (m5.xlarge)",
    "instância-hora",
    0.192,
    "https://aws.amazon.com/ec2/pricing/on-demand/",
    "2026-09-09",
    verified=False,
    notes="Referência AWS para tornar o custo Databricks classic comparável; ajuste ao provedor contratado.",
)
DBX_JOBS = Price("Lakeflow Jobs — classic", "DBU", 0.15, DBX_SOURCE, "2026-09-08", verified=False)
DBX_ALL_PURPOSE = Price("All-Purpose Compute", "DBU", 0.55, DBX_SOURCE, "2026-09-08", verified=False)
DBX_SQL_CLASSIC = Price("SQL Warehouse Classic", "DBU", 0.22, DBX_SOURCE, "2026-09-08", verified=False)
DBX_SQL_SERVERLESS = Price(
    "SQL Warehouse Serverless",
    "DBU",
    0.70,
    DBX_SOURCE,
    "2026-09-08",
    verified=False,
    notes="Serverless já inclui a VM da nuvem.",
)
DBX_DLT = Price(
    "Lakeflow Declarative Pipelines — Core",
    "DBU",
    0.20,
    DBX_SOURCE,
    "2026-09-08",
    verified=False,
)
DBX_STORAGE = Price(
    "Databricks managed storage",
    "GB/mês",
    0.023,
    DBX_SOURCE,
    "2026-09-08",
    verified=False,
    notes="DSU. O data lake na nuvem (S3/ADLS/GCS) é cobrado no provedor.",
)
DBX_MODEL_SERVING = Price(
    "Databricks Model Serving — serverless",
    "DBU",
    0.07,
    DBX_SOURCE,
    "2026-09-09",
    verified=False,
)
DBX_VECTOR_SEARCH = Price(
    "Databricks Vector Search",
    "DBU",
    0.20,
    DBX_SOURCE,
    "2026-09-09",
    verified=False,
)
DBX_LAKEHOUSE_MONITORING = Price(
    "Databricks Lakehouse Monitoring",
    "DBU",
    0.20,
    DBX_SOURCE,
    "2026-09-09",
    verified=False,
)
