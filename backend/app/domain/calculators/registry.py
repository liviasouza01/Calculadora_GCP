"""Central registry mapping a service id to its calculator instance.

The API layer only ever talks to this module, never to individual
calculator classes directly, so wiring a new service in is a one-line change.
"""
from __future__ import annotations

from app.domain.calculators.automl_vision import AutomlVisionCalculator
from app.domain.calculators.aws_data import (
    AwsAthenaCalculator,
    AwsDataSyncCalculator,
    AwsDmsCalculator,
    AwsEmrCalculator,
    AwsFlinkCalculator,
    AwsGlueCalculator,
    AwsKinesisCalculator,
    AwsMwaaCalculator,
    AwsRedshiftCalculator,
    AwsS3Calculator,
)
from app.domain.calculators.aws_platform import (
    AwsCloudWatchCalculator,
    AwsCodeBuildCalculator,
    AwsFeatureStoreCalculator,
    AwsLambdaCalculator,
    AwsOpenSearchCalculator,
    AwsQuickSightCalculator,
    AwsRekognitionImageCalculator,
    AwsRekognitionVideoCalculator,
    AwsSagemakerEndpointCalculator,
    AwsSagemakerNotebookCalculator,
    AwsSagemakerTrainingCalculator,
    AwsSecretsManagerCalculator,
)
from app.domain.calculators.azure_data import (
    AzureAdlsCalculator,
    AzureDataFactoryCalculator,
    AzureDmsCalculator,
    AzureEventHubsCalculator,
    AzureStorageMoverCalculator,
    AzureStreamAnalyticsCalculator,
    AzureSynapseCalculator,
    AzureSynapseSparkCalculator,
)
from app.domain.calculators.azure_platform import (
    AzureAiSearchCalculator,
    AzureContainerAppsCalculator,
    AzureKeyVaultCalculator,
    AzureMlEndpointCalculator,
    AzureMlTrainingCalculator,
    AzureMlWorkbenchCalculator,
    AzureMonitorCalculator,
    AzurePipelinesCalculator,
    AzurePowerBiCalculator,
    AzureVideoCalculator,
    AzureVisionCalculator,
)
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators.bigquery import BigQueryCalculator
from app.domain.calculators.cloud_build import CloudBuildCalculator
from app.domain.calculators.cloud_operations import CloudOperationsCalculator
from app.domain.calculators.cloud_run import CloudRunCalculator
from app.domain.calculators.composer import ComposerCalculator
from app.domain.calculators.dataflow import DataflowCalculator
from app.domain.calculators.data_transfer import DataTransferCalculator
from app.domain.calculators.databricks_data import (
    DatabricksAllPurposeCalculator,
    DatabricksDltCalculator,
    DatabricksJobsCalculator,
    DatabricksSqlCalculator,
    DatabricksStorageCalculator,
)
from app.domain.calculators.databricks_platform import (
    DatabricksModelServingCalculator,
    DatabricksMonitoringCalculator,
    DatabricksVectorSearchCalculator,
)
from app.domain.calculators.dataproc import DataprocCalculator
from app.domain.calculators.datastream import DatastreamCalculator
from app.domain.calculators.feature_store import FeatureStoreCalculator
from app.domain.calculators.looker import LookerCalculator
from app.domain.calculators.model_monitoring import ModelMonitoringCalculator
from app.domain.calculators.prediction import PredictionCalculator
from app.domain.calculators.pubsub import PubSubCalculator
from app.domain.calculators.secret_manager import SecretManagerCalculator
from app.domain.calculators.storage import StorageCalculator
from app.domain.calculators.training import TrainingCalculator
from app.domain.calculators.vector_search import VectorSearchCalculator
from app.domain.calculators.vertex_pipelines import VertexPipelinesCalculator
from app.domain.calculators.vertex_workbench import VertexWorkbenchCalculator
from app.domain.calculators.video_intelligence import VideoIntelligenceCalculator
from app.domain.calculators.vision_api import VisionApiCalculator

_CALCULATORS: list[BaseCalculator] = [
    StorageCalculator(),
    BigQueryCalculator(),
    LookerCalculator(),
    TrainingCalculator(),
    PredictionCalculator(),
    FeatureStoreCalculator(),
    VertexPipelinesCalculator(),
    VertexWorkbenchCalculator(),
    VectorSearchCalculator(),
    ModelMonitoringCalculator(),
    AutomlVisionCalculator(),
    VisionApiCalculator(),
    VideoIntelligenceCalculator(),
    DatastreamCalculator(),
    PubSubCalculator(),
    DataTransferCalculator(),
    DataflowCalculator(),
    DataprocCalculator(),
    ComposerCalculator(),
    CloudRunCalculator(),
    CloudOperationsCalculator(),
    SecretManagerCalculator(),
    CloudBuildCalculator(),
    AzureAdlsCalculator(),
    AzureSynapseCalculator(),
    AzureEventHubsCalculator(),
    AzureStreamAnalyticsCalculator(),
    AzureDataFactoryCalculator(),
    AzureDmsCalculator(),
    AzureStorageMoverCalculator(),
    AzureSynapseSparkCalculator(),
    AzureMlTrainingCalculator(),
    AzureMlEndpointCalculator(),
    AzureMlWorkbenchCalculator(),
    AzureAiSearchCalculator(),
    AzureVisionCalculator(),
    AzureVideoCalculator(),
    AzureMonitorCalculator(),
    AzureKeyVaultCalculator(),
    AzureContainerAppsCalculator(),
    AzurePowerBiCalculator(),
    AzurePipelinesCalculator(),
    AwsS3Calculator(),
    AwsAthenaCalculator(),
    AwsRedshiftCalculator(),
    AwsKinesisCalculator(),
    AwsFlinkCalculator(),
    AwsGlueCalculator(),
    AwsDmsCalculator(),
    AwsDataSyncCalculator(),
    AwsEmrCalculator(),
    AwsMwaaCalculator(),
    AwsSagemakerTrainingCalculator(),
    AwsSagemakerEndpointCalculator(),
    AwsSagemakerNotebookCalculator(),
    AwsFeatureStoreCalculator(),
    AwsOpenSearchCalculator(),
    AwsRekognitionImageCalculator(),
    AwsRekognitionVideoCalculator(),
    AwsCloudWatchCalculator(),
    AwsSecretsManagerCalculator(),
    AwsLambdaCalculator(),
    AwsCodeBuildCalculator(),
    AwsQuickSightCalculator(),
    DatabricksStorageCalculator(),
    DatabricksSqlCalculator(),
    DatabricksJobsCalculator(),
    DatabricksAllPurposeCalculator(),
    DatabricksDltCalculator(),
    DatabricksModelServingCalculator(),
    DatabricksVectorSearchCalculator(),
    DatabricksMonitoringCalculator(),
]

REGISTRY: dict[str, BaseCalculator] = {calc.definition.id: calc for calc in _CALCULATORS}


def list_definitions():
    return [calc.definition for calc in _CALCULATORS]


def get_calculator(service_id: str) -> BaseCalculator | None:
    return REGISTRY.get(service_id)
