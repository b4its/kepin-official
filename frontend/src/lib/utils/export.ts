/**
 * Export utility — PDF (jsPDF + autoTable) and Excel (SheetJS).
 * All functions are client-side only; call them from browser event handlers.
 */

export interface ExportColumn {
  key: string;
  label: string;
  render?: (row: any) => string;
}

export interface ExportOptions {
  title: string;
  subtitle?: string;
  columns: ExportColumn[];
  rows: any[];
  filename?: string;
}

// ── helpers ──────────────────────────────────────────────────────────

function cellValue(col: ExportColumn, row: any): string {
  if (col.render) {
    // strip HTML tags from rendered values
    return col.render(row).replace(/<[^>]*>/g, '');
  }
  const v = row[col.key];
  return v == null ? '' : String(v);
}

function buildHead(cols: ExportColumn[]): string[] {
  return cols.map((c) => c.label);
}

function buildBody(cols: ExportColumn[], rows: any[]): string[][] {
  return rows.map((r) => cols.map((c) => cellValue(c, r)));
}

// ── PDF ──────────────────────────────────────────────────────────────

export async function downloadPdf(opts: ExportOptions): Promise<void> {
  const { default: jsPDF } = await import('jspdf');
  const autoTable = (await import('jspdf-autotable')).default;

  const doc = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'a4' });

  const now = new Date().toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' });

  // header
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text(opts.title, 40, 40);

  if (opts.subtitle) {
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(opts.subtitle, 40, 56);
  }

  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(120, 120, 120);
  doc.text(`Dicetak: ${now}`, 40, opts.subtitle ? 68 : 56);
  doc.setTextColor(0, 0, 0);

  autoTable(doc, {
    startY: opts.subtitle ? 80 : 72,
    head: [buildHead(opts.columns)],
    body: buildBody(opts.columns, opts.rows),
    styles: { fontSize: 8, cellPadding: 4 },
    headStyles: {
      fillColor: [21, 89, 199],
      textColor: 255,
      fontStyle: 'bold',
    },
    alternateRowStyles: { fillColor: [245, 247, 252] },
    margin: { left: 40, right: 40 },
  });

  doc.save(`${opts.filename ?? opts.title}.pdf`);
}

// ── Excel ─────────────────────────────────────────────────────────────

export async function downloadExcel(opts: ExportOptions): Promise<void> {
  const XLSX = await import('xlsx');

  const header = buildHead(opts.columns);
  const data = buildBody(opts.columns, opts.rows);

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet([header, ...data]);

  // auto column widths
  const colWidths = opts.columns.map((col, ci) => {
    const maxLen = Math.max(
      col.label.length,
      ...opts.rows.map((r) => cellValue(col, r).length),
    );
    return { wch: Math.min(Math.max(maxLen, 8), 40) };
  });
  ws['!cols'] = colWidths;

  // bold header row
  const range = XLSX.utils.decode_range(ws['!ref'] ?? 'A1');
  for (let C = range.s.c; C <= range.e.c; C++) {
    const addr = XLSX.utils.encode_cell({ r: 0, c: C });
    if (ws[addr]) {
      ws[addr].s = { font: { bold: true }, fill: { fgColor: { rgb: 'DBEAFE' } } };
    }
  }

  XLSX.utils.book_append_sheet(wb, ws, opts.title.slice(0, 31));
  XLSX.writeFile(wb, `${opts.filename ?? opts.title}.xlsx`);
}
