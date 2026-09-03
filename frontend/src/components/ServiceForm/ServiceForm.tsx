import type { FieldSchema, ServiceInputs } from "../../types";
import { NumberField } from "./NumberField";
import { SelectField } from "./SelectField";

interface Props {
  fields: FieldSchema[];
  values: ServiceInputs;
  onChange: (fieldId: string, value: number | string) => void;
}

/**
 * Renders any service's input form purely from its FieldSchema[] — this is
 * the piece that makes adding a new GCP service a backend-only change.
 */
export function ServiceForm({ fields, values, onChange }: Props) {
  return (
    <div className="service-form">
      {fields.map((field) => {
        const value = values[field.id] ?? field.default ?? (field.type === "number" ? 0 : "");
        if (field.type === "select") {
          return (
            <SelectField
              key={field.id}
              field={field}
              value={String(value)}
              onChange={(v) => onChange(field.id, v)}
            />
          );
        }
        return (
          <NumberField
            key={field.id}
            field={field}
            value={value as number | string}
            onChange={(v) => onChange(field.id, v)}
          />
        );
      })}
    </div>
  );
}
