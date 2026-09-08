import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import type { CalculationResult, ServiceDefinition } from "../types";
import { money } from "../format";

export function downloadProjectReport(params: {
  services: ServiceDefinition[];
  results: CalculationResult[];
  title?: string;
  disclaimer?: string;
}): void {
  const { services, results } = params;
  const title = params.title ?? "Relatorio de custos - Projetos de dados no GCP";
  const disclaimerText =
    params.disclaimer ??
    "Estimativa baseada em precos publicos do Google Cloud (regiao US), sem descontos por compromisso de uso e sem impostos. Valores reais podem variar por regiao, negociacao comercial e uso real.";
  const names = new Map(services.map((service) => [service.id, service.name]));
  const grandTotal = results.reduce((sum, result) => sum + result.total, 0);
  const generatedAt = new Date().toLocaleString("pt-BR");

  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 18;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text(title, 14, y);
  y += 8;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(90);
  doc.text(`Gerado em ${generatedAt}`, 14, y);
  y += 10;
  doc.setTextColor(20);

  for (const result of results) {
    if (y > 250) {
      doc.addPage();
      y = 18;
    }
    const title = names.get(result.service_id) ?? result.service_id;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.text(title, 14, y);
    y += 4;

    autoTable(doc, {
      startY: y,
      head: [["Item", "Quantidade", "Preco unitario", "Subtotal"]],
      body: result.line_items.map((item) => [
        item.label,
        `${item.quantity} ${item.unit}`,
        money.format(item.unit_price),
        money.format(item.subtotal),
      ]),
      foot: [["Total estimado", "", "", money.format(result.total)]],
      theme: "striped",
      styles: { fontSize: 9 },
      headStyles: { fillColor: [91, 33, 182] },
      footStyles: { fillColor: [245, 241, 254], textColor: [91, 33, 182], fontStyle: "bold" },
      margin: { left: 14, right: 14 },
    });
    y = ((doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY ?? y) + 6;

    if (result.notes.length > 0) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.setTextColor(90);
      for (const note of result.notes) {
        const noteLines = doc.splitTextToSize(`- ${note}`, pageWidth - 28);
        if (y + noteLines.length * 4 > 280) {
          doc.addPage();
          y = 18;
        }
        doc.text(noteLines, 14, y);
        y += noteLines.length * 4 + 1;
      }
      doc.setTextColor(20);
      y += 4;
    }
  }

  if (y > 250) {
    doc.addPage();
    y = 18;
  }
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.text(`Total mensal estimado: ${money.format(grandTotal)}`, 14, y);
  y += 10;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(110);
  const disclaimer = doc.splitTextToSize(
    disclaimerText,
    pageWidth - 28,
  );
  doc.text(disclaimer, 14, y);

  doc.save("relatorio-calculadora-gcp.pdf");
}

function addScenarioSection(
  doc: jsPDF,
  heading: string,
  names: Map<string, string>,
  results: CalculationResult[],
  total: number,
  y: number,
): number {
  const pageWidth = doc.internal.pageSize.getWidth();
  if (y > 250) {
    doc.addPage();
    y = 18;
  }
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(20);
  doc.text(heading, 14, y);
  y += 6;
  autoTable(doc, {
    startY: y,
    head: [["Servico", "Total / mes"]],
    body: results.map((result) => [
      names.get(result.service_id) ?? result.service_id,
      money.format(result.total),
    ]),
    foot: [["Total", money.format(total)]],
    theme: "striped",
    styles: { fontSize: 9 },
    headStyles: { fillColor: [40, 40, 40] },
    footStyles: { fillColor: [30, 30, 30], textColor: [255, 255, 255], fontStyle: "bold" },
    margin: { left: 14, right: 14 },
  });
  y = ((doc as unknown as { lastAutoTable: { finalY: number } }).lastAutoTable.finalY ?? y) + 10;
  void pageWidth;
  return y;
}

export function downloadCompareReport(params: {
  services: ServiceDefinition[];
  asIs: CalculationResult[];
  toBe: CalculationResult[];
  asIsLabel: string;
  toBeLabel: string;
  disclaimer?: string;
}): void {
  const names = new Map(params.services.map((service) => [service.id, service.name]));
  const asIsTotal = params.asIs.reduce((sum, result) => sum + result.total, 0);
  const toBeTotal = params.toBe.reduce((sum, result) => sum + result.total, 0);
  const delta = toBeTotal - asIsTotal;
  const generatedAt = new Date().toLocaleString("pt-BR");
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 18;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Relatorio AS IS vs TO-BE", 14, y);
  y += 8;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(90);
  doc.text(`Gerado em ${generatedAt}`, 14, y);
  y += 10;

  doc.setTextColor(20);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.text("Diferenca de preco (mensal)", 14, y);
  y += 7;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(`AS IS (${params.asIsLabel}): ${money.format(asIsTotal)}`, 14, y);
  y += 6;
  doc.text(`TO-BE (${params.toBeLabel}): ${money.format(toBeTotal)}`, 14, y);
  y += 6;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  if (delta > 0.005) {
    doc.setTextColor(180, 40, 40);
    doc.text(`TO-BE e ${money.format(delta)} mais caro que o AS IS por mes.`, 14, y);
  } else if (delta < -0.005) {
    doc.setTextColor(30, 130, 70);
    doc.text(`TO-BE e ${money.format(Math.abs(delta))} mais barato que o AS IS por mes.`, 14, y);
  } else {
    doc.setTextColor(20);
    doc.text("TO-BE tem o mesmo custo mensal do AS IS.", 14, y);
  }
  y += 12;
  doc.setTextColor(20);

  y = addScenarioSection(doc, `AS IS — ${params.asIsLabel}`, names, params.asIs, asIsTotal, y);
  y = addScenarioSection(doc, `TO-BE — ${params.toBeLabel}`, names, params.toBe, toBeTotal, y);

  if (y > 250) {
    doc.addPage();
    y = 18;
  }
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(110);
  const disclaimer = doc.splitTextToSize(
    params.disclaimer ??
      "Estimativa com precos publicos de lista, sem desconto e sem impostos. Confirme nas calculadoras oficiais.",
    pageWidth - 28,
  );
  doc.text(disclaimer, 14, y);
  doc.save("relatorio-as-is-to-be.pdf");
}
