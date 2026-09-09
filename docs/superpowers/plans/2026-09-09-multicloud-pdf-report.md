# Multicloud PDF Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export one PDF containing every populated cloud, each cloud's detailed costs, and a consolidated function-and-cost comparison.

**Architecture:** A pure report-data builder will group active calculations by provider and functional equivalence. The existing PDF exporter will consume that model only when two or more providers are present; the current single-cloud path remains unchanged.

**Tech Stack:** React 18, TypeScript 5.6, Vitest, jsPDF, jspdf-autotable.

## Global Constraints

- Do not change calculator prices or backend calculations.
- Do not change the AS IS versus TO-BE report.
- Preserve the current single-cloud PDF behavior.
- Include only populated services and providers.
- Keep provider order as GCP, Azure, AWS, Databricks.

---

### Task 1: Build the multicloud report model

**Files:**
- Create: `frontend/src/export/multicloudReportData.ts`
- Create: `frontend/src/export/multicloudReportData.test.ts`
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`

**Interfaces:**
- Consumes: `ServiceDefinition[]` and `CalculationResult[]`.
- Produces: `buildMulticloudReportData(services, results): MulticloudReportData`.

- [ ] **Step 1: Install and configure the test command**

Run:

```bash
npm install --save-dev vitest
npm pkg set scripts.test="vitest run"
```

Expected: `vitest` appears in `devDependencies` and `npm test` is available.

- [ ] **Step 2: Write failing model tests**

Create test fixtures for `storage`, `azure_adls`, `aws_s3`, `bigquery`, `aws_athena`, `aws_redshift`, and one unmapped service. Assert:

```ts
expect(model.isMulticloud).toBe(true);
expect(model.providers.map((group) => group.id)).toEqual(["gcp", "azure", "aws"]);
expect(model.providers.map((group) => group.total)).toEqual([100, 80, 95]);
expect(model.comparisons.find((row) => row.functionName === "Armazenamento de objetos"))
  .toMatchObject({
    values: {
      gcp: { serviceNames: ["Cloud Storage"], total: 40 },
      azure: { serviceNames: ["ADLS"], total: 35 },
      aws: { serviceNames: ["S3"], total: 30 },
    },
  });
expect(model.comparisons.find((row) => row.functionName === "Warehouse e SQL")?.values.aws)
  .toMatchObject({ serviceNames: ["Athena", "Redshift"], total: 65 });
expect(model.comparisons.some((row) => row.functionName === "Serviço exclusivo")).toBe(true);
```

Add a second test with GCP-only results:

```ts
expect(buildMulticloudReportData(services, gcpResults).isMulticloud).toBe(false);
```

- [ ] **Step 3: Run the tests and verify RED**

Run:

```bash
npm test -- src/export/multicloudReportData.test.ts
```

Expected: FAIL because `multicloudReportData` does not exist.

- [ ] **Step 4: Implement the report model**

Define these public types:

```ts
export interface ProviderReportGroup {
  id: CloudProvider;
  label: string;
  services: { definition: ServiceDefinition; result: CalculationResult }[];
  total: number;
}

export interface ComparisonValue {
  serviceNames: string[];
  total: number;
}

export interface ComparisonRow {
  functionName: string;
  values: Partial<Record<CloudProvider, ComparisonValue>>;
}

export interface MulticloudReportData {
  isMulticloud: boolean;
  providers: ProviderReportGroup[];
  comparisons: ComparisonRow[];
}
```

Implement a fixed equivalence list matching the approved design and current agent map. Aggregate multiple services from the same provider in one function row. Append each unmatched service as an exclusive row. Derive the provider from `service.provider ?? "gcp"` and preserve `PROVIDERS` order.

- [ ] **Step 5: Run the focused tests**

Run:

```bash
npm test -- src/export/multicloudReportData.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit the model**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/export/multicloudReportData.ts frontend/src/export/multicloudReportData.test.ts
git commit -m "feat: build multicloud report data"
```

### Task 2: Render the consolidated PDF

**Files:**
- Modify: `frontend/src/export/reportPdf.ts`
- Test: `frontend/src/export/multicloudReportData.test.ts`

**Interfaces:**
- Consumes: `buildMulticloudReportData`.
- Preserves: `downloadProjectReport({ services, results, title?, disclaimer? }): void`.

- [ ] **Step 1: Add a failing completeness test**

Export `MULTICLOUD_FUNCTIONS` from the model module and assert that representative groups contain the exact current IDs:

```ts
expect(MULTICLOUD_FUNCTIONS.find((group) => group.name === "Streaming analytics")?.serviceIds)
  .toEqual(["dataflow", "azure_stream_analytics", "aws_flink", "dbx_jobs"]);
expect(MULTICLOUD_FUNCTIONS.find((group) => group.name === "Warehouse e SQL")?.serviceIds)
  .toEqual(["bigquery", "azure_synapse_sql", "aws_athena", "aws_redshift", "dbx_sql"]);
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
npm test -- src/export/multicloudReportData.test.ts
```

Expected: FAIL until the exported mapping includes the required groups.

- [ ] **Step 3: Add multicloud rendering**

At the start of `downloadProjectReport`, build the report model. If `isMulticloud` is false, keep the existing code path. Otherwise:

1. Render title `Relatório comparativo multicloud`.
2. For every provider group, render a provider heading followed by each service's existing line-item table and notes.
3. Render `Resumo consolidado por função` with columns `Função`, `Google`, `Azure`, `AWS`, `Databricks`. Each provider cell contains service names and the aggregated monthly total, or `—`.
4. Render `Totais por nuvem` with one row per populated provider.
5. Render the existing disclaimer.
6. Save as `relatorio-comparativo-multicloud.pdf`.

Use small local helpers for page breaks, service details, and consolidated tables. Do not modify `downloadCompareReport`.

- [ ] **Step 4: Run tests and TypeScript build**

Run:

```bash
npm test
npm run build
```

Expected: all tests PASS and Vite build completes.

- [ ] **Step 5: Commit the PDF renderer**

```bash
git add frontend/src/export/reportPdf.ts frontend/src/export/multicloudReportData.ts frontend/src/export/multicloudReportData.test.ts
git commit -m "feat: render consolidated multicloud PDF"
```

### Task 3: Export all populated providers from the summary

**Files:**
- Modify: `frontend/src/components/ProjectSummary.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Adds optional `reportServices?: ServiceDefinition[]` and `reportResults?: CalculationResult[]` props to `ProjectSummary`.
- Passes only enabled, non-null results from `App`.

- [ ] **Step 1: Add report inputs to `ProjectSummary`**

Select export data without changing the visible summary:

```ts
const exportServices = reportServices ?? services;
const exportResults = reportResults ?? active;
```

Pass these values to `downloadProjectReport`.

- [ ] **Step 2: Pass all enabled results from `App`**

Build:

```ts
const reportServices = services.filter((service) => enabled[service.id] && results[service.id]);
const reportResults = reportServices
  .map((service) => results[service.id])
  .filter((result): result is CalculationResult => result !== null);
```

Provide them to `ProjectSummary`. This keeps the on-screen sidebar scoped to the selected tab while making the PDF multicloud.

- [ ] **Step 3: Run all verification**

Run:

```bash
npm test
npm run build
git diff --check
```

Expected: all tests PASS, production build completes, and diff check emits no errors.

- [ ] **Step 4: Commit the integration**

```bash
git add frontend/src/App.tsx frontend/src/components/ProjectSummary.tsx
git commit -m "feat: export every populated cloud"
```
