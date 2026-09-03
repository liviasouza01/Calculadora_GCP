import { useEffect, useState } from "react";
import type { CalculationResult, ServiceDefinition, ServiceInputs } from "../types";
import { calculateService } from "../api/client";
import { ServiceForm } from "./ServiceForm/ServiceForm";
import { ResultTable } from "./Summary/ResultTable";

interface Props {
  service: ServiceDefinition;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  onResult: (result: CalculationResult | null) => void;
}

function defaultInputs(service: ServiceDefinition): ServiceInputs {
  const inputs: ServiceInputs = {};
  for (const field of service.fields) {
    inputs[field.id] = field.default ?? (field.type === "number" ? 0 : field.options?.[0]?.value ?? "");
  }
  return inputs;
}

export function ServicePanel({ service, enabled, onToggle, onResult }: Props) {
  const [inputs, setInputs] = useState<ServiceInputs>(() => defaultInputs(service));
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [showReferences, setShowReferences] = useState(false);

  useEffect(() => {
    if (!enabled) {
      onResult(null);
      return;
    }
    let cancelled = false;
    calculateService(service.id, inputs)
      .then((res) => {
        if (!cancelled) {
          setResult(res);
          onResult(res);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setResult(null);
          onResult(null);
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputs, enabled, service.id]);

  const handleFieldChange = (fieldId: string, value: number | string) => {
    setInputs((prev) => ({ ...prev, [fieldId]: value }));
  };

  return (
    <section className={`service-panel ${enabled ? "service-panel--active" : ""}`}>
      <header className="service-panel__header">
        <label className="service-panel__toggle">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onToggle(e.target.checked)}
          />
          <div>
            <h3>{service.name}</h3>
            <p>{service.description}</p>
          </div>
        </label>
      </header>

      {enabled ? (
        <div className="service-panel__body">
          <ServiceForm fields={service.fields} values={inputs} onChange={handleFieldChange} />
          {result ? <ResultTable result={result} /> : null}

          <button
            type="button"
            className="link-button"
            onClick={() => setShowReferences((v) => !v)}
          >
            {showReferences ? "Ocultar" : "Ver"} preços oficiais do Google Cloud
          </button>
          {showReferences ? (
            <ul className="pricing-references">
              {service.pricing_references.map((ref, idx) => (
                <li key={idx}>
                  <strong>{ref.label}:</strong> ${ref.unit_price} / {ref.unit}{" "}
                  <a href={ref.source_url} target="_blank" rel="noreferrer">
                    (fonte oficial)
                  </a>{" "}
                  <span className="pricing-references__date">
                    verificado em {ref.last_verified}
                  </span>
                  {ref.notes ? <div className="pricing-references__notes">{ref.notes}</div> : null}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
