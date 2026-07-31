<script lang="ts">
  import { page } from '$app/stores';
  import { tenantApi } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Download, RefreshCw, Share2 } from '@lucide/svelte';

  type InvestorReport = {
    metadata: { period?: { startDate?: string; endDate?: string }; generated_at?: string; generatedAt?: string };
    metrics: { revenue: string; grossMargin: string; burnRate: string; cashPosition: string; runway: string | null };
    series: { month: string; revenue: string; expense: string }[];
    composition: { name: string; amount: string }[];
  };

  const slug = $derived($page.params.tenantSlug || '');
  let report = $state<InvestorReport | null>(null);
  let loading = $state(false);
  let error = $state('');
  let showExport = $state(false);

  const revenue = $derived(toNumber(report?.metrics.revenue));
  const grossMargin = $derived(toNumber(report?.metrics.grossMargin));
  const burnRate = $derived(toNumber(report?.metrics.burnRate));
  const cashPosition = $derived(toNumber(report?.metrics.cashPosition));
  const runway = $derived(report?.metrics.runway === null || report?.metrics.runway === undefined ? null : toNumber(report.metrics.runway));
  const marginPercent = $derived(revenue > 0 ? grossMargin / revenue * 100 : 0);

  const chart = $derived(() => ({
    labels: (report?.series ?? []).map((row) => row.month.slice(0, 7)),
    revenue: (report?.series ?? []).map((row) => toNumber(row.revenue)),
    expense: (report?.series ?? []).map((row) => toNumber(row.expense)),
  }));

  const exportColumns = [
    { key: 'label', label: 'Keterangan' },
    { key: 'value', label: 'Nilai' },
  ];

  const exportRows = $derived([
    { label: 'Periode', value: `${report?.metadata.period?.startDate ?? '-'} s/d ${report?.metadata.period?.endDate ?? '-'}` },
    { label: 'Total Pendapatan 6 Bulan', value: formatIDR(revenue) },
    { label: 'Gross Margin', value: formatIDR(grossMargin) },
    { label: 'Gross Margin %', value: `${marginPercent.toFixed(1)}%` },
    { label: 'Burn Rate', value: formatIDR(burnRate) },
    { label: 'Cash Position', value: formatIDR(cashPosition) },
    { label: 'Runway', value: runway === null ? '-' : `${runway.toFixed(1)} bulan` },
    ...(report?.composition ?? []).map((row) => ({ label: `Beban - ${row.name}`, value: formatIDR(toNumber(row.amount)) })),
  ]);

  function toNumber(value: string | number | null | undefined): number {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  async function loadReport() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      report = await tenantApi.getReports(slug, 'investor') as InvestorReport;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat investor report';
    } finally {
      loading = false;
    }
  }

  async function shareReport() {
    const text = `Investor Report ${slug}: revenue ${formatIDR(revenue)}, gross margin ${formatIDR(grossMargin)}`;
    if (navigator.share) {
      await navigator.share({ title: 'Investor Report KePin', text }).catch(() => undefined);
    } else {
      await navigator.clipboard?.writeText(text);
      showToast('Ringkasan investor report disalin', 'success');
    }
  }

  $effect(() => {
    if (slug) void loadReport();
  });
</script>

<PageHeader title="Investor Report" description="Laporan investor dari backend, tanpa angka dummy" breadcrumbs={[{ label: 'Laporan' }, { label: 'Investor' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={shareReport} disabled={!report || loading}><Share2 class="w-4 h-4" /> Bagikan</Button>
    <Button variant="secondary" onclick={loadReport} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    <Button onclick={() => showExport = true} disabled={!report || loading || Boolean(error)}><Download class="w-4 h-4" /> Ekspor</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="card p-5 mb-6">
  <h2 class="text-xl font-bold mb-1">Executive Summary</h2>
  <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">
    Periode: {report?.metadata.period?.startDate ?? '-'} s/d {report?.metadata.period?.endDate ?? '-'}
  </p>
  <p class="text-sm leading-relaxed">
    Pendapatan 6 bulan <strong>{formatIDR(revenue)}</strong>, gross margin <strong>{formatIDR(grossMargin)}</strong> ({marginPercent.toFixed(1)}%), cash position <strong>{formatIDR(cashPosition)}</strong>, dan runway <strong>{runway === null ? '-' : `${runway.toFixed(1)} bulan`}</strong>.
  </p>
</div>

<div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
  <MetricCard label="Pendapatan 6B" value={revenue} loading={loading} format="currency" />
  <MetricCard label="Gross Margin" value={grossMargin} loading={loading} format="currency" />
  <MetricCard label="Margin %" value={marginPercent} loading={loading} format="percent" />
  <MetricCard label="Cash Position" value={cashPosition} loading={loading} format="currency" />
  <MetricCard label="Runway" value={runway} loading={loading} format="number" unit=" bulan" />
</div>

<div class="grid lg:grid-cols-2 gap-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pendapatan vs Beban Bulanan</h3>
    <BarChart labels={chart().labels} datasets={[
      { label: 'Pendapatan', data: chart().revenue, color: '#059669' },
      { label: 'Beban', data: chart().expense, color: '#dc2626' },
    ]} height={220} yFormat="currency" />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Komposisi Beban</h3>
    {#if (report?.composition ?? []).length > 0}
      <PieChart labels={(report?.composition ?? []).map((row) => row.name)} values={(report?.composition ?? []).map((row) => toNumber(row.amount))} height={220} donut={true} />
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada beban pada periode investor report.</p>
    {/if}
  </div>
</div>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Investor Report"
  subtitle={`Periode ${report?.metadata.period?.startDate ?? '-'} s/d ${report?.metadata.period?.endDate ?? '-'}`}
  columns={exportColumns}
  rows={exportRows}
  filename="investor-report"
/>
