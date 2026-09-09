import { useEffect, useState } from "react";
import type {
  AppTab,
  CalculationResult,
  CloudProvider,
  CompareScope,
  ServiceDefinition,
  ServiceInputs,
} from "./types";
import { fetchServices, createShare, fetchShare } from "./api/client";
import { ComparePanel } from "./components/ComparePanel";
import { CompareSummary } from "./components/CompareSummary";
import { HomeChat } from "./components/HomeChat";
import type { ChatMessage } from "./components/HomeChat";
import { ProviderTabs } from "./components/ProviderTabs";
import { ServicePanel } from "./components/ServicePanel";
import { ProjectSummary } from "./components/ProjectSummary";
import { APP_TITLE, CLIENT_TABS, COMPARE_SCOPES, PROVIDER_COPY, PROVIDERS } from "./providers";
import type { AppFlags } from "./flags";
import { currentShareId, magicLink } from "./shareUrl";
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

function groupByCloudAndCategory(services: ServiceDefinition[]) {
  const groups = new Map<string, ServiceDefinition[]>();
  for (const service of services) {
    const key = `${labelOf(serviceProvider(service))} · ${service.category}`;
    const list = groups.get(key) ?? [];
    list.push(service);
    groups.set(key, list);
  }
  return groups;
}

function serviceProvider(service: ServiceDefinition): CloudProvider {
  return service.provider ?? "gcp";
}

function isCloudTab(tab: AppTab): tab is CloudProvider {
  return tab !== "compare" && tab !== "home";
}

function labelOf(scope: CompareScope): string {
  return COMPARE_SCOPES.find((item) => item.id === scope)?.label ?? scope;
}

function enabledMap(filled: Record<string, ServiceInputs>): Record<string, boolean> {
  return Object.fromEntries(Object.keys(filled).map((id) => [id, true]));
}

