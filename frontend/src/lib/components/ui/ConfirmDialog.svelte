<script lang="ts">
  import type { Snippet } from 'svelte';
  import { AlertTriangle } from '@lucide/svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  type Props = {
    open: boolean;
    onclose: () => void;
    onconfirm: () => void;
    title?: string;
    message?: string;
    confirmText?: string;
    loading?: boolean;
    children?: Snippet;
  };

  let {
    open,
    onclose,
    onconfirm,
    title = 'Konfirmasi',
    message = 'Apakah Anda yakin?',
    confirmText = 'Hapus',
    loading = false,
    children,
  }: Props = $props();
</script>

<Modal {open} {onclose} size="sm">
  <div class="text-center">
    <AlertTriangle class="w-10 h-10 text-[var(--color-kepin-danger)] mx-auto mb-3" />
    <h3 class="font-semibold text-sm mb-1">{title}</h3>
    <p class="text-xs text-[hsl(var(--muted-foreground))] mb-5">{message}</p>
    {#if children}
      <div class="mb-4">{@render children()}</div>
    {/if}
    <div class="flex justify-center gap-2">
      <Button variant="secondary" onclick={onclose} disabled={loading}>Batal</Button>
      <Button variant="destructive" onclick={onconfirm} disabled={loading} loading={loading}>{confirmText}</Button>
    </div>
  </div>
</Modal>