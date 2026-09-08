export type FieldType = "number" | "select";

export interface FieldOption {
  value: string;
  label: string;
}

export interface FieldSchema {
  id: string;
  label: string;
  type: FieldType;
  unit?: string | null;
  default?: number | string | null;
  min?: number | null;
  step?: number | null;
  options?: FieldOption[] | null;
  help?: string | null;
}

export interface PricingReference {
  label: string;
  unit: string;
  unit_price: number;
  source_url: string;
  last_verified: string;
  notes?: string | null;
}

export type CloudProvider = "gcp" | "azure" | "aws" | "databricks";
export type CompareScope = CloudProvider | "multicloud";
export type AppTab = CloudProvider | "compare" | "home";

export interface ServiceDefinition {
  id: string;
  name: string;
  category: string;
  description: string;
  fields: FieldSchema[];
  pricing_references: PricingReference[];
  provider?: CloudProvider;
}

export interface LineItem {
  label: string;
  quantity: number;
  unit: string;
  unit_price: number;
  subtotal: number;
  source_url: string;
}

export interface CalculationResult {
  service_id: string;
  currency: string;
  line_items: LineItem[];
  total: number;
  notes: string[];
}

export type ServiceInputs = Record<string, number | string>;
