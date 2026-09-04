import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import type { ServiceInputs } from "../types";
import { fillFromBriefing } from "../api/client";
import Markdown from "react-markdown";

interface Props {
  onFilled: (filled: Record<string, ServiceInputs>, summary: string) => void;
}

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
  const [conversationNames, setConversationNames] = useState<string[]>([]);
  const [architectureNames, setArchitectureNames] = useState<string[]>([]);

  function handleConversationChange(event: ChangeEvent<HTMLInputElement>) {
    setConversationNames(fileNames(event.target.files));
  }

  function handleArchitectureChange(event: ChangeEvent<HTMLInputElement>) {
    setArchitectureNames(fileNames(event.target.files));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const conversations = form.elements.namedItem("conversations");
    const architectures = form.elements.namedItem("architectures");
    const notesField = form.elements.namedItem("notes");

    const conversationFiles =
      conversations instanceof HTMLInputElement && conversations.files
        ? Array.from(conversations.files)
        : [];
    if (conversationFiles.length === 0) {
      setError("Anexe ao menos uma transcrição (PDF, TXT ou Word).");
      return;
    }

    const data = new FormData();
    for (const file of conversationFiles) {
      data.append("conversations", file);
    }
    if (architectures instanceof HTMLInputElement && architectures.files) {
      for (const file of Array.from(architectures.files)) {
        data.append("architectures", file);
      }
    }
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
      setError(err instanceof Error ? err.message : "Falha ao interpretar o briefing.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="briefing-panel">
      <div className="section-heading">
        <span className="section-heading__step">1</span>
        <div>
          <h2>Briefing</h2>
          <p>O agente lê os anexos e sugere quais serviços entram na calculadora.</p>
        </div>
      </div>
      <form className="briefing-panel__form" onSubmit={handleSubmit}>
        <div className="dropzone-row">
          <label className={`dropzone ${conversationNames.length ? "dropzone--filled" : ""}`}>
            <input
              name="conversations"
              type="file"
              multiple
              accept=".pdf,.txt,.docx,application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              required
              onChange={handleConversationChange}
            />
            <strong>Transcrições</strong>
            <span>PDF, TXT ou Word. Clique ou arraste vários arquivos.</span>
            {conversationNames.length > 0 ? (
              <ul>
                {conversationNames.map((name, index) => (
                  <li key={`${name}-${index}`}>{name}</li>
                ))}
              </ul>
            ) : (
              <em>Obrigatório</em>
            )}
          </label>
          <label className={`dropzone ${architectureNames.length ? "dropzone--filled" : ""}`}>
            <input
              name="architectures"
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,image/png,image/jpeg"
              onChange={handleArchitectureChange}
            />
            <strong>Arquitetura</strong>
            <span>PNG ou JPG dos desenhos. Opcional.</span>
            {architectureNames.length > 0 ? (
              <ul>
                {architectureNames.map((name, index) => (
                  <li key={`${name}-${index}`}>{name}</li>
                ))}
              </ul>
            ) : (
              <em>Opcional</em>
            )}
          </label>
        </div>
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
