import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export type Toast = {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
};

export const toasts = writable<Toast[]>([]);

export function showToast(message: string, type: ToastType = 'info', duration = 4000): string {
  const id = crypto.randomUUID();
  toasts.update(t => [...t, { id, message, type, duration }]);
  if (duration > 0) {
    setTimeout(() => {
      toasts.update(t => t.filter(toast => toast.id !== id));
    }, duration);
  }
  return id;
}

export function dismissToast(id: string) {
  toasts.update(t => t.filter(toast => toast.id !== id));
}
