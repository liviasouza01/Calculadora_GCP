import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import type { ServiceInputs } from "../types";
import { fillFromBriefing } from "../api/client";
import Markdown from "react-markdown";

interface Props {
  onFilled: (filled: Record<string, ServiceInputs>, summary: string) => void;
}

const ACCEPT =
  ".pdf,.txt,.csv,.xlsx,.xls,.docx,.png,.jpg,.jpeg,application/pdf,text/plain,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg";

function fileNames(files: FileList | null): string[] {
  if (!files) {
    return [];
  }
  return Array.from(files).map((file) => file.name);
}

export function BriefingPanel({ onFilled }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [names, setNames] = useState<string[]>([]);

  function handleFilesChange(event: ChangeEvent<HTMLInputElement>) {
    setNames(fileNames(event.target.files));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const filesField = form.elements.namedItem("files");
    const notesField = form.elements.namedItem("notes");

    const uploaded =
      filesField instanceof HTMLInputElement && filesField.files
        ? Array.from(filesField.files)
        : [];
    if (uploaded.length === 0) {
      setError("Anexe ao menos um arquivo (PDF, TXT, CSV, Excel, Word, PNG ou JPG).");
      return;
    }

    const data = new FormData();
    for (const file of uploaded) {
      data.append("files", file);
    }
    data.append("intent", "context");
    data.append("source_provider", "gcp");
    data.append("target_provider", "gcp");
    if (notesField instanceof HTMLTextAreaElement) {
      data.append("notes", notesField.value);
    }

    setBusy(true);
    setError(null);
    setSummary(null);
    try {
      const result = await fillFromBriefing(data);
      setSummary(result.summary);
      onFilled(result.filled_services, result.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao interpretar o contexto.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="briefing-panel">
      <div className="section-heading">
        <span className="section-heading__step">1</span>
        <div>
          <h2>Contexto</h2>
        </div>
      </div>
      <form className="briefing-panel__form" onSubmit={handleSubmit}>
        <label className={`dropzone ${names.length ? "dropzone--filled" : ""}`}>
          <input
            name="files"
            type="file"
            multiple
            accept={ACCEPT}
            required
            onChange={handleFilesChange}
          />
          <strong>Arquivos</strong>
          <span>PDF, TXT, CSV, Excel, Word, PNG ou JPG. Clique ou arraste vários arquivos.</span>
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
        <label className="briefing-panel__field">
          <span>Notas extras</span>
          <textarea name="notes" rows={2} placeholder="Região, volumes, premissas que não estão nos anexos..." />
        </label>
        <button type="submit" className="briefing-panel__submit" disabled={busy}>
          {busy ? "Lendo anexos..." : "Preencher calculadora"}
        </button>
      </form>
      {error ? <p className="briefing-panel__error">{error}</p> : null}
      {summary ? (
        <div className="briefing-panel__summary">
          <Markdown>{summary}</Markdown>
        </div>
      ) : null}
    </section>
  );
}