export default function App({ flags }: { flags: AppFlags }) {
  const [services, setServices] = useState<ServiceDefinition[] | null>(null);
  const [tab, setTab] = useState<AppTab>("home");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [architectureImage, setArchitectureImage] = useState<string | null>(null);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [presets, setPresets] = useState<Record<string, ServiceInputs>>({});
  const [results, setResults] = useState<Record<string, CalculationResult | null>>({});
  const [asIsInputs, setAsIsInputs] = useState<Record<string, ServiceInputs>>({});
  const [toBeInputs, setToBeInputs] = useState<Record<string, ServiceInputs>>({});
  const [asIsResults, setAsIsResults] = useState<Record<string, CalculationResult | null>>({});
  const [toBeResults, setToBeResults] = useState<Record<string, CalculationResult | null>>({});
  const [compareSource, setCompareSource] = useState<CompareScope>("gcp");
  const [compareTarget, setCompareTarget] = useState<CompareScope | null>(null);
  const [asIsEnabled, setAsIsEnabled] = useState<Record<string, boolean>>({});
  const [toBeEnabled, setToBeEnabled] = useState<Record<string, boolean>>({});
  const [sessionKey, setSessionKey] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [shareBusy, setShareBusy] = useState(false);
  const shareId = currentShareId();
  const clientView = Boolean(shareId) || flags.clientCalculatorOnly;

  useEffect(() => {
    fetchServices()
      .then(setServices)
      .catch(() => setError("Não foi possível conectar à API. Verifique se o backend está rodando."));
  }, []);

  useEffect(() => {
    if (!shareId || !services) {
      return;
    }
    let cancelled = false;
    fetchShare(shareId)
      .then((share) => {
        if (cancelled) {
          return;
        }
        setEnabled(share.enabled);
        setPresets(share.presets);
        setResults({});
        const match = services.find((service) => share.enabled[service.id]);
        setTab(match ? serviceProvider(match) : "gcp");
      })
      .catch(() => {
        if (!cancelled) {
          setError("Este link mágico não é válido ou expirou.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [shareId, services]);

  function applyProposal(filled: Record<string, ServiceInputs>, image: string | null) {
    setPresets(filled);
    setEnabled(enabledMap(filled));
    setResults({});
    setArchitectureImage(image);
  }

  function clearSession() {
    setChatMessages([]);
    setChatBusy(false);
    setChatError(null);
    setArchitectureImage(null);
    setEnabled({});
    setPresets({});
    setResults({});
    setAsIsInputs({});
    setToBeInputs({});
    setAsIsResults({});
    setToBeResults({});
    setAsIsEnabled({});
    setToBeEnabled({});
    setCompareSource("gcp");
    setCompareTarget(null);
    setSessionKey((value) => value + 1);
    setTab("home");
  }

  async function shareWithClient() {
    setShareBusy(true);
    setShareUrl(null);
    try {
      const created = await createShare({ enabled, presets });
      const url = magicLink(created.id);
      await navigator.clipboard.writeText(url);
      setShareUrl(url);
    } catch (err) {
      setShareUrl(err instanceof Error ? err.message : "Não foi possível gerar o link.");
    } finally {
      setShareBusy(false);
    }
  }

  if (error) {
    return <div className="app-error">{error}</div>;
  }

  if (!services) {
    return <div className="app-loading">Carregando componentes...</div>;
  }

  const compareMode = !clientView && tab === "compare";
  const homeMode = !clientView && tab === "home";
  const provider: CloudProvider = isCloudTab(tab) ? tab : "gcp";
  const copy = PROVIDER_COPY[provider];
  const visible = compareMode
    ? []
    : services.filter((service) => {
        if (serviceProvider(service) !== provider) {
          return false;
        }
        if (clientView) {
          return Boolean(enabled[service.id] || presets[service.id]);
        }
        return true;
      });
  const grouped = groupByCategory(visible);
  const visibleIds = new Set(visible.map((service) => service.id));
  const visibleResults = Object.fromEntries(
    Object.entries(results).filter(([serviceId]) => visibleIds.has(serviceId)),
  );

  const asIsServices = services.filter((service) => asIsInputs[service.id]);
  const toBeServices = services.filter((service) => toBeInputs[service.id]);
  const asIsActive = Object.values(asIsResults).filter(
    (result): result is CalculationResult => result !== null,
  );
  const toBeActive = Object.values(toBeResults).filter(
    (result): result is CalculationResult => result !== null,
  );
  const hasCompare = compareTarget !== null && (asIsServices.length > 0 || toBeServices.length > 0);
  const filledProviders = PROVIDERS.map((item) => item.id).filter((id) =>
    services.some((service) => Boolean(enabled[service.id]) && serviceProvider(service) === id),
  );
  const hasCalculator = Object.values(enabled).some(Boolean);
  const canShare = flags.shareCalculator && hasCalculator && !clientView;
  const clientTabs = CLIENT_TABS.filter((item) =>
    filledProviders.includes(item.id as CloudProvider),
  );

  function renderGroup(title: string, list: ServiceDefinition[], scenario: "as_is" | "to_be") {
    if (list.length === 0) {
      return null;
    }
    const groupedScenario = groupByCloudAndCategory(list);
    return (
      <>
        <div className="section-heading">
          <span className="section-heading__step">{scenario === "as_is" ? "2" : "2"}</span>
          <div>
            <h2>{title}</h2>
            <p>
              {scenario === "as_is"
                ? "O que existe hoje. Desmarque o que não entra no AS IS."
                : "Proposta da IA. Desmarque o que não entra no TO-BE."}
            </p>
          </div>
        </div>
        {Array.from(groupedScenario.entries()).map(([category, categoryServices]) => (
          <div key={`${scenario}-${category}`} className="category-group">
            <h2 className="category-group__title">{category}</h2>
            {categoryServices.map((service) => (
              <ServicePanel
                key={`${scenario}-${service.id}`}
                service={service}
                enabled={
                  scenario === "as_is"
                    ? asIsEnabled[service.id] !== false
                    : toBeEnabled[service.id] !== false
                }
                presetInputs={scenario === "as_is" ? asIsInputs[service.id] : toBeInputs[service.id]}
                onToggle={(value) => {
                  if (scenario === "as_is") {
                    setAsIsEnabled((prev) => ({ ...prev, [service.id]: value }));
                  } else {
                    setToBeEnabled((prev) => ({ ...prev, [service.id]: value }));
                  }
                }}
                onResult={(result) => {
                  if (scenario === "as_is") {
                    setAsIsResults((prev) => ({ ...prev, [service.id]: result }));
                  } else {
                    setToBeResults((prev) => ({ ...prev, [service.id]: result }));
                  }
                }}
              />
            ))}
          </div>
        ))}
      </>
    );
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-inner">
          {homeMode && !clientView ? null : <h1>{APP_TITLE}</h1>}
          <div className="app__header-row">
            <ProviderTabs
              value={isCloudTab(tab) ? tab : clientView ? (clientTabs[0]?.id ?? "gcp") : tab}
              onChange={setTab}
              tabs={clientView ? clientTabs : undefined}
            />
            <div className="app__header-actions">
              {canShare ? (
                <button type="button" className="app__clear" onClick={() => void shareWithClient()} disabled={shareBusy}>
                  {shareBusy ? "Gerando link..." : "Link mágico"}
                </button>
              ) : null}
              {clientView ? null : (
                <button type="button" className="app__clear" onClick={clearSession}>
                  Limpar
                </button>
              )}
            </div>
          </div>
          {shareUrl && !clientView ? <p className="app__share-url">{shareUrl}</p> : null}
        </div>
      </header>

      <div className={homeMode ? "app__home-wrap" : "app__content"}>
        {homeMode ? (
          <HomeChat
            key={sessionKey}
            messages={chatMessages}
            busy={chatBusy}
            error={chatError}
            filledProviders={filledProviders}
            onOpenTab={setTab}
            onMessages={setChatMessages}
            onBusy={setChatBusy}
            onError={setChatError}
            onComplete={(filled, image) => applyProposal(filled, image)}
          />
        ) : (
          <>
        <main className="app__services">
          <div hidden={!compareMode}>
            <ComparePanel
              key={sessionKey}
              onFilled={(asIs, toBe, source, target) => {
                setCompareSource(source);
                setCompareTarget(target);
                setAsIsInputs(asIs);
                setToBeInputs(toBe);
                setAsIsEnabled(enabledMap(asIs));
                setToBeEnabled(enabledMap(toBe));
                setAsIsResults({});
                setToBeResults({});
              }}
            />
          </div>
          {compareMode && compareTarget && !hasCompare ? (
            <p className="provider-empty">
              Nenhum item AS IS ou TO-BE foi preenchido. Confira a nuvem da calculadora enviada.
            </p>
          ) : null}
          {compareMode && hasCompare ? (
            <>
              {renderGroup(`AS IS · ${labelOf(compareSource)}`, asIsServices, "as_is")}
              {renderGroup(`TO-BE · ${labelOf(compareTarget)}`, toBeServices, "to_be")}
            </>
          ) : null}
          {isCloudTab(tab) ? (
            <>
              {architectureImage && !clientView ? (
                <img
                  className="architecture-preview"
                  src={
                    architectureImage.startsWith("data:")
                      ? architectureImage
                      : `data:image/png;base64,${architectureImage}`
                  }
                  alt="Arquitetura proposta"
                />
              ) : null}
              <div className="section-heading">
                <span className="section-heading__step">1</span>
                <div>
                  <h2>Serviços</h2>
                  <p>Ative só o que entra no projeto e ajuste os volumes.</p>
                </div>
              </div>
              {visible.length === 0 ? (
                <p className="provider-empty">{copy.empty}</p>
              ) : (
                Array.from(grouped.entries()).map(([category, categoryServices]) => (
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
                ))
              )}
            </>
          ) : null}
        </main>

        {compareMode ? (
          <CompareSummary
            services={services}
            asIs={asIsActive}
            toBe={toBeActive}
            asIsLabel={labelOf(compareSource)}
            toBeLabel={labelOf(compareTarget ?? compareSource)}
            disclaimer="Preços de lista, sem desconto e sem impostos. AS IS é a calculadora atual; TO-BE é a proposta."
          />
        ) : (
          <ProjectSummary
            services={visible}
            results={visibleResults}
            disclaimer={copy.disclaimer}
            pdfTitle={copy.pdfTitle}
            stepLabel="2"
          />
        )}
          </>
        )}
      </div>
    </div>
  );
}
