import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import type { CalculationResult, ServiceDefinition } from "../types";
import { money } from "../format";

export function downloadProjectReport(params: {
  services: ServiceDefinition[];
  results: CalculationResult[];
}): void {
  const { services, results } = params;
  const names = new Map(services.map((service) => [service.id, service.name]));
  const grandTotal = results.reduce((sum, result) => sum + result.total, 0);
  const generatedAt = new Date().toLocaleString("pt-BR");

  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 18;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Relatorio de custos - Projetos de dados no GCP", 14, y);
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
    "Estimativa baseada em precos publicos do Google Cloud (regiao US), sem descontos por compromisso de uso e sem impostos. Valores reais podem variar por regiao, negociacao comercial e uso real.",
    pageWidth - 28,
  );
  doc.text(disclaimer, 14, y);

  doc.save("relatorio-calculadora-gcp.pdf");
}
