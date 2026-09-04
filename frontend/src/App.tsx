import { useEffect, useState } from "react";
import type { CalculationResult, ServiceDefinition, ServiceInputs } from "./types";
import { fetchServices } from "./api/client";
import { BriefingPanel } from "./components/BriefingPanel";
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
  const [presets, setPresets] = useState<Record<string, ServiceInputs>>({});
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
          <h1>Calculadora de custos GCP</h1>
          <p>
            Estime o custo mensal de um projeto de dados. Envie um briefing ou
            preencha os serviços manualmente.
          </p>
        </div>
      </header>

      <div className="app__content">
        <main className="app__services">
          <BriefingPanel
            onFilled={(filled) => {
              setPresets((prev) => ({ ...prev, ...filled }));
              setEnabled((prev) => {
                const next = { ...prev };
                for (const serviceId of Object.keys(filled)) {
                  next[serviceId] = true;
                }
                return next;
              });
            }}
          />
          <div className="section-heading">
            <span className="section-heading__step">2</span>
            <div>
              <h2>Serviços</h2>
              <p>Ative só o que entra no projeto e ajuste os volumes.</p>
            </div>
          </div>
          {Array.from(grouped.entries()).map(([category, categoryServices]) => (
            <div key={category} className="category-group">
              <h2 className="category-group__title">{category}</h2>
              {categoryServices.map((service) => (
                <ServicePanel
                  key={service.id}
                  service={service}
                  enabled={Boolean(enabled[service.id])}
                  presetInputs={presets[service.id]}
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

        <ProjectSummary services={services} results={results} />
      </div>
    </div>
  );
}
