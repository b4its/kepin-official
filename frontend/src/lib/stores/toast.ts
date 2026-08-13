import { writable } from 'svelte/store';
import { createId } from '$lib/utils/id';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export type Toast = {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
};

export const toasts = writable<Toast[]>([]);

export function showToast(message: string, type: ToastType = 'info', duration = 4000): string {
  const id = createId();
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
