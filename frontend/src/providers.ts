import type { AppTab, CloudProvider, CompareScope } from "./types";

export const PROVIDERS: { id: CloudProvider; label: string }[] = [
  { id: "gcp", label: "Google" },
  { id: "azure", label: "Azure" },
  { id: "aws", label: "AWS" },
  { id: "databricks", label: "Databricks" },
];

export const COMPARE_SCOPES: { id: CompareScope; label: string }[] = [
  ...PROVIDERS,
  { id: "multicloud", label: "Multicloud" },
];

export const APP_TABS: { id: AppTab; label: string }[] = [
  { id: "home", label: "Início" },
  ...PROVIDERS,
  { id: "compare", label: "Comparar" },
];

export const CLIENT_TABS: { id: AppTab; label: string }[] = [...PROVIDERS];

export const APP_TITLE = "Calculadora de Dados, ML e Visão Computacional";

export const PROVIDER_COPY: Record<
  CloudProvider,
  { empty: string; disclaimer: string; pdfTitle: string; pricesCta: string }
> = {
  gcp: {
    empty: "Nenhum serviço GCP carregado.",
    disclaimer:
      "Preços públicos do Google Cloud (região US), sem compromisso de uso e sem impostos. Confirme na fonte oficial antes de decidir.",
    pdfTitle: "Relatorio de custos - GCP",
    pricesCta: "preços oficiais do Google Cloud",
  },
  azure: {
    empty: "Nenhum serviço Azure carregado.",
    disclaimer:
      "Preços públicos pay-as-you-go (East US), sem compromisso e sem impostos. Confirme na calculadora oficial da Microsoft.",
    pdfTitle: "Relatorio de custos - Azure",
    pricesCta: "preços oficiais da Azure",
  },
  aws: {
    empty: "Nenhum serviço AWS carregado.",
    disclaimer:
      "Preços públicos on-demand (us-east-1), sem Savings Plans e sem impostos. Confirme na calculadora oficial da AWS.",
    pdfTitle: "Relatorio de custos - AWS",
    pricesCta: "preços oficiais da AWS",
  },
  databricks: {
    empty: "Nenhum serviço Databricks carregado.",
    disclaimer:
      "Lista AWS Premium por DBU. Compute clássico não inclui a VM da nuvem. Confirme em databricks.com/product/pricing.",
    pdfTitle: "Relatorio de custos - Databricks",
    pricesCta: "preços oficiais do Databricks",
  },
};
