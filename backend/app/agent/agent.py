"""Agente ADK no formato do tutorial oficial da Google.

Quickstart: Agent + funções-ferramenta (FunctionTool) + instrução.
https://google.github.io/adk-docs/get-started/python/
https://google.github.io/adk-docs/tools-custom/
"""

from __future__ import annotations

import json

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool, ToolContext

from app.domain.calculators.registry import get_calculator, list_definitions

MODEL_ID = "gemini-flash-latest"

CLOUD_FUNCTION_MAP = """
Quando comparar nuvens, preencha SOMENTE equivalentes da mesma função, com os MESMOS volumes.
Use estes ids do catálogo:

Função | Google | Azure | AWS | Databricks
Object storage | storage | azure_adls | aws_s3 | dbx_storage
Warehouse / analytics SQL | bigquery | azure_synapse_sql | aws_athena e aws_redshift | dbx_sql
Eventos / mensageria | pubsub | azure_event_hubs | aws_kinesis | (sem equivalente; não invente)
CDC / replicação | datastream | azure_dms | aws_dms | (sem equivalente)
Transferência de arquivos | data_transfer | azure_storage_mover | aws_datasync | (sem equivalente)
ETL / pipelines batch | dataflow (job_type batch) | azure_data_factory | aws_glue | dbx_jobs e dbx_dlt
Spark / processamento | dataproc | azure_synapse_spark | aws_emr | dbx_all_purpose
Orquestração | composer | azure_data_factory | aws_mwaa | dbx_jobs
Streaming analytics | dataflow (job_type streaming) | azure_stream_analytics | aws_flink | dbx_jobs
Treinamento ML | training ou automl_vision | azure_ml_training | aws_sagemaker_training | dbx_jobs
Inferência ML | prediction | azure_ml_endpoint | aws_sagemaker_endpoint | dbx_model_serving
Notebooks ML | vertex_workbench | azure_ml_workbench | aws_sagemaker_notebook | dbx_all_purpose
Feature store | feature_store | (sem cobrança separada comparável) | aws_feature_store | (sem cobrança separada comparável)
Busca vetorial | vector_search | azure_ai_search | aws_opensearch | dbx_vector_search
Monitoramento de modelos | model_monitoring | azure_monitor | aws_cloudwatch | dbx_lakehouse_monitoring
Análise de imagens | vision_api | azure_ai_vision | aws_rekognition_image | (sem equivalente; não invente)
Análise de vídeo | video_intelligence | azure_ai_video | aws_rekognition_video | (sem equivalente; não invente)
Aplicação serverless | cloud_run | azure_container_apps | aws_lambda | (sem equivalente; não invente)
Logs e observabilidade | cloud_operations | azure_monitor | aws_cloudwatch | (sem equivalente; não invente)
Secrets | secret_manager | azure_key_vault | aws_secrets_manager | (sem equivalente; não invente)
CI/CD | cloud_build | azure_pipelines | aws_codebuild | (sem equivalente; não invente)
BI e dashboards | looker | azure_power_bi | aws_quicksight | dbx_sql (dashboards incluídos no warehouse)

Regras:
- Se a proposta usa Cloud Storage, preencha também azure_adls, aws_s3 e dbx_storage com o mesmo GB.
- dbx_storage mede o armazenamento gerenciado pelo Databricks e complementa o object storage
  da nuvem hospedeira; mantenha o mesmo volume para tornar essa parcela explícita.
- Se usa BigQuery, preencha azure_synapse_sql, aws_athena (e redshift se for warehouse) e dbx_sql.
- Não reutilize aws_kinesis como processamento: ele representa mensageria; para streaming
  analytics use aws_flink.
- Em ETL batch, defina explicitamente dataflow.job_type como batch.
- Para ML, visão e operação, use os equivalentes explícitos acima e preserve horas, GB,
  número de transações, imagens, minutos e requisições sempre que as unidades permitirem.
- Para BI, use azure_power_bi, aws_quicksight e os dashboards incluídos em dbx_sql.
- Databricks não é uma nuvem de infraestrutura: compute clássico deve incluir DBUs e
  cloud_vm_hours; serverless não deve adicionar VM.
- Não misture funções (ex.: não use S3 no lugar de BigQuery).
"""


def list_calculator_services(provider: str = "") -> dict:
    """Lista os serviços da calculadora e os campos que cada um aceita.

    Args:
        provider: gcp, azure, aws, databricks ou multicloud (lista todos). Vazio lista todos.

    Returns:
        dict: status e a lista de serviços com id, nome, descrição e campos.
    """
    wanted = (provider or "").strip().lower()
    if wanted in {"multicloud", "all", "*"}:
        wanted = ""
    services = []
    for definition in list_definitions():
        if wanted and definition.provider != wanted:
            continue
        services.append(
            {
                "id": definition.id,
                "name": definition.name,
                "provider": definition.provider,
                "description": definition.description,
                "fields": [
                    {
                        "id": field.id,
                        "label": field.label,
                        "type": field.type,
                        "unit": field.unit,
                        "default": field.default,
                        "options": (
                            [{"value": opt.value, "label": opt.label} for opt in field.options]
                            if field.options
                            else None
                        ),
                        "help": field.help,
                    }
                    for field in definition.fields
                ],
            }
        )
    return {"status": "success", "services": services}


