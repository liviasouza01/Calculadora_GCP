import type { CalculationResult, ServiceDefinition } from "../types";
import { downloadProjectReport } from "../export/reportPdf";
import { money } from "../format";

interface Props {
  services: ServiceDefinition[];
  results: Record<string, CalculationResult | null>;
  disclaimer: string;
  pdfTitle: string;
  stepLabel: string;
}

export function ProjectSummary({ services, results, disclaimer, pdfTitle, stepLabel }: Props) {
  const names = new Map(services.map((service) => [service.id, service.name]));
  const active = Object.values(results).filter(
    (result): result is CalculationResult => result !== null,
  );
  const grandTotal = active.reduce((sum, result) => sum + result.total, 0);

  return (
    <aside className="project-summary">
      <div className="section-heading section-heading--compact">
        <span className="section-heading__step">{stepLabel}</span>
        <div>
          <h2>Resumo</h2>
          <p>Total mensal estimado</p>
        </div>
      </div>
      {active.length === 0 ? (
        <p className="project-summary__empty">
          Marque os serviços à esquerda ou envie o contexto para ver o total.
        </p>
      ) : (
        <ul>
          {active.map((result) => (
            <li key={result.service_id}>
              <span>{names.get(result.service_id) ?? result.service_id}</span>
              <span>{money.format(result.total)}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="project-summary__total">
        <span>Total / mês</span>
        <strong>{money.format(grandTotal)}</strong>
      </div>
      <button
        type="button"
        className="project-summary__export"
        disabled={active.length === 0}
        onClick={() =>
          downloadProjectReport({
            services,
            results: active,
            title: pdfTitle,
            disclaimer,
          })
        }
      >
        Exportar relatório em PDF
      </button>
      <p className="project-summary__disclaimer">
        {disclaimer}
      </p>
    </aside>
  );
}
