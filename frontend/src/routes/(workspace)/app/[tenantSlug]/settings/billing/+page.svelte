<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { tenantApi } from '$lib/stores/data';
  import { RefreshCw } from '@lucide/svelte';

  type Billing = {
    tenantId: string;
    planCode: string;
    status: string;
    startDate?: string | null;
    endDate?: string | null;
    features: string[];
  };

  const slug = $derived($page.params.tenantSlug || '');
  let billing = $state<Billing | null>(null);
  let loading = $state(false);
  let error = $state('');

  async function loadBilling() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      billing = await tenantApi.getBilling(slug) as Billing;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat billing';
    } finally {
      loading = false;
    }
  }

  $effect(() => { if (slug) void loadBilling(); });
</script>

<PageHeader title="Billing" description="Langganan dan tagihan dari backend" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Billing' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadBilling} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6 max-w-3xl">
  <MetricCard label="Paket" value={0} format="number" loading={loading} />
  <MetricCard label="Fitur Aktif" value={billing?.features?.length ?? 0} format="number" loading={loading} />
  <MetricCard label="Status" value={billing?.status === 'active' ? 1 : 0} format="number" loading={loading} />
</div>

<div class="card p-5 max-w-2xl">
  <div class="flex items-start justify-between gap-4">
    <div>
      <h3 class="font-semibold">Paket {billing?.planCode ?? '-'}</h3>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Status: {billing?.status ?? '-'}</p>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Periode: {billing?.startDate ?? '-'} s/d {billing?.endDate ?? '-'}</p>
    </div>
    <span class="rounded-full border border-[hsl(var(--border))] px-2.5 py-1 text-xs uppercase">{billing?.status ?? 'unknown'}</span>
  </div>

  <div class="mt-5 border-t border-[hsl(var(--border))] pt-4">
    <h4 class="text-sm font-semibold mb-2">Fitur Backend</h4>
    {#if (billing?.features ?? []).length > 0}
      <ul class="list-disc pl-5 text-sm text-[hsl(var(--muted-foreground))]">
        {#each billing?.features ?? [] as feature}
          <li>{feature}</li>
        {/each}
      </ul>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Backend belum mengembalikan daftar fitur atau invoice billing. Tidak menampilkan riwayat tagihan dummy.</p>
    {/if}
  </div>
</div>
