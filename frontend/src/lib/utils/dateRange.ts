export type DateRange = {
  startDate: string;
  endDate: string;
};

export type Preset = '1week' | '2week' | '3week' | '1month' | 'custom';

export function getDateRange(preset: Preset, customStart?: string, customEnd?: string): DateRange {
  const now = new Date();
  const end = now.toISOString().slice(0, 10);

  if (preset === 'custom') {
    return {
      startDate: customStart || end,
      endDate: customEnd || end,
    };
  }

  const days = { '1week': 7, '2week': 14, '3week': 21, '1month': 30 }[preset] ?? 7;
  const start = new Date(now.getTime() - days * 86400000).toISOString().slice(0, 10);
  return { startDate: start, endDate: end };
}

export const presetLabels: Record<Preset, string> = {
  '1week': 'Minggu lalu',
  '2week': '2 Minggu lalu',
  '3week': '3 Minggu lalu',
  '1month': '1 Bulan',
  'custom': 'Kustom',
};

export function inDateRange<T extends { date?: string; createdAt?: string; timestamp?: string }>(
  item: T,
  range: DateRange
): boolean {
  const d = item.date || item.createdAt || item.timestamp || '';
  return d.slice(0, 10) >= range.startDate && d.slice(0, 10) <= range.endDate;
}
