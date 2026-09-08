import type { CalculationResult, ServiceDefinition } from "../types";
import { downloadCompareReport } from "../export/reportPdf";
import { money, signedMoney } from "../format";

interface Props {
  services: ServiceDefinition[];
  asIs: CalculationResult[];
  toBe: CalculationResult[];
  asIsLabel: string;
  toBeLabel: string;
  disclaimer: string;
}

function list(names: Map<string, string>, results: CalculationResult[]) {
  if (results.length === 0) {
    return <p className="project-summary__empty">Nenhum item neste cenário.</p>;
  }
  return (
    <ul>
      {results.map((result) => (
        <li key={result.service_id}>
          <span>{names.get(result.service_id) ?? result.service_id}</span>
          <span>{money.format(result.total)}</span>
        </li>
      ))}
    </ul>
  );
}

export function CompareSummary({
  services,
  asIs,
  toBe,
  asIsLabel,
  toBeLabel,
  disclaimer,
}: Props) {
  const names = new Map(services.map((service) => [service.id, service.name]));
  const asIsTotal = asIs.reduce((sum, result) => sum + result.total, 0);
  const toBeTotal = toBe.reduce((sum, result) => sum + result.total, 0);
  const delta = toBeTotal - asIsTotal;
  const deltaClass =
    delta > 0.005 ? "compare-delta compare-delta--up" : delta < -0.005 ? "compare-delta compare-delta--down" : "compare-delta";
  const deltaText =
    delta > 0.005
      ? `TO-BE é ${signedMoney(delta)} mais caro / mês`
      : delta < -0.005
        ? `TO-BE é ${signedMoney(delta)} mais barato / mês`
        : "TO-BE tem o mesmo custo mensal do AS IS";

  return (
    <aside className="project-summary">
      <div className="section-heading section-heading--compact">
        <span className="section-heading__step">3</span>
        <div>
          <h2>AS IS vs TO-BE</h2>
          <p>Diferença explícita de preço</p>
        </div>
      </div>
      <div className="compare-totals">
        <div>
          <span>AS IS · {asIsLabel}</span>
          <strong>{money.format(asIsTotal)}</strong>
        </div>
        <div>
          <span>TO-BE · {toBeLabel}</span>
          <strong>{money.format(toBeTotal)}</strong>
        </div>
      </div>
      <p className={deltaClass}>{deltaText}</p>
      <h3 className="compare-block-title">AS IS</h3>
      {list(names, asIs)}
      <h3 className="compare-block-title">TO-BE</h3>
      {list(names, toBe)}
      <button
        type="button"
        className="project-summary__export"
        disabled={asIs.length === 0 && toBe.length === 0}
        onClick={() =>
          downloadCompareReport({
            services,
            asIs,
            toBe,
            asIsLabel,
            toBeLabel,
            disclaimer,
          })
        }
      >
        Exportar relatório AS IS vs TO-BE
      </button>
      <p className="project-summary__disclaimer">{disclaimer}</p>
    </aside>
  );
}
