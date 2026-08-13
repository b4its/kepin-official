import { writable } from 'svelte/store';

export type TourElement = string | (() => Element | undefined | null);

export type TourStep = {
  /** CSS selector ATAU fungsi untuk elemen yang akan disorot. Kosongkan untuk popover di tengah layar. */
  element?: TourElement;
  /** Judul langkah */
  title: string;
  /** Penjelasan langkah */
  description: string;
  /**
   * Halaman tempat langkah ini muncul.
   * - Dimulai `/` → path absolut (mis. `/auth/login`, `/`)
   * - Selain itu → path relatif terhadap `/app/{slug}` (mis. `inventory/products`, `''` = dashboard)
   */
  page: string;
  /** Side effect: navigate ke halaman ini saat langkah dimulai */
  navigateTo?: string;
  /** Posisi popover */
  side?: 'top' | 'bottom' | 'left' | 'right';
  /** Align popover */
  align?: 'start' | 'center' | 'end';
  /** Grup/fase tur (untuk halaman tutorial) */
  phase: string;
};

export type TourPhase = {
  key: string;
  label: string;
  description: string;
};

export type TourConfig = {
  name: string;
  phases: TourPhase[];
  steps: TourStep[];
};

export const tourRunning = writable(false);
export const tourStepIndex = writable(0);
export const tourConfig = writable<TourConfig | null>(null);

/** Bertambah setiap kali tur diminta dimulai ulang (dari halaman tutorial). */
export const tourNonce = writable(0);

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

/** Slug tenant aktif: dari URL, atau fallback dari localStorage (sesi login). */
export function getTenantSlug(): string {
  if (typeof window !== 'undefined') {
    const parts = window.location.pathname.split('/');
    if (parts[1] === 'app' && parts[2]) return parts[2];
    try {
      const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
      if (Array.isArray(tenants) && tenants.length > 0) return tenants[0].slug;
    } catch { /* noop */ }
  }
  return '';
}

/** Path absolut dari sebuah langkah (mis. `/app/{slug}/inventory/products`). */
export function stepUrl(step: TourStep, slug: string): string {
  if (step.page.startsWith('/')) return step.page;
  const rel = step.page.replace(/^\/?/, '');
  return rel ? `/app/${slug}/${rel}` : `/app/${slug}`;
}

/** Apakah langkah ini muncul di pathname saat ini. */
export function stepMatchesPath(step: TourStep, pathname: string, slug: string): boolean {
  const target = step.page.startsWith('/') ? step.page : `/app/${slug}/${step.page.replace(/^\/?/, '')}`;
  if (target === `/app/${slug}/`) return pathname === `/app/${slug}` || pathname === `/app/${slug}/`;
  return pathname === target;
}

/** Menyuruh tur dimulai (atau dimulai ulang) dari langkah tertentu — dipakai halaman tutorial. */
export function requestTourStart(config: TourConfig, stepIndex: number) {
  const step = config.steps[stepIndex];
  if (!step) return;
  tourStepIndex.set(stepIndex);
  tourRunning.set(true);
  saveTourState(step.page, stepIndex);
  tourNonce.update((n) => n + 1);
}
