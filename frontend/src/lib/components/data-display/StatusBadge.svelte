<script lang="ts">
  import Badge from '$lib/components/ui/Badge.svelte';

  type Props = {
    status: string;
    class?: string;
  };

  let { status, class: className = '' }: Props = $props();

  let config: Record<string, { label: string; variant: 'success' | 'info' | 'warning' | 'danger' | 'neutral' }> = $derived({
    active: { label: 'Aktif', variant: 'success' },
    inactive: { label: 'Nonaktif', variant: 'neutral' },
    trial: { label: 'Trial', variant: 'info' },
    suspended: { label: 'Ditangguhkan', variant: 'danger' },
    posted: { label: 'Diposting', variant: 'success' },
    draft: { label: 'Draft', variant: 'info' },
    voided: { label: 'Dibatalkan', variant: 'neutral' },
    reversed: { label: 'Reversal', variant: 'warning' },
    sent: { label: 'Terkirim', variant: 'info' },
    partial: { label: 'Sebagian', variant: 'warning' },
    paid: { label: 'Lunas', variant: 'success' },
    overdue: { label: 'Jatuh Tempo', variant: 'danger' },
    cancelled: { label: 'Batal', variant: 'neutral' },
    in: { label: 'Masuk', variant: 'success' },
    out: { label: 'Keluar', variant: 'warning' },
    adjustment: { label: 'Penyesuaian', variant: 'info' },
    transfer: { label: 'Transfer', variant: 'info' },
  });

  let current = $derived(config[status] ?? { label: status, variant: 'neutral' as const });
</script>

<Badge variant={current.variant} class={className}>
  {current.label}
</Badge>
