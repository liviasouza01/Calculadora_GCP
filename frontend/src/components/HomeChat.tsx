import { useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import Markdown from "react-markdown";
import type { CloudProvider, ServiceInputs } from "../types";
import { fillFromBriefing } from "../api/client";
import { APP_TITLE, PROVIDERS } from "../providers";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  files?: string[];
  image?: string | null;
}

interface Props {
  messages: ChatMessage[];
  busy: boolean;
  error: string | null;
  filledProviders: CloudProvider[];
  onOpenTab: (tab: CloudProvider) => void;
  onComplete: (filled: Record<string, ServiceInputs>, image: string | null) => void;
  onMessages: (messages: ChatMessage[]) => void;
  onBusy: (busy: boolean) => void;
  onError: (error: string | null) => void;
}

const ACCEPT =
  ".pdf,.txt,.csv,.xlsx,.xls,.docx,.png,.jpg,.jpeg,application/pdf,text/plain,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg";

function imageSrc(raw: string): string {
  return raw.startsWith("data:") ? raw : `data:image/png;base64,${raw}`;
}

export function HomeChat({
  messages,
  busy,
  error,
  filledProviders,
  onOpenTab,
  onComplete,
  onMessages,
  onBusy,
  onError,
}: Props) {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [wantArchitecture, setWantArchitecture] = useState(true);
  const fileRef = useRef<HTMLInputElement>(null);

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const notes = text.trim();
    if (!notes && files.length === 0) {
      onError("Escreva o briefing ou anexe arquivos.");
      return;
    }

    const userMessage: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      text: notes || "Arquivos anexados",
      files: files.map((file) => file.name),
    };
    onMessages([...messages, userMessage]);
    onBusy(true);
    onError(null);

    const data = new FormData();
    for (const file of files) {
      data.append("files", file);
    }
    data.append("notes", notes);
    data.append("intent", "context");
    data.append("source_provider", "multicloud");
    data.append("target_provider", "multicloud");
    data.append("want_architecture", wantArchitecture ? "true" : "false");

    try {
      const result = await fillFromBriefing(data);
      const image = result.architecture_image ?? null;
      onMessages([
        ...messages,
        userMessage,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          text: result.summary,
          image,
        },
      ]);
      onComplete(result.filled_to_be ?? result.filled_services, image);
      setText("");
      setFiles([]);
      if (fileRef.current) {
        fileRef.current.value = "";
      }
    } catch (err) {
      onError(err instanceof Error ? err.message : "Falha ao gerar a proposta.");
    } finally {
      onBusy(false);
    }
  }

  const empty = messages.length === 0;

  return (
    <div className={`home-chat ${empty ? "home-chat--empty" : ""}`}>
      {empty ? (
        <div className="home-chat__hero">
          <p className="home-chat__hello">Olá</p>
          <h2>{APP_TITLE}</h2>
          <p className="home-chat__sub">Descreva o projeto, anexe arquivos e gere a arquitetura. A calculadora preenche as abas para você baixar o relatório.</p>
        </div>
      ) : (
        <div className="home-chat__thread">
          {messages.map((message) => (
            <article
              key={message.id}
              className={
                message.role === "user" ? "home-chat__bubble home-chat__bubble--user" : "home-chat__bubble"
              }
            >
              {message.role === "assistant" ? (
                <Markdown components={{ a: ({ children }) => <span>{children}</span> }}>{message.text}</Markdown>
              ) : (
                <p>{message.text}</p>
              )}
              {message.files && message.files.length > 0 ? (
                <ul className="home-chat__files">
                  {message.files.map((name) => (
                    <li key={name}>{name}</li>
                  ))}
                </ul>
              ) : null}
              {message.image ? (
                <img className="home-chat__arch" src={imageSrc(message.image)} alt="Arquitetura proposta" />
              ) : null}
            </article>
          ))}
          {busy ? <p className="home-chat__busy">Pensando...</p> : null}
          {filledProviders.length > 0 ? (
            <div className="home-chat__tabs">
              {PROVIDERS.filter((provider) => filledProviders.includes(provider.id)).map((provider) => (
                <button key={provider.id} type="button" onClick={() => onOpenTab(provider.id)}>
                  Abrir {provider.label}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      )}

      <form className="home-composer" onSubmit={handleSubmit}>
        {files.length > 0 ? (
          <ul className="home-composer__chips">
            {files.map((file) => (
              <li key={`${file.name}-${file.size}`}>
                {file.name}
                <button
                  type="button"
                  aria-label={`Remover ${file.name}`}
                  onClick={() => setFiles((prev) => prev.filter((item) => item !== file))}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        <textarea
          rows={2}
          value={text}
          disabled={busy}
          placeholder="Pergunte sobre o projeto, volumes, nuvem..."
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="home-composer__bar">
          <input
            ref={fileRef}
            type="file"
            multiple
            accept={ACCEPT}
            hidden
            onChange={(event) => {
              const next = event.target.files ? Array.from(event.target.files) : [];
              setFiles((prev) => [...prev, ...next]);
            }}
          />
          <button type="button" className="home-composer__icon" onClick={() => fileRef.current?.click()} disabled={busy}>
            +
          </button>
          <button
            type="button"
            className={wantArchitecture ? "home-composer__tool home-composer__tool--on" : "home-composer__tool"}
            onClick={() => setWantArchitecture((value) => !value)}
            title="Ligado: gera o diagrama da arquitetura. Desligado: só preenche a calculadora."
          >
            Gerar diagrama
          </button>
          <span className="home-composer__grow" />
          <button type="submit" className="home-composer__send" disabled={busy}>
            ↑
          </button>
        </div>
      </form>
      {error ? <p className="home-chat__error">{error}</p> : null}
    </div>
  );
}
