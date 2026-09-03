import type { FieldSchema } from "../../types";

interface Props {
  field: FieldSchema;
  value: string;
  onChange: (value: string) => void;
}

export function SelectField({ field, value, onChange }: Props) {
  return (
    <label className="field">
      <span className="field__label">{field.label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {field.options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {field.help ? <span className="field__help">{field.help}</span> : null}
    </label>
  );
}
