import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import type { CompareScope, ServiceInputs } from "../types";
import { fillFromBriefing } from "../api/client";
import { COMPARE_SCOPES } from "../providers";
import Markdown from "react-markdown";

interface Props {
  onFilled: (
    asIs: Record<string, ServiceInputs>,
    toBe: Record<string, ServiceInputs>,
    source: CompareScope,
    target: CompareScope,
  ) => void;
}

const ACCEPT =
  ".pdf,.txt,.docx,.png,.jpg,.jpeg,application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg";

function fileNames(files: FileList | null): string[] {
  if (!files) {
    return [];
  }
  return Array.from(files).map((file) => file.name);
}

export function ComparePanel({ onFilled }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [names, setNames] = useState<string[]>([]);
  const [intent, setIntent] = useState<"compare" | "complement">("compare");
  const [source, setSource] = useState<CompareScope>("gcp");
  const [target, setTarget] = useState<CompareScope>("azure");

  function handleFilesChange(event: ChangeEvent<HTMLInputElement>) {
    setNames(fileNames(event.target.files));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const filesField = form.elements.namedItem("files");
    const notesField = form.elements.namedItem("notes");

    if (intent === "compare" && source === target && source !== "multicloud") {
      setError("Escolha outra nuvem de destino, ou Multicloud.");
      return;
    }

    const uploaded =
      filesField instanceof HTMLInputElement && filesField.files
        ? Array.from(filesField.files)
        : [];
    if (uploaded.length === 0) {
      setError("Anexe a calculadora atual (PDF, print, Word ou TXT).");
      return;
    }

    const data = new FormData();
    for (const file of uploaded) {
      data.append("files", file);
    }
    data.append("intent", intent);
    data.append("source_provider", source);
    data.append("target_provider", target);
    if (notesField instanceof HTMLTextAreaElement) {
      data.append("notes", notesField.value);
    }

    setBusy(true);
    setError(null);
    setSummary(null);
    try {
      const result = await fillFromBriefing(data);
      setSummary(result.summary);
      onFilled(result.filled_as_is ?? {}, result.filled_to_be ?? result.filled_services, source, target);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao comparar a calculadora.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="briefing-panel">
      <div className="section-heading">
        <span className="section-heading__step">1</span>
        <div>
          <h2>Calculadora atual</h2>
        </div>
      </div>
      <form className="briefing-panel__form" onSubmit={handleSubmit}>
        <label className={`dropzone ${names.length ? "dropzone--filled" : ""}`}>
          <input name="files" type="file" multiple accept={ACCEPT} required onChange={handleFilesChange} />
          <strong>Arquivos</strong>
          <span>PDF, print (PNG/JPG), Word ou TXT da calculadora que o cliente já enviou.</span>
          {names.length > 0 ? (
            <ul>
              {names.map((name, index) => (
                <li key={`${name}-${index}`}>{name}</li>
              ))}
            </ul>
          ) : (
            <em>Obrigatório</em>
          )}
        </label>
        <div className="compare-fields">
          <label className="briefing-panel__field">
            <span>Objetivo</span>
            <select
              value={intent}
              onChange={(event) => setIntent(event.target.value as "compare" | "complement")}
            >
              <option value="compare">Comparar com outra nuvem</option>
              <option value="complement">Complementar a estrutura atual</option>
            </select>
          </label>
          <label className="briefing-panel__field">
            <span>Nuvem da calculadora enviada</span>
            <select value={source} onChange={(event) => setSource(event.target.value as CompareScope)}>
              {COMPARE_SCOPES.map((scope) => (
                <option key={scope.id} value={scope.id}>
                  {scope.label}
                </option>
              ))}
            </select>
          </label>
          <label className="briefing-panel__field">
            <span>Solução proposta</span>
            <select value={target} onChange={(event) => setTarget(event.target.value as CompareScope)}>
              {COMPARE_SCOPES.map((scope) => (
                <option key={scope.id} value={scope.id}>
                  {scope.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label className="briefing-panel__field">
          <span>Notas extras</span>
          <textarea
            name="notes"
            rows={3}
            placeholder="Ex.: cliente já tem Databricks + S3; manter Databricks; warehouse no BigQuery; incluir ML."
          />
        </label>
        <button type="submit" className="briefing-panel__submit" disabled={busy}>
          {busy ? "Lendo a calculadora..." : intent === "compare" ? "Gerar comparação" : "Complementar estrutura"}
        </button>
      </form>
      {error ? <p className="briefing-panel__error">{error}</p> : null}
      {summary ? (
        <div className="briefing-panel__summary">
          <Markdown components={{ a: ({ children }) => <span>{children}</span> }}>{summary}</Markdown>
        </div>
      ) : null}
    </section>
  );
}
