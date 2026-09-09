from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.calculators.base import BaseCalculator
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


def _result(service_id: str, line_items, notes: list[str] | None = None) -> CalculationResult:
    return CalculationResult(
        service_id=service_id,
        line_items=line_items,
        total=round(sum(item.subtotal for item in line_items), 2),
        notes=notes or [],
    )


class AzureMlTrainingCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ml_training",
        name="Azure Machine Learning Training",
        category="Machine Learning",
        provider="azure",
        description="Compute gerenciado para treinamento de modelos.",
        fields=[
            FieldSchema(
                id="instance_hours",
                label="Instância-horas",
                type="number",
                unit="hora/mês",
                default=100,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_ML_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_ML_COMPUTE, self.get_number(inputs, "instance_hours"))],
            ["Azure ML não cobra taxa adicional de plataforma; este item representa o compute."],
        )


class AzureMlEndpointCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ml_endpoint",
        name="Azure Machine Learning Online Endpoints",
        category="Machine Learning",
        provider="azure",
        description="Compute para inferência online gerenciada.",
        fields=[
            FieldSchema(
                id="instance_hours",
                label="Instância-horas",
                type="number",
                unit="hora/mês",
                default=730,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_ML_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_ML_COMPUTE, self.get_number(inputs, "instance_hours"))],
        )


class AzureMlWorkbenchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ml_workbench",
        name="Azure Machine Learning Compute Instance",
        category="Machine Learning",
        provider="azure",
        description="Ambiente de notebooks e desenvolvimento para cientistas de dados.",
        fields=[
            FieldSchema(
                id="instance_hours",
                label="Instância-horas",
                type="number",
                unit="hora/mês",
                default=160,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_ML_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_ML_COMPUTE, self.get_number(inputs, "instance_hours"))],
        )


class AzureAiSearchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ai_search",
        name="Azure AI Search",
        category="Machine Learning",
        provider="azure",
        description="Busca vetorial e semântica gerenciada.",
        fields=[
            FieldSchema(
                id="search_unit_hours",
                label="Search unit-horas",
                type="number",
                unit="SU-hora/mês",
                default=730,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_AI_SEARCH_SU)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_AI_SEARCH_SU, self.get_number(inputs, "search_unit_hours"))],
        )


class AzureVisionCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ai_vision",
        name="Azure AI Vision",
        category="Visão Computacional",
        provider="azure",
        description="OCR, tags e detecção de objetos em imagens.",
        fields=[
            FieldSchema(
                id="thousand_transactions",
                label="Transações",
                type="number",
                unit="milhares/mês",
                default=10,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_VISION_TRANSACTIONS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_VISION_TRANSACTIONS, self.get_number(inputs, "thousand_transactions"))],
        )


class AzureVideoCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_ai_video",
        name="Azure AI Video",
        category="Visão Computacional",
        provider="azure",
        description="Análise automatizada de conteúdo de vídeo.",
        fields=[
            FieldSchema(
                id="minutes",
                label="Vídeo analisado",
                type="number",
                unit="minutos/mês",
                default=1000,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_VIDEO_MINUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_VIDEO_MINUTE, self.get_number(inputs, "minutes"))],
        )


class AzureMonitorCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_monitor",
        name="Azure Monitor",
        category="Operação e Segurança",
        provider="azure",
        description="Ingestão de logs e observabilidade da solução.",
        fields=[
            FieldSchema(
                id="logging_gb",
                label="Logs ingeridos",
                type="number",
                unit="GB/mês",
                default=50,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_MONITOR_LOGS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_MONITOR_LOGS, self.get_number(inputs, "logging_gb"))],
        )


class AzureKeyVaultCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_key_vault",
        name="Azure Key Vault",
        category="Operação e Segurança",
        provider="azure",
        description="Armazenamento e acesso a secrets da aplicação.",
        fields=[
            FieldSchema(
                id="operations_blocks",
                label="Operações",
                type="number",
                unit="10.000 operações/mês",
                default=10,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_KEY_VAULT_OPS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_KEY_VAULT_OPS, self.get_number(inputs, "operations_blocks"))],
        )


class AzureContainerAppsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_container_apps",
        name="Azure Container Apps",
        category="Aplicação e DevOps",
        provider="azure",
        description="Execução serverless de containers.",
        fields=[
            FieldSchema(id="vcpu_hours", label="vCPU-horas", type="number", unit="vCPU-hora/mês", default=100, min=0),
            FieldSchema(
                id="memory_gib_hours",
                label="Memória",
                type="number",
                unit="GiB-hora/mês",
                default=200,
                min=0,
            ),
            FieldSchema(
                id="requests_millions",
                label="Requisições",
                type="number",
                unit="milhões/mês",
                default=1,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.AZURE_CONTAINER_APPS_VCPU),
            to_reference(p.AZURE_CONTAINER_APPS_MEMORY),
            to_reference(p.AZURE_CONTAINER_APPS_REQUESTS),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AZURE_CONTAINER_APPS_VCPU, self.get_number(inputs, "vcpu_hours")),
                to_line_item(p.AZURE_CONTAINER_APPS_MEMORY, self.get_number(inputs, "memory_gib_hours")),
                to_line_item(p.AZURE_CONTAINER_APPS_REQUESTS, self.get_number(inputs, "requests_millions")),
            ],
        )


class AzurePowerBiCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_power_bi",
        name="Microsoft Power BI",
        category="BI e Visualização",
        provider="azure",
        description="Licenças Power BI Pro para criação e consumo de relatórios.",
        fields=[
            FieldSchema(
                id="users",
                label="Usuários Pro",
                type="number",
                unit="usuários/mês",
                default=10,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_POWER_BI_PRO)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_POWER_BI_PRO, self.get_number(inputs, "users"))],
        )


class AzurePipelinesCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="azure_pipelines",
        name="Azure Pipelines",
        category="Aplicação e DevOps",
        provider="azure",
        description="Jobs hospedados para build e integração contínua.",
        fields=[
            FieldSchema(
                id="parallel_jobs",
                label="Jobs paralelos",
                type="number",
                unit="jobs/mês",
                default=1,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AZURE_PIPELINES_PARALLEL)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AZURE_PIPELINES_PARALLEL, self.get_number(inputs, "parallel_jobs"))],
        )
