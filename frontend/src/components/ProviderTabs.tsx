import type { AppTab } from "../types";
import { APP_TABS } from "../providers";

interface Props {
  value: AppTab;
  onChange: (tab: AppTab) => void;
}

export function ProviderTabs({ value, onChange }: Props) {
  return (
    <div className="provider-tabs" role="tablist" aria-label="Provedor de nuvem">
      {APP_TABS.map((tab) => {
        const selected = tab.id === value;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={selected}
            className={selected ? "provider-tabs__tab provider-tabs__tab--active" : "provider-tabs__tab"}
            onClick={() => onChange(tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