def fill_service(
    service_id: str,
    inputs_json: str,
    tool_context: ToolContext,
    scenario: str = "to_be",
) -> dict:
    """Registra os valores estimados de um serviço na sessão da calculadora.

    Args:
        service_id: id do serviço (ex.: storage, bigquery, looker).
        inputs_json: JSON com os campos do serviço, por exemplo
            '{"region":"us","storage_gb":2000}'.
        tool_context: injetado pelo ADK; não passar na chamada do modelo.
        scenario: as_is (calculadora atual) ou to_be (proposta). Default to_be.

    Returns:
        dict: status success/error e os inputs aceitos.
    """
    calculator = get_calculator(service_id)
    if calculator is None:
        return {"status": "error", "error_message": f"Serviço desconhecido: {service_id}"}

    bucket = "as_is" if str(scenario or "to_be").strip().lower() in {"as_is", "asis", "as-is"} else "to_be"
    source = str(tool_context.state.get("source_provider") or "").strip().lower()
    target = str(tool_context.state.get("target_provider") or "").strip().lower()
    wanted = source if bucket == "as_is" else target
    if wanted and wanted not in {"multicloud", "all", "*"} and calculator.definition.provider != wanted:
        return {
            "status": "error",
            "error_message": (
                f"Serviço '{service_id}' é de {calculator.definition.provider}, "
                f"não de '{wanted}' para scenario={bucket}."
            ),
        }

    try:
        raw = json.loads(inputs_json) if inputs_json else {}
    except json.JSONDecodeError:
        return {"status": "error", "error_message": "inputs_json não é um JSON válido."}

    if not isinstance(raw, dict):
        return {"status": "error", "error_message": "inputs_json deve ser um objeto JSON."}

    coerced: dict[str, float | str] = {}
    for field in calculator.definition.fields:
        if field.id not in raw:
            if field.default is not None:
                coerced[field.id] = field.default
            continue
        value = raw[field.id]
        if field.type == "number":
            try:
                coerced[field.id] = float(value)
            except (TypeError, ValueError):
                return {
                    "status": "error",
                    "error_message": f"Campo '{field.id}' precisa ser numérico.",
                }
        else:
            text = str(value)
            if field.options:
                allowed = {opt.value for opt in field.options}
                if text not in allowed:
                    return {
                        "status": "error",
                        "error_message": (
                            f"Campo '{field.id}' deve ser um de: {sorted(allowed)}"
                        ),
                    }
            coerced[field.id] = text

    filled = tool_context.state.get("filled_services", {})
    filled[service_id] = coerced
    tool_context.state["filled_services"] = filled
    key = "filled_as_is" if bucket == "as_is" else "filled_to_be"
    bucket_map = tool_context.state.get(key, {})
    bucket_map[service_id] = coerced
    tool_context.state[key] = bucket_map
    return {
        "status": "success",
        "service_id": service_id,
        "scenario": bucket,
        "inputs": coerced,
    }


list_services_tool = FunctionTool(func=list_calculator_services)
fill_service_tool = FunctionTool(func=fill_service)

root_agent = Agent(
    model=MODEL_ID,
    name="root_agent",
    description=(
        "Interpreta briefing ou calculadora existente e preenche custos "
        "em Google, Azure, AWS ou Databricks."
    ),
    instruction="""Você preenche a calculadora de Dados, ML e Visão Computacional.

Fluxo obrigatório:
1. Chame list_calculator_services. Se a origem/destino for multicloud, use provider='multicloud' (catálogo completo).
2. Leia todos os anexos e as notas extras. Um PDF pode ter contas de várias nuvens ao mesmo tempo; se a origem for multicloud, preencha todos os serviços reconhecidos.
3. Chame fill_service com service_id, inputs_json e scenario:
   - scenario='as_is' para o que JÁ existe. Se a origem for multicloud, use ids de qualquer nuvem que aparecer no anexo.
   - scenario='to_be' para a proposta. Se o destino for multicloud, misture nuvens conforme as notas extras.
4. Tarefas:
   - CONTEXTO: só scenario='to_be'. Se pedirem comparação de nuvens, preencha cada função nas 4 nuvens pelos equivalentes abaixo, mesmos volumes. Senão, só a nuvem da proposta.

Equivalências (ids):
""" + CLOUD_FUNCTION_MAP + """
   - COMPARAR: as_is na origem e to_be no destino (destino pode ser uma nuvem ou multicloud).
   - COMPLEMENTAR: as_is = o anexo; to_be = anexo + gaps. Destino pode ser a mesma nuvem ou multicloud.
5. Responda em português com AS IS vs TO-BE e as premissas.

Não calcule preços você mesmo. Só preencha os inputs via fill_service.""",
    tools=[list_services_tool, fill_service_tool],
)
