import type { CalculationResult } from "../../types";
import { money } from "../../format";

interface Props {
  result: CalculationResult;
}

export function ResultTable({ result }: Props) {
  if (result.line_items.length === 0) {
    return <p className="result-table__empty">Informe os dados para ver a estimativa.</p>;
  }

  return (
    <div className="result-table">
      <table>
        <thead>
          <tr>
            <th>Item</th>
            <th>Quantidade</th>
            <th>Preço unitário</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {result.line_items.map((item, idx) => (
            <tr key={idx}>
              <td>
                {item.label}
                {item.source_url ? (
                  <a
                    className="source-link"
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    fonte
                  </a>
                ) : null}
              </td>
              <td>
                {item.quantity} {item.unit}
              </td>
              <td>{money.format(item.unit_price)}</td>
              <td>{money.format(item.subtotal)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={3}>Total estimado</td>
            <td>{money.format(result.total)}</td>
          </tr>
        </tfoot>
      </table>
      {result.notes.length > 0 ? (
        <ul className="result-table__notes">
          {result.notes.map((note, idx) => (
            <li key={idx}>{note}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
