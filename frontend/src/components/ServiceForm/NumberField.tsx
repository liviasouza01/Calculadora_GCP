import type { FieldSchema } from "../../types";

interface Props {
  field: FieldSchema;
  value: number | string;
  onChange: (value: number) => void;
}

export function NumberField({ field, value, onChange }: Props) {
  return (
    <label className="field">
      <span className="field__label">
        {field.label}
        {field.unit ? <span className="field__unit"> ({field.unit})</span> : null}
      </span>
      <input
        type="number"
        min={field.min ?? 0}
        step={field.step ?? "any"}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      {field.help ? <span className="field__help">{field.help}</span> : null}
    </label>
  );
}
