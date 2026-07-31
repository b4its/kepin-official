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

  type BillingHistoryItem = {
    id: string;
    planCode: string;
    planName: string;
    price: string;
    currency: string;
    status: string;
    startDate?: string | null;
    endDate?: string | null;
    createdAt: string;
  };

  const slug = $derived($page.params.tenantSlug || '');
  let billing = $state<Billing | null>(null);
  let history = $state<BillingHistoryItem[]>([]);
  let loading = $state(false);
  let error = $state('');

  async function loadBilling() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      billing = await tenantApi.getBilling(slug) as Billing;
      history = await tenantApi.getBillingHistory(slug) as BillingHistoryItem[];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat billing';
    } finally {
      loading = false;
    }
  }

  const planName = $derived(history[0]?.planName || (billing ? `Paket ${billing.planCode}` : '-'));

  function formatDate(value?: string | null): string {
    if (!value) return '-';
    return new Date(value).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function formatMoney(item: BillingHistoryItem): string {
    const amount = Number(item.price || 0);
    return amount === 0 ? 'Rp0' : amount.toLocaleString('id-ID', { style: 'currency', currency: item.currency || 'IDR', maximumFractionDigits: 0 });
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
      <h3 class="font-semibold">{planName}</h3>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Paket {billing?.planCode ?? '-'}</p>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Status: {billing?.status ?? '-'}</p>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Periode: {formatDate(billing?.startDate)} s/d {formatDate(billing?.endDate)}</p>
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
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Backend belum mengembalikan daftar fitur.</p>
    {/if}
  </div>
</div>

<div class="card p-5 max-w-3xl mt-6">
  <h3 class="font-semibold mb-3">Riwayat Langganan</h3>
  {#if loading}
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat riwayat…</p>
  {:else if history.length === 0}
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada riwayat langganan.</p>
  {:else}
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs uppercase text-[hsl(var(--muted-foreground))] border-b border-[hsl(var(--border))]">
            <th class="py-2 pr-4 font-medium">Paket</th>
            <th class="py-2 pr-4 font-medium">Status</th>
            <th class="py-2 pr-4 font-medium">Periode</th>
            <th class="py-2 pr-4 font-medium text-right">Biaya</th>
            <th class="py-2 font-medium text-right">Mulai</th>
          </tr>
        </thead>
        <tbody>
          {#each history as item}
            <tr class="border-b border-[hsl(var(--border))] last:border-0">
              <td class="py-2.5 pr-4 font-medium">{item.planName} <span class="text-xs text-[hsl(var(--muted-foreground))]">({item.planCode})</span></td>
              <td class="py-2.5 pr-4">
                <span class="rounded-full border border-[hsl(var(--border))] px-2 py-0.5 text-xs uppercase" class:bg-green-50={item.status === 'active'}>{item.status}</span>
              </td>
              <td class="py-2.5 pr-4 text-[hsl(var(--muted-foreground))]">{formatDate(item.startDate)} s/d {formatDate(item.endDate)}</td>
              <td class="py-2.5 pr-4 text-right">{formatMoney(item)}</td>
              <td class="py-2.5 text-right text-[hsl(var(--muted-foreground))]">{formatDate(item.createdAt)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
