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


def list_calculator_services() -> dict:
    """Lista os serviços GCP da calculadora e os campos que cada um aceita.

    Returns:
        dict: status e a lista de serviços com id, nome, descrição e campos.
    """
    services = []
    for definition in list_definitions():
        services.append(
            {
                "id": definition.id,
                "name": definition.name,
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


def fill_service(service_id: str, inputs_json: str, tool_context: ToolContext) -> dict:
    """Registra os valores estimados de um serviço na sessão da calculadora.

    Args:
        service_id: id do serviço (ex.: storage, bigquery, looker).
        inputs_json: JSON com os campos do serviço, por exemplo
            '{"region":"us","storage_gb":2000}'.
        tool_context: injetado pelo ADK; não passar na chamada do modelo.

    Returns:
        dict: status success/error e os inputs aceitos.
    """
    calculator = get_calculator(service_id)
    if calculator is None:
        return {"status": "error", "error_message": f"Serviço desconhecido: {service_id}"}

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
    return {"status": "success", "service_id": service_id, "inputs": coerced}


list_services_tool = FunctionTool(func=list_calculator_services)
fill_service_tool = FunctionTool(func=fill_service)

root_agent = Agent(
    model=MODEL_ID,
    name="root_agent",
    description=(
        "Interpreta transcrições de conversa e desenhos de arquitetura "
        "para preencher a calculadora de custos GCP."
    ),
    instruction="""Você preenche a calculadora de custos de dados no Google Cloud.

Fluxo obrigatório:
1. Chame list_calculator_services para ver ids, campos e opções válidas.
2. Leia todos os anexos: transcrições (PDF/TXT/Word) e, se houver, desenhos de arquitetura (PNG/JPG). Cruze as evidências entre os arquivos.
3. Identifique quais serviços GCP do catálogo aparecem de fato no briefing.
4. Para cada serviço relevante, chame fill_service com service_id e inputs_json.
   - Use apenas ids e valores de opções retornados por list_calculator_services.
   - Estime quantidades a partir do texto/desenho. Se o briefing não der um número, use o default do campo.
   - Não invente serviços que não estejam no catálogo.
   - Não preencha um serviço se não houver evidência razoável de que ele entra no projeto.
5. Ao final, responda em português com um resumo curto: quais serviços preencheu e as premissas.

Não calcule preços você mesmo. Só preencha os inputs via fill_service.""",
    tools=[list_services_tool, fill_service_tool],
)
