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


class AwsSagemakerTrainingCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_sagemaker_training",
        name="Amazon SageMaker AI Training",
        category="Machine Learning",
        provider="aws",
        description="Instâncias gerenciadas para treinamento de modelos.",
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
        pricing_references=[to_reference(p.AWS_SAGEMAKER_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_SAGEMAKER_COMPUTE, self.get_number(inputs, "instance_hours"))],
        )


class AwsSagemakerEndpointCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_sagemaker_endpoint",
        name="Amazon SageMaker AI Endpoint",
        category="Machine Learning",
        provider="aws",
        description="Hospedagem gerenciada para inferência em tempo real.",
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
        pricing_references=[to_reference(p.AWS_SAGEMAKER_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_SAGEMAKER_COMPUTE, self.get_number(inputs, "instance_hours"))],
        )


class AwsSagemakerNotebookCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_sagemaker_notebook",
        name="Amazon SageMaker Studio Notebooks",
        category="Machine Learning",
        provider="aws",
        description="Ambiente gerenciado de notebooks para ciência de dados.",
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
        pricing_references=[to_reference(p.AWS_SAGEMAKER_COMPUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_SAGEMAKER_COMPUTE, self.get_number(inputs, "instance_hours"))],
        )


class AwsFeatureStoreCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_feature_store",
        name="Amazon SageMaker Feature Store",
        category="Machine Learning",
        provider="aws",
        description="Armazenamento online de features para treino e serving.",
        fields=[
            FieldSchema(id="storage_gb", label="Storage online", type="number", unit="GB/mês", default=50, min=0),
            FieldSchema(id="writes_millions", label="Gravações", type="number", unit="milhões/mês", default=10, min=0),
            FieldSchema(id="reads_millions", label="Leituras", type="number", unit="milhões/mês", default=10, min=0),
        ],
        pricing_references=[
            to_reference(p.AWS_FEATURE_STORE_STORAGE),
            to_reference(p.AWS_FEATURE_STORE_WRITE),
            to_reference(p.AWS_FEATURE_STORE_READ),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AWS_FEATURE_STORE_STORAGE, self.get_number(inputs, "storage_gb")),
                to_line_item(p.AWS_FEATURE_STORE_WRITE, self.get_number(inputs, "writes_millions")),
                to_line_item(p.AWS_FEATURE_STORE_READ, self.get_number(inputs, "reads_millions")),
            ],
        )


class AwsOpenSearchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_opensearch",
        name="Amazon OpenSearch Serverless",
        category="Machine Learning",
        provider="aws",
        description="Busca vetorial e semântica serverless.",
        fields=[
            FieldSchema(id="ocu_hours", label="OCU-horas", type="number", unit="OCU-hora/mês", default=730, min=0),
            FieldSchema(id="storage_gb", label="Índices", type="number", unit="GB/mês", default=50, min=0),
        ],
        pricing_references=[to_reference(p.AWS_OPENSEARCH_OCU), to_reference(p.AWS_OPENSEARCH_STORAGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AWS_OPENSEARCH_OCU, self.get_number(inputs, "ocu_hours")),
                to_line_item(p.AWS_OPENSEARCH_STORAGE, self.get_number(inputs, "storage_gb")),
            ],
        )


class AwsRekognitionImageCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_rekognition_image",
        name="Amazon Rekognition Image",
        category="Visão Computacional",
        provider="aws",
        description="Detecção de labels, objetos e moderação de imagens.",
        fields=[
            FieldSchema(
                id="thousand_images",
                label="Imagens analisadas",
                type="number",
                unit="milhares/mês",
                default=10,
                min=0,
            )
        ],
        pricing_references=[to_reference(p.AWS_REKOGNITION_IMAGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_REKOGNITION_IMAGE, self.get_number(inputs, "thousand_images"))],
        )


class AwsRekognitionVideoCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_rekognition_video",
        name="Amazon Rekognition Video",
        category="Visão Computacional",
        provider="aws",
        description="Detecção de labels e objetos em vídeo.",
        fields=[
            FieldSchema(id="minutes", label="Vídeo analisado", type="number", unit="minutos/mês", default=1000, min=0)
        ],
        pricing_references=[to_reference(p.AWS_REKOGNITION_VIDEO)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_REKOGNITION_VIDEO, self.get_number(inputs, "minutes"))],
        )


class AwsCloudWatchCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_cloudwatch",
        name="Amazon CloudWatch",
        category="Operação e Segurança",
        provider="aws",
        description="Ingestão de logs e observabilidade da solução.",
        fields=[
            FieldSchema(id="logging_gb", label="Logs ingeridos", type="number", unit="GB/mês", default=50, min=0)
        ],
        pricing_references=[to_reference(p.AWS_CLOUDWATCH_LOGS)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_CLOUDWATCH_LOGS, self.get_number(inputs, "logging_gb"))],
        )


class AwsSecretsManagerCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_secrets_manager",
        name="AWS Secrets Manager",
        category="Operação e Segurança",
        provider="aws",
        description="Armazenamento e acesso a secrets da aplicação.",
        fields=[
            FieldSchema(id="secrets", label="Secrets", type="number", unit="secret/mês", default=10, min=0),
            FieldSchema(
                id="api_blocks",
                label="Chamadas de API",
                type="number",
                unit="10.000 chamadas/mês",
                default=10,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AWS_SECRET_MONTH), to_reference(p.AWS_SECRET_API)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AWS_SECRET_MONTH, self.get_number(inputs, "secrets")),
                to_line_item(p.AWS_SECRET_API, self.get_number(inputs, "api_blocks")),
            ],
        )


class AwsLambdaCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_lambda",
        name="AWS Lambda",
        category="Aplicação e DevOps",
        provider="aws",
        description="Execução serverless de funções para APIs e processamento.",
        fields=[
            FieldSchema(id="requests_millions", label="Requisições", type="number", unit="milhões/mês", default=1, min=0),
            FieldSchema(
                id="gb_seconds_millions",
                label="Duração",
                type="number",
                unit="milhões de GB-s/mês",
                default=0.1,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AWS_LAMBDA_REQUESTS), to_reference(p.AWS_LAMBDA_DURATION)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AWS_LAMBDA_REQUESTS, self.get_number(inputs, "requests_millions")),
                to_line_item(p.AWS_LAMBDA_DURATION, self.get_number(inputs, "gb_seconds_millions")),
            ],
        )


class AwsCodeBuildCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_codebuild",
        name="AWS CodeBuild",
        category="Aplicação e DevOps",
        provider="aws",
        description="Build e integração contínua gerenciados.",
        fields=[
            FieldSchema(id="build_minutes", label="Minutos de build", type="number", unit="minutos/mês", default=1000, min=0)
        ],
        pricing_references=[to_reference(p.AWS_CODEBUILD_MINUTE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [to_line_item(p.AWS_CODEBUILD_MINUTE, self.get_number(inputs, "build_minutes"))],
        )


class AwsQuickSightCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_quicksight",
        name="Amazon QuickSight",
        category="BI e Visualização",
        provider="aws",
        description="BI gerenciado para autores e leitores de dashboards.",
        fields=[
            FieldSchema(id="authors", label="Autores", type="number", unit="autores/mês", default=2, min=0),
            FieldSchema(id="readers", label="Leitores", type="number", unit="leitores/mês", default=10, min=0),
        ],
        pricing_references=[
            to_reference(p.AWS_QUICKSIGHT_AUTHOR),
            to_reference(p.AWS_QUICKSIGHT_READER),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        return _result(
            self.definition.id,
            [
                to_line_item(p.AWS_QUICKSIGHT_AUTHOR, self.get_number(inputs, "authors")),
                to_line_item(p.AWS_QUICKSIGHT_READER, self.get_number(inputs, "readers")),
            ],
        )
