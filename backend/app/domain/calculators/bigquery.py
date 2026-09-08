from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition

_REGION_OPTIONS = [FieldOption(value=region_id, label=label) for region_id, label in p.REGIONS]


class BigQueryCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="bigquery",
        name="BigQuery",
        category="Processamento e Analytics",
        description="Data warehouse serverless: armazenamento e consultas on-demand.",
        fields=[
            FieldSchema(
                id="region",
                label="Região / local do dataset",
                type="select",
                default="us",
                options=_REGION_OPTIONS,
            ),
            FieldSchema(
                id="pricing_model",
                label="Modelo de cobrança de consultas",
                type="select",
                default="on_demand",
                options=[
                    FieldOption(value="on_demand", label="Sob demanda (por TiB processado)"),
                    FieldOption(value="enterprise", label="BigQuery Enterprise (Editions, por slot-hora)"),
                    FieldOption(value="bqml", label="BigQuery ML (treino e predição por TiB)"),
                    FieldOption(value="bi_engine", label="BI Engine (capacidade de memória)"),
                ],
                help="Sob demanda e Enterprise cobram consultas SQL. BigQuery ML e BI Engine têm campos próprios abaixo; no Enterprise o treino ML já entra nos slots.",
            ),
            FieldSchema(
                id="query_tib_per_month",
                label="Dados processados em consultas",
                type="number",
                unit="TiB/mês",
                default=5,
                min=0,
                help="Usado no modelo sob demanda. Primeiro 1 TiB/mês é gratuito.",
            ),
            FieldSchema(
                id="enterprise_slot_hours",
                label="Capacidade Enterprise utilizada",
                type="number",
                unit="slot-hora/mês",
                default=0,
                min=0,
                help="Usado no modelo BigQuery Enterprise. Inclui consultas e BigQuery ML.",
            ),
            FieldSchema(
                id="bqml_model_type",
                label="BigQuery ML — tipo de modelo",
                type="select",
                default="linear_reg",
                options=[
                    FieldOption(value="linear_reg", label="Regressão linear (built-in)"),
                    FieldOption(value="logistic_reg", label="Regressão logística (built-in)"),
                    FieldOption(value="kmeans", label="K-means (built-in)"),
                    FieldOption(value="pca", label="PCA (built-in)"),
                    FieldOption(value="arima", label="Séries temporais ARIMA+ (built-in)"),
                    FieldOption(value="contribution_analysis", label="Contribution analysis (built-in)"),
                    FieldOption(value="dnn", label="DNN (externo / Vertex)"),
                    FieldOption(value="wide_and_deep", label="Wide-and-Deep (externo / Vertex)"),
                    FieldOption(value="boosted_tree", label="Boosted tree (externo / Vertex)"),
                    FieldOption(value="random_forest", label="Random forest (externo / Vertex)"),
                    FieldOption(value="automl", label="AutoML Tables (externo / Vertex)"),
                    FieldOption(value="autoencoder", label="Autoencoder (externo / Vertex)"),
                ],
                help="Built-in: treino a 50× o preço de consulta. Externo: pré-processamento no BigQuery + treino no Vertex (não incluso).",
            ),
            FieldSchema(
                id="bqml_processed_tib",
                label="BigQuery ML — volume processado no treino",
                type="number",
                unit="TiB/mês",
                default=0,
                min=0,
                help="Bytes processados pelo CREATE MODEL. Deixe 0 se não for usar ML.",
            ),
            FieldSchema(
                id="bqml_prediction_tib",
                label="BigQuery ML — predição",
                type="number",
                unit="TiB/mês",
                default=0,
                min=0,
                help="ML.PREDICT / avaliação / inspeção. Preço igual ao de consulta on-demand.",
            ),
            FieldSchema(
                id="bi_engine_memory_gib",
                label="BI Engine — capacidade de memória",
                type="number",
                unit="GiB",
                default=0,
                min=0,
                help="Reserva em GiB. Cobra US$ 0,0416 por GiB-hora (~730 h/mês). Deixe 0 se não usar.",
            ),
            FieldSchema(
                id="active_storage_gb",
                label="Armazenamento ativo",
                type="number",
                unit="GB",
                default=500,
                min=0,
            ),
            FieldSchema(
                id="long_term_storage_gb",
                label="Armazenamento de longo prazo",
                type="number",
                unit="GB",
                default=0,
                min=0,
                help="Tabelas/partições sem alteração há 90+ dias.",
            ),
            FieldSchema(
                id="streaming_inserts_gb",
                label="Streaming inserts",
                type="number",
                unit="GB/mês",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [
                *p.BQ_ON_DEMAND_ANALYSIS_BY_REGION.values(),
                *p.BQ_ACTIVE_STORAGE_BY_REGION.values(),
                *p.BQ_LONG_TERM_STORAGE_BY_REGION.values(),
                p.BQ_STREAMING_INSERTS,
                p.BQ_EDITIONS_STANDARD_SLOT,
                p.BQ_EDITIONS_ENTERPRISE_SLOT,
                p.BQ_EDITIONS_ENTERPRISE_PLUS_SLOT,
                *p.BQ_ML_BUILTIN_TRAINING_BY_REGION.values(),
                *p.BQ_ML_PREDICTION_BY_REGION.values(),
                p.BQ_BI_ENGINE,
            ]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        region = self.get_string(inputs, "region", "us")
        active_storage_price = p.BQ_ACTIVE_STORAGE_BY_REGION.get(region, p.BQ_ACTIVE_STORAGE_BY_REGION["us"])
        long_term_storage_price = p.BQ_LONG_TERM_STORAGE_BY_REGION.get(
            region, p.BQ_LONG_TERM_STORAGE_BY_REGION["us"]
        )

        pricing_model = self.get_string(inputs, "pricing_model", "on_demand")
        active_storage_gb = self.get_number(inputs, "active_storage_gb")
        long_term_storage_gb = self.get_number(inputs, "long_term_storage_gb")
        streaming_gb = self.get_number(inputs, "streaming_inserts_gb")
        bqml_model_type = self.get_string(inputs, "bqml_model_type", "linear_reg")
        bqml_processed_tib = self.get_number(inputs, "bqml_processed_tib")
        bqml_prediction_tib = self.get_number(inputs, "bqml_prediction_tib")
        bi_engine_gib = self.get_number(inputs, "bi_engine_memory_gib")

        line_items = [
            to_line_item(active_storage_price, active_storage_gb),
            to_line_item(long_term_storage_price, long_term_storage_gb),
            to_line_item(p.BQ_STREAMING_INSERTS, streaming_gb / 0.2),
        ]
        notes = []
        on_demand_price = p.BQ_ON_DEMAND_ANALYSIS_BY_REGION.get(region, p.BQ_ON_DEMAND_ANALYSIS_BY_REGION["us"])
        charge_queries = pricing_model == "on_demand"
        charge_bqml_bytes = pricing_model != "enterprise"
        charge_slots = pricing_model == "enterprise"

        if charge_slots:
            slot_hours = self.get_number(inputs, "enterprise_slot_hours")
            line_items.insert(0, to_line_item(p.BQ_EDITIONS_ENTERPRISE_SLOT, slot_hours))
            notes.append(
                "Modelo BigQuery Enterprise (Editions): consultas e BigQuery ML entram nos slot-hora. "
                "BI Engine é cobrado à parte."
            )
        elif charge_queries:
            query_tib = self.get_number(inputs, "query_tib_per_month")
            billable_tib = max(0.0, query_tib - 1)
            line_items.insert(0, to_line_item(on_demand_price, billable_tib))
            notes.append("Primeiro 1 TiB de consultas por mês é gratuito, já descontado acima.")

        if charge_bqml_bytes and (bqml_processed_tib > 0 or bqml_prediction_tib > 0):
            if bqml_model_type in p.BQ_ML_BUILTIN_TYPES and bqml_processed_tib > 0:
                training_price = p.BQ_ML_BUILTIN_TRAINING_BY_REGION.get(
                    region, p.BQ_ML_BUILTIN_TRAINING_BY_REGION["us"]
                )
                line_items.append(to_line_item(training_price, bqml_processed_tib))
            elif bqml_model_type in p.BQ_ML_EXTERNAL_TYPES and bqml_processed_tib > 0:
                training_price = p.BQ_ML_EXTERNAL_TRAINING_BY_REGION.get(
                    region, p.BQ_ML_EXTERNAL_TRAINING_BY_REGION["us"]
                )
                line_items.append(to_line_item(training_price, bqml_processed_tib))
                notes.append(
                    "Modelo ML externo: esta linha é só o processamento no BigQuery. "
                    "O treino no Vertex AI / Gemini Agent Platform é cobrado à parte."
                )
            if bqml_prediction_tib > 0:
                prediction_price = p.BQ_ML_PREDICTION_BY_REGION.get(region, p.BQ_ML_PREDICTION_BY_REGION["us"])
                line_items.append(to_line_item(prediction_price, bqml_prediction_tib))
        elif pricing_model == "enterprise" and (bqml_processed_tib > 0 or bqml_prediction_tib > 0):
            notes.append(
                "BigQuery ML no Enterprise não gera linha extra por TiB: o treino e a predição consomem slot-hora."
            )

        if bi_engine_gib > 0:
            line_items.append(to_line_item(p.BQ_BI_ENGINE, bi_engine_gib * p.BQ_BI_ENGINE_HOURS_PER_MONTH))
            notes.append(
                f"BI Engine: {bi_engine_gib:g} GiB × {p.BQ_BI_ENGINE_HOURS_PER_MONTH:g} h/mês × "
                f"US$ {p.BQ_BI_ENGINE.unit_price}/GiB-hora."
            )

        total = sum(item.subtotal for item in line_items)

        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=notes,
        )
