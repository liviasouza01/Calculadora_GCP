import { PROVIDERS } from "../providers";
import type {
  AgentComparisonGroup,
  CalculationResult,
  CloudProvider,
  ServiceDefinition,
} from "../types";

export const MULTICLOUD_FUNCTIONS: {
  name: string;
  serviceIds: string[];
}[] = [
  {
    name: "Armazenamento de objetos",
    serviceIds: ["storage", "azure_adls", "aws_s3", "dbx_storage"],
  },
  {
    name: "Warehouse e SQL",
    serviceIds: [
      "bigquery",
      "azure_synapse_sql",
      "aws_athena",
      "aws_redshift",
      "dbx_sql",
    ],
  },
  {
    name: "Eventos e mensageria",
    serviceIds: ["pubsub", "azure_event_hubs", "aws_kinesis"],
  },
  {
    name: "CDC serverless por volume",
    serviceIds: ["datastream"],
  },
  {
    name: "Migração e replicação gerenciada",
    serviceIds: ["azure_dms", "aws_dms"],
  },
  {
    name: "Transferência de arquivos",
    serviceIds: ["data_transfer", "azure_storage_mover", "aws_datasync"],
  },
  {
    name: "ETL e pipelines batch",
    serviceIds: [
      "dataflow",
      "azure_data_factory",
      "aws_glue",
      "dbx_jobs",
      "dbx_dlt",
    ],
  },
  {
    name: "Spark e processamento",
    serviceIds: [
      "dataproc",
      "azure_synapse_spark",
      "aws_emr",
      "dbx_all_purpose",
    ],
  },
  {
    name: "Orquestração",
    serviceIds: ["composer", "azure_data_factory", "aws_mwaa", "dbx_jobs"],
  },
  {
    name: "Streaming analytics",
    serviceIds: [
      "dataflow",
      "azure_stream_analytics",
      "aws_flink",
      "dbx_jobs",
    ],
  },
  {
    name: "Treinamento de ML",
    serviceIds: [
      "training",
      "automl_vision",
      "azure_ml_training",
      "aws_sagemaker_training",
      "dbx_jobs",
    ],
  },
  {
    name: "Inferência de ML",
    serviceIds: [
      "prediction",
      "azure_ml_endpoint",
      "aws_sagemaker_endpoint",
      "dbx_model_serving",
    ],
  },
  {
    name: "Notebooks de ML",
    serviceIds: [
      "vertex_workbench",
      "azure_ml_workbench",
      "aws_sagemaker_notebook",
      "dbx_all_purpose",
    ],
  },
  {
    name: "Feature store",
    serviceIds: ["feature_store", "aws_feature_store"],
  },
  {
    name: "Busca vetorial",
    serviceIds: [
      "vector_search",
      "azure_ai_search",
      "aws_opensearch",
      "dbx_vector_search",
    ],
  },
  {
    name: "Monitoramento de modelos",
    serviceIds: [
      "model_monitoring",
      "azure_monitor",
      "aws_cloudwatch",
      "dbx_lakehouse_monitoring",
    ],
  },
  {
    name: "Análise de imagens",
    serviceIds: ["vision_api", "azure_ai_vision", "aws_rekognition_image"],
  },
  {
    name: "Análise de vídeo",
    serviceIds: [
      "video_intelligence",
      "azure_ai_video",
      "aws_rekognition_video",
    ],
  },
  {
    name: "Aplicação serverless",
    serviceIds: ["cloud_run", "azure_container_apps", "aws_lambda"],
  },
  {
    name: "Logs e observabilidade",
    serviceIds: ["cloud_operations", "azure_monitor", "aws_cloudwatch"],
  },
  {
    name: "Secrets",
    serviceIds: ["secret_manager", "azure_key_vault", "aws_secrets_manager"],
  },
  {
    name: "CI/CD",
    serviceIds: ["cloud_build", "azure_pipelines", "aws_codebuild"],
  },
  {
    name: "BI e dashboards",
    serviceIds: ["looker", "azure_power_bi", "aws_quicksight"],
  },
];

export interface ProviderReportGroup {
  id: CloudProvider;
  label: string;
  services: {
    definition: ServiceDefinition;
    result: CalculationResult;
  }[];
  total: number;
}

export interface ComparisonValue {
  serviceNames: string[];
  total: number;
}

export interface ComparisonRow {
  functionName: string;
  values: Partial<Record<CloudProvider, ComparisonValue>>;
  rationale?: string;
  comparability?: AgentComparisonGroup["comparability"];
}

export interface MulticloudReportData {
  isMulticloud: boolean;
  providers: ProviderReportGroup[];
  comparisons: ComparisonRow[];
}

interface ReportFunctionGroup {
  name: string;
  serviceIds: string[];
  rationale?: string;
  comparability?: AgentComparisonGroup["comparability"];
}

function providerOf(service: ServiceDefinition): CloudProvider {
  return service.provider ?? "gcp";
}

export function buildMulticloudReportData(
  services: ServiceDefinition[],
  results: CalculationResult[],
  comparisonGroups: AgentComparisonGroup[] = [],
): MulticloudReportData {
  const definitions = new Map(services.map((service) => [service.id, service]));
  const active = results.flatMap((result) => {
    const definition = definitions.get(result.service_id);
    return definition ? [{ definition, result }] : [];
  });

  const providers = PROVIDERS.flatMap((provider) => {
    const providerServices = active.filter(
      ({ definition }) => providerOf(definition) === provider.id,
    );
    if (providerServices.length === 0) {
      return [];
    }
    return [
      {
        id: provider.id,
        label: provider.label,
        services: providerServices,
        total: providerServices.reduce(
          (sum, item) => sum + item.result.total,
          0,
        ),
      },
    ];
  });

  const mappedIds = new Set<string>();
  const comparisons: ComparisonRow[] = [];
  const groups: ReportFunctionGroup[] =
    comparisonGroups.length > 0
      ? comparisonGroups.map((group) => ({
          name: group.function_name,
          serviceIds: group.service_ids,
          rationale: group.rationale,
          comparability: group.comparability,
        }))
      : MULTICLOUD_FUNCTIONS;

  for (const group of groups) {
    const matches = active.filter(({ definition }) =>
      group.serviceIds.includes(definition.id),
    );
    if (matches.length === 0) {
      continue;
    }

    const values: Partial<Record<CloudProvider, ComparisonValue>> = {};
    for (const provider of PROVIDERS) {
      const providerMatches = matches.filter(
        ({ definition }) => providerOf(definition) === provider.id,
      );
      if (providerMatches.length === 0) {
        continue;
      }
      values[provider.id] = {
        serviceNames: providerMatches.map(({ definition }) => definition.name),
        total: providerMatches.reduce(
          (sum, item) => sum + item.result.total,
          0,
        ),
      };
      providerMatches.forEach(({ definition }) => mappedIds.add(definition.id));
    }
    comparisons.push({
      functionName: group.name,
      values,
      rationale: group.rationale,
      comparability: group.comparability,
    });
  }

  for (const item of active) {
    if (mappedIds.has(item.definition.id)) {
      continue;
    }
    const provider = providerOf(item.definition);
    comparisons.push({
      functionName: item.definition.name,
      rationale:
        comparisonGroups.length > 0
          ? "Serviço não agrupado pelo agente com um equivalente direto."
          : undefined,
      comparability:
        comparisonGroups.length > 0 ? "no_direct_equivalent" : undefined,
      values: {
        [provider]: {
          serviceNames: [item.definition.name],
          total: item.result.total,
        },
      },
    });
  }

  return {
    isMulticloud: providers.length > 1,
    providers,
    comparisons,
  };
}
