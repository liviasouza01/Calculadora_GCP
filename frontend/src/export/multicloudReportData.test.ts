import { describe, expect, it } from "vitest";
import type {
  CalculationResult,
  CloudProvider,
  ServiceDefinition,
} from "../types";
import {
  buildMulticloudReportData,
  MULTICLOUD_FUNCTIONS,
} from "./multicloudReportData";

function service(
  id: string,
  name: string,
  provider: CloudProvider,
): ServiceDefinition {
  return {
    id,
    name,
    provider,
    category: "Dados",
    description: "",
    fields: [],
    pricing_references: [],
  };
}

function result(serviceId: string, total: number): CalculationResult {
  return {
    service_id: serviceId,
    currency: "USD",
    line_items: [],
    total,
    notes: [],
  };
}

const services = [
  service("storage", "Cloud Storage", "gcp"),
  service("bigquery", "BigQuery", "gcp"),
  service("azure_adls", "ADLS", "azure"),
  service("azure_exclusive", "Serviço exclusivo", "azure"),
  service("aws_s3", "S3", "aws"),
  service("aws_athena", "Athena", "aws"),
  service("aws_redshift", "Redshift", "aws"),
];

describe("buildMulticloudReportData", () => {
  it("groups providers and equivalent functions while retaining exclusive services", () => {
    const model = buildMulticloudReportData(services, [
      result("storage", 40),
      result("bigquery", 60),
      result("azure_adls", 35),
      result("azure_exclusive", 45),
      result("aws_s3", 30),
      result("aws_athena", 25),
      result("aws_redshift", 40),
    ]);

    expect(model.isMulticloud).toBe(true);
    expect(model.providers.map((group) => group.id)).toEqual([
      "gcp",
      "azure",
      "aws",
    ]);
    expect(model.providers.map((group) => group.total)).toEqual([100, 80, 95]);
    expect(
      model.comparisons.find(
        (row) => row.functionName === "Armazenamento de objetos",
      ),
    ).toMatchObject({
      values: {
        gcp: { serviceNames: ["Cloud Storage"], total: 40 },
        azure: { serviceNames: ["ADLS"], total: 35 },
        aws: { serviceNames: ["S3"], total: 30 },
      },
    });
    expect(
      model.comparisons.find(
        (row) => row.functionName === "Warehouse e SQL",
      )?.values.aws,
    ).toMatchObject({
      serviceNames: ["Athena", "Redshift"],
      total: 65,
    });
    expect(
      model.comparisons.some(
        (row) => row.functionName === "Serviço exclusivo",
      ),
    ).toBe(true);
  });

  it("does not enable multicloud format for one provider", () => {
    const model = buildMulticloudReportData(services, [
      result("storage", 40),
      result("bigquery", 60),
    ]);

    expect(model.isMulticloud).toBe(false);
  });
});

describe("MULTICLOUD_FUNCTIONS", () => {
  it("maps streaming and warehouse calculators used by the agent", () => {
    expect(
      MULTICLOUD_FUNCTIONS.find(
        (group) => group.name === "Streaming analytics",
      )?.serviceIds,
    ).toEqual([
      "dataflow",
      "azure_stream_analytics",
      "aws_flink",
      "dbx_jobs",
    ]);
    expect(
      MULTICLOUD_FUNCTIONS.find(
        (group) => group.name === "Warehouse e SQL",
      )?.serviceIds,
    ).toEqual([
      "bigquery",
      "azure_synapse_sql",
      "aws_athena",
      "aws_redshift",
      "dbx_sql",
    ]);
  });
});
