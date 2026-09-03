import { useEffect, useState } from "react";
import type { CalculationResult, ServiceDefinition } from "./types";
import { fetchServices } from "./api/client";
import { ServicePanel } from "./components/ServicePanel";
import { ProjectSummary } from "./components/ProjectSummary";
import "./App.css";

function groupByCategory(services: ServiceDefinition[]) {
  const groups = new Map<string, ServiceDefinition[]>();
  for (const service of services) {
    const list = groups.get(service.category) ?? [];
    list.push(service);
    groups.set(service.category, list);
  }
  return groups;
}

export default function App() {
  const [services, setServices] = useState<ServiceDefinition[] | null>(null);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, CalculationResult | null>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchServices()
      .then(setServices)
      .catch(() => setError("Não foi possível conectar à API. Verifique se o backend está rodando."));
  }, []);

  if (error) {
    return <div className="app-error">{error}</div>;
  }

  if (!services) {
    return <div className="app-loading">Carregando componentes do Google Cloud...</div>;
  }

  const grouped = groupByCategory(services);

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-inner">
          <span className="app__eyebrow">Google Cloud · Dados</span>
          <h1>Calculadora de Custos — Projetos de Dados no GCP</h1>
          <p>
            Estime o custo de infraestrutura de dados no Google Cloud combinando
            Storage, BigQuery (on-demand ou Enterprise), Looker, Datastream, Pub/Sub, Dataflow,
            Composer e serviços de transferência de dados, com base em preços
            oficiais publicados pelo Google.
          </p>
        </div>
      </header>

      <div className="app__content">
        <main className="app__services">
          {Array.from(grouped.entries()).map(([category, categoryServices]) => (
            <div key={category} className="category-group">
              <h2 className="category-group__title">{category}</h2>
              {categoryServices.map((service) => (
                <ServicePanel
                  key={service.id}
                  service={service}
                  enabled={Boolean(enabled[service.id])}
                  onToggle={(value) =>
                    setEnabled((prev) => ({ ...prev, [service.id]: value }))
                  }
                  onResult={(result) =>
                    setResults((prev) => ({ ...prev, [service.id]: result }))
                  }
                />
              ))}
            </div>
          ))}
        </main>

        <ProjectSummary results={results} />
      </div>
    </div>
  );
}
