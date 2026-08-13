import { writable } from 'svelte/store';

export type TourStep = {
  /** CSS selector untuk elemen yang akan disorot. Kosongkan untuk popover di tengah layar. */
  element?: string;
  /** Judul langkah */
  title: string;
  /** Penjelasan langkah */
  description: string;
  /** URL halaman tempat langkah ini muncul (relatif dari /app/{slug}) */
  page: string;
  /** Side effect: navigate ke halaman ini saat langkah dimulai */
  navigateTo?: string;
  /** Posisi popover */
  side?: 'top' | 'bottom' | 'left' | 'right';
  /** Align popover */
  align?: 'start' | 'center' | 'end';
};

export type TourConfig = {
  name: string;
  steps: TourStep[];
};

export const tourRunning = writable(false);
export const tourStepIndex = writable(0);
export const tourConfig = writable<TourConfig | null>(null);

const STORAGE_KEY = 'kepin_tour_active';

export function saveTourState(page: string, step: number) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ page, step }));
}

export function loadTourState(): { page: string; step: number } | null {
  if (typeof localStorage === 'undefined') return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearTourState() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
}