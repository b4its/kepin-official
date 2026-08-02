<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { tenantApi } from '$lib/stores/data';
  import type { Preset } from '$lib/utils/dateRange';
  import { AlertTriangle, RefreshCw, TrendingUp } from '@lucide/svelte';

  type Insight = { title: string; description: string; impact: 'positive' | 'negative'; horizon: string; factors: string[] };
  type Dashboard = {
    metrics: { income: string; expense: string; grossProfit: string; cashBalance: string };
    cashFlow: { date: string; income: string; expense: string }[];
    cash_flow?: { date: string; income: string; expense: string }[];
    insights: Insight[];
    alerts: { type: string; message: string }[];
  };

  const slug = $derived($page.params.tenantSlug || '');
  let startDate = $state('');
  let endDate = $state('');
  let data = $state<Dashboard | null>(null);
  let loading = $state(false);
  let error = $state('');
  let compareMode = $state(false);
  let compareStart = $state('');
  let compareEnd = $state('');
  let compareData = $state<Dashboard | null>(null);
  let compareLoading = $state(false);
  const flow = $derived(data?.cashFlow ?? data?.cash_flow ?? []);
  const income = $derived(number(data?.metrics.income));
  const expense = $derived(number(data?.metrics.expense));
  const profit = $derived(number(data?.metrics.grossProfit));
  const cash = $derived(number(data?.metrics.cashBalance));
  const compareIncome = $derived(compareMode ? number(compareData?.metrics.income) : null);
  const compareExpense = $derived(compareMode ? number(compareData?.metrics.expense) : null);
  const compareProfit = $derived(compareMode ? number(compareData?.metrics.grossProfit) : null);

  function number(value: string | number | undefined) { const parsed = Number(value ?? 0); return Number.isFinite(parsed) ? parsed : 0; }
  function onRangeChange(_preset: Preset, start: string, end: string) { startDate = start; endDate = end; }

  function defaultCompareRange() {
    if (!startDate || !endDate) return;
    const span = new Date(`${endDate}T00:00:00`).getTime() - new Date(`${startDate}T00:00:00`).getTime();
    const cEnd = new Date(`${startDate}T00:00:00`).getTime() - 86400000;
    compareStart = new Date(cEnd - span).toISOString().slice(0, 10);
    compareEnd = new Date(cEnd).toISOString().slice(0, 10);
  }

  function toggleCompare() {
    compareMode = !compareMode;
    if (compareMode) defaultCompareRange();
  }

  async function loadCompare() {
    if (!slug || !compareStart || !compareEnd) return;
    compareLoading = true;
    try {
      compareData = await tenantApi.getTenantDashboard(slug, { startDate: compareStart, endDate: compareEnd }) as Dashboard;
    } catch {
      compareData = null;
    } finally {
      compareLoading = false;
    }
  }

  async function loadInsights() {
    if (!slug || !startDate || !endDate) return;
    loading = true;
    error = '';
    try {
      data = await tenantApi.getTenantDashboard(slug, { startDate, endDate }) as Dashboard;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat analitik bisnis';
    } finally { loading = false; }
  }

  $effect(() => {
    const now = new Date();
    const end = now.toISOString().slice(0, 10);
    const start = new Date(now.getTime() - 30 * 86400000).toISOString().slice(0, 10);
    if (!startDate) { startDate = start; endDate = end; }
  });
  $effect(() => { if (slug && startDate && endDate) void loadInsights(); });
  $effect(() => {
    if (slug && compareMode && compareStart && compareEnd) {
      void loadCompare();
    }
  });
</script>

<PageHeader title="Analitik Bisnis" description="Insight deterministik dari transaksi posted dan GL" breadcrumbs={[{ label: 'Analitik Bisnis' }]}> 
  {#snippet actions()}<Button variant="secondary" onclick={loadInsights} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>{/snippet}
</PageHeader>
<div class="mb-6"><DateRangeFilter onChange={onRangeChange} /></div>
{#if error}<div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}

<div class="card mb-4 flex flex-wrap items-center gap-x-5 gap-y-2 p-4">
  <label class="flex cursor-pointer items-center gap-2 text-sm font-medium">
    <input type="checkbox" checked={compareMode} onclick={toggleCompare} class="h-4 w-4" />
    Bandingkan dengan periode sebelumnya
  </label>
  {#if compareMode}
    <div class="flex flex-wrap items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
      <span>Periode pembanding:</span>
      <input type="date" bind:value={compareStart} class="input-field" aria-label="Tanggal mulai pembanding" />
      <span>s.d.</span>
      <input type="date" bind:value={compareEnd} class="input-field" aria-label="Tanggal akhir pembanding" />
    </div>
    <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={defaultCompareRange}>← Periode sebelumnya</button>
    {#if compareLoading}<span class="text-xs text-[hsl(var(--muted-foreground))]">Memuat…</span>{/if}
  {/if}
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"><MetricCard label="Pendapatan" value={income} previousValue={compareMode ? compareIncome : undefined} loading={loading} format="currency" /><MetricCard label="Beban" value={expense} previousValue={compareMode ? compareExpense : undefined} loading={loading} format="currency" /><MetricCard label="Laba Bersih" value={profit} previousValue={compareMode ? compareProfit : undefined} loading={loading} format="currency" /><MetricCard label="Kas & Bank" value={cash} loading={loading} format="currency" /></div>

<div class="card p-5 mb-6"><h3 class="font-semibold mb-4">Pendapatan dan Beban Harian</h3><BarChart labels={flow.map((row) => row.date.slice(5))} datasets={[{ label: 'Pendapatan', data: flow.map((row) => number(row.income)), color: '#059669' }, { label: 'Beban', data: flow.map((row) => number(row.expense)), color: '#dc2626' }]} height={220} yFormat="currency" /></div>

<div class="space-y-4">
  {#each data?.insights ?? [] as insight}
    <div class="card p-5"><div class="flex items-start gap-4">{#if insight.impact === 'positive'}<TrendingUp class="w-6 h-6 shrink-0 text-[var(--color-kepin-green)]" />{:else}<AlertTriangle class="w-6 h-6 shrink-0 text-[var(--color-kepin-yellow)]" />{/if}<div><h3 class="font-semibold">{insight.title}</h3><p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">{insight.description}</p><p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">Horizon: {insight.horizon} · Faktor: {insight.factors.join(', ')}</p></div></div></div>
  {:else}
    <div class="card p-5 text-center text-sm text-[hsl(var(--muted-foreground))]">Belum ada insight untuk periode ini.</div>
  {/each}
</div>
