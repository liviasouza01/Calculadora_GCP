import type { CalculationResult } from "../types";

interface Props {
  results: Record<string, CalculationResult | null>;
}

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

export function ProjectSummary({ results }: Props) {
  const active = Object.values(results).filter(
    (r): r is CalculationResult => r !== null,
  );
  const grandTotal = active.reduce((sum, r) => sum + r.total, 0);

  return (
    <aside className="project-summary">
      <h2>Resumo do projeto</h2>
      {active.length === 0 ? (
        <p>Selecione ao menos um componente para estimar o custo do projeto.</p>
      ) : (
        <ul>
          {active.map((r) => (
            <li key={r.service_id}>
              <span>{r.service_id}</span>
              <span>{currencyFormatter.format(r.total)}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="project-summary__total">
        <span>Total mensal estimado</span>
        <strong>{currencyFormatter.format(grandTotal)}</strong>
      </div>
      <p className="project-summary__disclaimer">
        Estimativa baseada em preços públicos do Google Cloud (região US),
        sem descontos por compromisso de uso, sem impostos. Valores reais podem
        variar por região, negociação comercial e uso real.
      </p>
    </aside>
  );
}
