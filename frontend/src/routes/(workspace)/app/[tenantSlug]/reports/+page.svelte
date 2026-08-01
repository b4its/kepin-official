<script lang="ts">
  import { page } from '$app/stores';
  import { api } from '$lib/api/client';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { showToast } from '$lib/stores/toast';
  import { currentRole } from '$lib/stores/data';
  import { formatIDR, formatNumber } from '$lib/utils/currency';
  import type { Preset } from '$lib/utils/dateRange';
  import { Download, RefreshCw } from '@lucide/svelte';

  type SummaryReport = {
    summary: { income: string; expense: string; profit: string };
    series: { date: string; income: string; expense: string }[];
    composition: { name: string; amount: string }[];
  };

  type ProfitLossReport = {
    summary: { totalIncome: string; totalExpense: string; netProfit: string };
    rows: { code: string; name: string; type: string; debitTotal: string; creditTotal: string; net: string }[];
  };

  type BalanceSheetReport = {
    summary: { totalAssets: string; totalLiabilities: string; totalEquity: string; liabilitiesPlusEquity: string };
    rows: { code: string; name: string; type: string; balance: string }[];
  };

  type TrialBalanceReport = {
    summary: { totalDebit: string; totalCredit: string; balanced: boolean };
    rows: {
      code: string;
      name: string;
      type: string;
      openingBalance: string;
      periodDebit: string;
      periodCredit: string;
      closingBalance: string;
      debit: string;
      credit: string;
    }[];
  };

  type ReceivableAgingReport = {
    buckets: Record<string, { total: string; items: unknown[] }>;
    grandTotal: string;
  };

  type PayableAgingReport = {
    rows: { supplierId: string; supplierName: string; received: string; paid: string; outstanding: string; bucket: string; daysSinceReceipt: number }[];
    grandTotal: string;
  };

  type StockValuationReport = {
    summary: { totalValue: string; glInventoryValue: string; glDelta: string };
    rows: { sku: string; productName: string; quantity: string; averageCost: string; value: string }[];
  };

  type CashFlowReport = {
    summary: { operating: string; investing: string; financing: string; netCashFlow: string };
    rows: {
      date: string;
      description: string;
      accountId: string;
      accountName: string;
      type: string;
      inflow: string;
      outflow: string;
    }[];
  };

  type MonthlyProfitLoss = {
    rows: { month: string; income: string; expense: string; profit: string }[];
  };

  type MonthlyBalanceSheet = {
    rows: { month: string; assets: string; liabilities: string; equity: string; liabilitiesPlusEquity: string }[];
  };

  type MonthlyCashFlow = {
    rows: { month: string; operating: string; investing: string; financing: string; net: string }[];
  };

  type AccountingPeriod = {
    id: string;
    name: string;
    startDate: string;
    endDate: string;
    status: string;
    closingJournalId?: string | null;
  };

  type FiscalYear = { id: string; name: string; periods: AccountingPeriod[] };

  const tabs = [
    { id: 'summary', label: 'Ringkasan' },
    { id: 'trial', label: 'Neraca Saldo' },
    { id: 'profit-loss', label: 'Laba Rugi' },
    { id: 'balance-sheet', label: 'Neraca' },
    { id: 'cash-flow', label: 'Arus Kas' },
    { id: 'aging', label: 'Aging' },
    { id: 'stock', label: 'Valuasi Stok' },
  ] as const;

  let startDate = $state('');
  let endDate = $state('');
  let loading = $state(false);
  let actionLoading = $state(false);
  let error = $state('');
  let activeTab = $state<(typeof tabs)[number]['id']>('summary');
  let includeClosing = $state(false);
  let showExport = $state(false);
  let requestSeq = 0;

  let summary = $state<SummaryReport | null>(null);
  let profitLoss = $state<ProfitLossReport | null>(null);
  let balanceSheet = $state<BalanceSheetReport | null>(null);
  let trialBalance = $state<TrialBalanceReport | null>(null);
  let receivableAging = $state<ReceivableAgingReport | null>(null);
  let payableAging = $state<PayableAgingReport | null>(null);
  let stockValuation = $state<StockValuationReport | null>(null);
  let cashFlow = $state<CashFlowReport | null>(null);
  let monthlyProfitLoss = $state<MonthlyProfitLoss | null>(null);
  let monthlyBalanceSheet = $state<MonthlyBalanceSheet | null>(null);
  let monthlyCashFlow = $state<MonthlyCashFlow | null>(null);
  let fiscalYears = $state<FiscalYear[]>([]);

  const tenantSlug = $derived($page.params.tenantSlug || '');
  const periods = $derived(fiscalYears.flatMap((fy) => fy.periods || []));
  const selectedPeriod = $derived(
    periods.find((p) => endDate >= p.startDate && endDate <= p.endDate) ?? null
  );
  const isOwner = $derived($currentRole === 'tenant_owner');

  const totalIncome = $derived(toNumber(summary?.summary.income));
  const totalExpense = $derived(toNumber(summary?.summary.expense));
  const netProfit = $derived(toNumber(summary?.summary.profit));
  const totalAssets = $derived(toNumber(balanceSheet?.summary.totalAssets));
  const liabilitiesPlusEquity = $derived(toNumber(balanceSheet?.summary.liabilitiesPlusEquity));
  const balanceGap = $derived(totalAssets - liabilitiesPlusEquity);
  const arOutstanding = $derived(toNumber(receivableAging?.grandTotal));
  const apOutstanding = $derived(toNumber(payableAging?.grandTotal));
  const stockGlDelta = $derived(toNumber(stockValuation?.summary.glDelta));
  const cashOperating = $derived(toNumber(cashFlow?.summary.operating));
  const cashInvesting = $derived(toNumber(cashFlow?.summary.investing));
  const cashFinancing = $derived(toNumber(cashFlow?.summary.financing));
  const cashNet = $derived(toNumber(cashFlow?.summary.netCashFlow));

  const summaryChart = $derived(() => {
    const rows = summary?.series ?? [];
    return {
      labels: rows.map((row) => row.date.slice(5)),
      income: rows.map((row) => toNumber(row.income)),
      expense: rows.map((row) => toNumber(row.expense)),
    };
  });

  const exportKinds = [
    { value: 'summary', label: 'Ringkasan' },
    { value: 'trial', label: 'Neraca Saldo' },
    { value: 'profit-loss', label: 'Laba Rugi' },
    { value: 'balance-sheet', label: 'Neraca' },
    { value: 'cash-flow', label: 'Arus Kas' },
    { value: 'aging', label: 'Aging' },
    { value: 'stock', label: 'Valuasi Stok' },
  ] as const;

  let exportKind = $state<(typeof exportKinds)[number]['value']>('summary');

  const EXPORT_COLUMNS: Record<string, { key: string; label: string }[]> = {
    summary: [
      { key: 'section', label: 'Bagian' },
      { key: 'label', label: 'Keterangan' },
      { key: 'value', label: 'Nilai' },
    ],
    trial: [
      { key: 'code', label: 'Kode' },
      { key: 'name', label: 'Akun' },
      { key: 'type', label: 'Tipe' },
      { key: 'openingBalance', label: 'Saldo Awal' },
      { key: 'periodDebit', label: 'Debit Periode' },
      { key: 'periodCredit', label: 'Kredit Periode' },
      { key: 'debit', label: 'Debit Akhir' },
      { key: 'credit', label: 'Kredit Akhir' },
    ],
    'profit-loss': [
      { key: 'code', label: 'Kode' },
      { key: 'name', label: 'Akun' },
      { key: 'type', label: 'Tipe' },
      { key: 'debitTotal', label: 'Debit' },
      { key: 'creditTotal', label: 'Kredit' },
      { key: 'net', label: 'Net' },
    ],
    'balance-sheet': [
      { key: 'code', label: 'Kode' },
      { key: 'name', label: 'Akun' },
      { key: 'type', label: 'Tipe' },
      { key: 'balance', label: 'Saldo' },
    ],
    'cash-flow': [
      { key: 'date', label: 'Tanggal' },
      { key: 'description', label: 'Deskripsi' },
      { key: 'accountName', label: 'Akun Kas' },
      { key: 'type', label: 'Kategori' },
      { key: 'inflow', label: 'Masuk' },
      { key: 'outflow', label: 'Keluar' },
    ],
    aging: [
      { key: 'section', label: 'Bagian' },
      { key: 'label', label: 'Keterangan' },
      { key: 'value', label: 'Nilai' },
    ],
    stock: [
      { key: 'sku', label: 'SKU' },
      { key: 'productName', label: 'Produk' },
      { key: 'quantity', label: 'Qty' },
      { key: 'averageCost', label: 'Avg Cost' },
      { key: 'value', label: 'Nilai' },
    ],
  };

  const EXPORT_COLUMN_RENDER: Record<string, { key: string; render: (row: any) => string }[]> = {
    trial: [
      { key: 'openingBalance', render: (r) => money(r.openingBalance) },
      { key: 'periodDebit', render: (r) => money(r.periodDebit) },
      { key: 'periodCredit', render: (r) => money(r.periodCredit) },
      { key: 'debit', render: (r) => money(r.debit) },
      { key: 'credit', render: (r) => money(r.credit) },
    ],
    'profit-loss': [
      { key: 'debitTotal', render: (r) => money(r.debitTotal) },
      { key: 'creditTotal', render: (r) => money(r.creditTotal) },
      { key: 'net', render: (r) => money(r.net) },
    ],
    'balance-sheet': [{ key: 'balance', render: (r) => money(r.balance) }],
    'cash-flow': [
      { key: 'inflow', render: (r) => (toNumber(r.inflow) > 0 ? money(r.inflow) : '-') },
      { key: 'outflow', render: (r) => (toNumber(r.outflow) > 0 ? money(r.outflow) : '-') },
    ],
    stock: [
      { key: 'quantity', render: (r) => formatNumber(toNumber(r.quantity)) },
      { key: 'averageCost', render: (r) => money(r.averageCost) },
      { key: 'value', render: (r) => money(r.value) },
    ],
  };

  const exportColumns = $derived(
    EXPORT_COLUMNS[exportKind].map((col) => {
      const renderCol = EXPORT_COLUMN_RENDER[exportKind]?.find((c) => c.key === col.key);
      return renderCol ? { ...col, render: renderCol.render } : col;
    })
  );

  const exportRows = $derived(() => {
    switch (exportKind) {
      case 'trial':
        return trialBalance?.rows ?? [];
      case 'profit-loss':
        return profitLoss?.rows ?? [];
      case 'balance-sheet':
        return balanceSheet?.rows ?? [];
      case 'cash-flow':
        return cashFlow?.rows ?? [];
      case 'stock':
        return stockValuation?.rows ?? [];
      case 'aging': {
        const rows: any[] = [];
        for (const [bucket, data] of Object.entries(receivableAging?.buckets ?? {})) {
          rows.push({ section: 'Piutang', label: `Bucket ${bucket}`, value: money(data.total) });
        }
        rows.push({ section: 'Piutang', label: 'Total Piutang', value: money(receivableAging?.grandTotal) });
        for (const row of payableAging?.rows ?? []) {
          rows.push({ section: 'Hutang', label: `${row.supplierName} (${row.bucket})`, value: money(row.outstanding) });
        }
        rows.push({ section: 'Hutang', label: 'Total Hutang', value: money(payableAging?.grandTotal) });
        return rows;
      }
      case 'summary':
      default:
        return [
          { section: 'Periode', label: 'Rentang', value: `${startDate} s/d ${endDate}` },
          { section: 'Ringkasan', label: 'Pendapatan', value: formatIDR(totalIncome) },
          { section: 'Ringkasan', label: 'Beban', value: formatIDR(totalExpense) },
          { section: 'Ringkasan', label: 'Laba Bersih', value: formatIDR(netProfit) },
          { section: 'Neraca', label: 'Total Aset', value: formatIDR(totalAssets) },
          { section: 'Neraca', label: 'Kewajiban + Ekuitas', value: formatIDR(liabilitiesPlusEquity) },
          { section: 'Aging', label: 'Piutang Outstanding', value: formatIDR(arOutstanding) },
          { section: 'Aging', label: 'Hutang Outstanding', value: formatIDR(apOutstanding) },
          { section: 'Inventaris', label: 'Delta GL vs Stock', value: formatIDR(stockGlDelta) },
          { section: 'Arus Kas', label: 'Net Arus Kas', value: formatIDR(cashNet) },
        ];
    }
  });


  function toNumber(value: string | number | null | undefined): number {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function money(value: string | number | null | undefined): string {
    return formatIDR(toNumber(value));
  }

  const monthLabels = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];

  function monthName(ym: string): string {
    const [y, m] = ym.split('-').map(Number);
    if (!y || !m || m < 1 || m > 12) return ym;
    return `${monthLabels[m - 1]} ${y}`;
  }

  function deltaTone(prev: number | undefined, curr: number): 'up' | 'down' | 'none' {
    if (prev === undefined) return 'none';
    return curr >= prev ? 'up' : 'down';
  }

  function deltaLabel(prev: number | undefined, curr: number): string {
    if (prev === undefined) return '—';
    const diff = curr - prev;
    if (diff === 0) return '0';
    const sign = diff > 0 ? '+' : '';
    const pct = prev !== 0 ? ` (${sign}${((diff / Math.abs(prev)) * 100).toFixed(0)}%)` : '';
    return `${sign}${formatIDR(diff)}${pct}`;
  }

  function query(params: Record<string, string | boolean | undefined>) {
    const search = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== '') search.set(key, String(value));
    }
    return search.toString();
  }

  function onRangeChange(_preset: Preset, start: string, end: string) {
    startDate = start;
    endDate = end;
  }

  async function loadReports(slug: string, start: string, end: string, closing: boolean) {
    const seq = ++requestSeq;
    loading = true;
    error = '';
    const q = query({ startDate: start, endDate: end });
    const tbq = query({ startDate: start, endDate: end, includeClosing: closing });
    try {
      const [summaryRes, profitLossRes, balanceSheetRes, trialBalanceRes, receivableRes, payableRes, stockRes, cashFlowRes, monthlyRes, monthlyBsRes, monthlyCfRes, yearsRes] = await Promise.all([
        api<SummaryReport>(`/tenants/${slug}/reports/summary?${q}`),
        api<ProfitLossReport>(`/tenants/${slug}/reports/profit-loss?${q}`),
        api<BalanceSheetReport>(`/tenants/${slug}/reports/balance-sheet?${q}`),
        api<TrialBalanceReport>(`/tenants/${slug}/reports/trial-balance?${tbq}`),
        api<ReceivableAgingReport>(`/tenants/${slug}/reports/receivable-aging?asOf=${end}`),
        api<PayableAgingReport>(`/tenants/${slug}/reports/payable-aging?asOf=${end}`),
        api<StockValuationReport>(`/tenants/${slug}/reports/stock-valuation?asOf=${end}`),
        api<CashFlowReport>(`/tenants/${slug}/reports/cash-flow?${q}`),
        api<MonthlyProfitLoss>(`/tenants/${slug}/reports/profit-loss-monthly?${q}`),
        api<MonthlyBalanceSheet>(`/tenants/${slug}/reports/balance-sheet-monthly?${q}`),
        api<MonthlyCashFlow>(`/tenants/${slug}/reports/cash-flow-monthly?${q}`),
        api<FiscalYear[]>(`/tenants/${slug}/fiscal-years`),
      ]);
      if (seq !== requestSeq) return;
      summary = summaryRes;
      profitLoss = profitLossRes;
      balanceSheet = balanceSheetRes;
      trialBalance = trialBalanceRes;
      receivableAging = receivableRes;
      payableAging = payableRes;
      stockValuation = stockRes;
      cashFlow = cashFlowRes;
      monthlyProfitLoss = monthlyRes;
      monthlyBalanceSheet = monthlyBsRes;
      monthlyCashFlow = monthlyCfRes;
      fiscalYears = yearsRes;
    } catch (err: any) {
      if (seq === requestSeq) error = err?.message || 'Gagal memuat laporan';
    } finally {
      if (seq === requestSeq) loading = false;
    }
  }

  async function closePeriod() {
    if (!tenantSlug || !selectedPeriod) return;
    if (!confirm(`Tutup ${selectedPeriod.name}? Posting baru di periode ini akan diblokir.`)) return;
    actionLoading = true;
    try {
      await api(`/tenants/${tenantSlug}/periods/${selectedPeriod.id}/close`, { method: 'POST' });
      showToast(`${selectedPeriod.name} berhasil ditutup`, 'success');
      await loadReports(tenantSlug, startDate, endDate, includeClosing);
    } catch (err: any) {
      showToast(err?.message || 'Gagal menutup periode', 'error');
    } finally {
      actionLoading = false;
    }
  }

  async function reopenPeriod() {
    if (!tenantSlug || !selectedPeriod) return;
    if (!confirm(`Buka kembali ${selectedPeriod.name}? Jurnal penutup akan direversal.`)) return;
    actionLoading = true;
    try {
      await api(`/tenants/${tenantSlug}/periods/${selectedPeriod.id}/reopen`, { method: 'POST' });
      showToast(`${selectedPeriod.name} berhasil dibuka kembali`, 'success');
      await loadReports(tenantSlug, startDate, endDate, includeClosing);
    } catch (err: any) {
      showToast(err?.message || 'Gagal membuka periode', 'error');
    } finally {
      actionLoading = false;
    }
  }

  $effect(() => {
    const now = new Date();
    const end = now.toISOString().slice(0, 10);
    const start = new Date(now.getTime() - 30 * 86400000).toISOString().slice(0, 10);
    if (!startDate) {
      startDate = start;
      endDate = end;
    }
  });

  $effect(() => {
    if (tenantSlug && startDate && endDate) {
      void loadReports(tenantSlug, startDate, endDate, includeClosing);
    }
  });
</script>

<PageHeader title="Laporan Keuangan" description="Trial balance, closing period, aging, dan valuasi stok dari GL live">
  {#snippet actions()}
    <select
      bind:value={exportKind}
      class="input-field w-44"
      aria-label="Jenis laporan untuk ekspor"
    >
      {#each exportKinds as kind}
        <option value={kind.value}>{kind.label}</option>
      {/each}
    </select>
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button variant="secondary" onclick={() => tenantSlug && loadReports(tenantSlug, startDate, endDate, includeClosing)} loading={loading}>
      <RefreshCw class="w-4 h-4" /> Refresh
    </Button>
  {/snippet}
</PageHeader>

<div class="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
  <DateRangeFilter onChange={onRangeChange} />
  <div class="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3">
    <div class="flex flex-wrap items-center gap-3">
      <div>
        <p class="text-xs text-[hsl(var(--muted-foreground))]">Periode akuntansi</p>
        <p class="font-semibold">{selectedPeriod?.name ?? 'Tidak ditemukan'}</p>
      </div>
      {#if selectedPeriod}
        <span class="rounded-full px-2.5 py-1 text-xs font-medium" class:bg-emerald-100={selectedPeriod.status === 'open'} class:text-emerald-700={selectedPeriod.status === 'open'} class:bg-amber-100={selectedPeriod.status !== 'open'} class:text-amber-700={selectedPeriod.status !== 'open'}>
          {selectedPeriod.status}
        </span>
        {#if !isOwner}
          <span class="text-xs text-[hsl(var(--muted-foreground))]">Read-only</span>
        {:else if selectedPeriod.status === 'open'}
          <Button size="sm" onclick={closePeriod} loading={actionLoading}>Tutup Periode</Button>
        {:else if selectedPeriod.status === 'closed'}
          <Button size="sm" variant="secondary" onclick={reopenPeriod} loading={actionLoading}>Buka Kembali</Button>
        {:else}
          <span class="text-xs text-[hsl(var(--muted-foreground))]">Periode terkunci</span>
        {/if}
      {/if}
    </div>
  </div>
</div>

{#if error}
  <div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={totalIncome} loading={loading} format="currency" />
  <MetricCard label="Beban" value={totalExpense} loading={loading} format="currency" />
  <MetricCard label="Laba Bersih" value={netProfit} loading={loading} format="currency" />
  <MetricCard label="Piutang Outstanding" value={arOutstanding} loading={loading} format="currency" />
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Aset" value={totalAssets} loading={loading} format="currency" />
  <MetricCard label="Kewajiban + Ekuitas" value={liabilitiesPlusEquity} loading={loading} format="currency" />
  <MetricCard label="Selisih Neraca" value={balanceGap} loading={loading} format="currency" />
  <MetricCard label="Delta Stok vs GL" value={stockGlDelta} loading={loading} format="currency" />
</div>

<div class="mb-6 flex gap-2 overflow-x-auto border-b border-[hsl(var(--border))]">
  {#each tabs as tab}
    <button
      class="whitespace-nowrap border-b-2 px-3 py-2 text-sm font-medium transition-colors"
      class:border-[hsl(var(--primary))]={activeTab === tab.id}
      class:text-[hsl(var(--primary))]={activeTab === tab.id}
      class:border-transparent={activeTab !== tab.id}
      class:text-[hsl(var(--muted-foreground))]={activeTab !== tab.id}
      onclick={() => activeTab = tab.id}
    >
      {tab.label}
    </button>
  {/each}
</div>

{#if activeTab === 'summary'}
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="card p-5 lg:col-span-2">
      <h3 class="mb-4 font-semibold">Pendapatan vs Beban Harian</h3>
      <BarChart labels={summaryChart().labels} datasets={[
        { label: 'Pendapatan', data: summaryChart().income, color: '#059669' },
        { label: 'Beban', data: summaryChart().expense, color: '#dc2626' },
      ]} height={260} yFormat="currency" />
    </div>
    <div class="card p-5">
      <h3 class="mb-4 font-semibold">Beban Terbesar</h3>
      <div class="space-y-3">
        {#each (summary?.composition ?? []).slice(0, 8) as item}
          <div class="flex items-center justify-between gap-3 text-sm">
            <span class="truncate">{item.name}</span>
            <span class="font-medium tabular-nums">{money(item.amount)}</span>
          </div>
        {:else}
          <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada beban pada periode ini.</p>
        {/each}
      </div>
    </div>
  </div>
{:else if activeTab === 'trial'}
  <div class="mb-3 flex items-center justify-between gap-3">
    <label class="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
      <input type="checkbox" bind:checked={includeClosing} />
      Sertakan jurnal penutup CLS/REV-CLS
    </label>
    <span class="text-sm" class:text-emerald-600={trialBalance?.summary.balanced} class:text-red-600={!trialBalance?.summary.balanced}>
      {trialBalance?.summary.balanced ? 'Balanced' : 'Tidak balanced'} · Dr {money(trialBalance?.summary.totalDebit)} / Cr {money(trialBalance?.summary.totalCredit)}
    </span>
  </div>
  <DataTable
    columns={[
      { key: 'code', label: 'Kode', sortable: true },
      { key: 'name', label: 'Akun', sortable: true },
      { key: 'openingBalance', label: 'Saldo Awal', align: 'right', render: (r: any) => money(r.openingBalance) },
      { key: 'periodDebit', label: 'Debit Periode', align: 'right', render: (r: any) => money(r.periodDebit) },
      { key: 'periodCredit', label: 'Kredit Periode', align: 'right', render: (r: any) => money(r.periodCredit) },
      { key: 'debit', label: 'Debit Akhir', align: 'right', render: (r: any) => money(r.debit) },
      { key: 'credit', label: 'Kredit Akhir', align: 'right', render: (r: any) => money(r.credit) },
    ]}
    data={trialBalance?.rows ?? []}
    total={trialBalance?.rows.length ?? 0}
    pageSize={12}
    loading={loading}
    searchable={true}
  />
{:else if activeTab === 'profit-loss'}
  <div class="card p-5 mb-4">
    <h3 class="mb-4 font-semibold">Laba Rugi per Bulan</h3>
    {#if (monthlyProfitLoss?.rows ?? []).length > 0}
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th class="pb-2 pr-4 font-medium">Bulan</th>
              <th class="pb-2 pr-4 text-right font-medium">Pendapatan</th>
              <th class="pb-2 pr-4 text-right font-medium">Beban</th>
              <th class="pb-2 pr-4 text-right font-medium">Laba Bersih</th>
              <th class="pb-2 text-right font-medium">Δ Laba vs Bulan Lalu</th>
            </tr>
          </thead>
          <tbody>
            {#each monthlyProfitLoss?.rows ?? [] as row, i (row.month)}
              {@const prev = (monthlyProfitLoss?.rows ?? [])[i - 1]}
              <tr class="border-b border-[hsl(var(--border))] last:border-0">
                <td class="py-2 pr-4">{monthName(row.month)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.income)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.expense)}</td>
                <td class="py-2 pr-4 text-right font-semibold tabular-nums" class:text-emerald-600={toNumber(row.profit) >= 0} class:text-red-600={toNumber(row.profit) < 0}>{money(row.profit)}</td>
                <td class="py-2 text-right text-xs tabular-nums" class:text-emerald-600={deltaTone(prev ? toNumber(prev.profit) : undefined, toNumber(row.profit)) === 'up'} class:text-red-600={deltaTone(prev ? toNumber(prev.profit) : undefined, toNumber(row.profit)) === 'down'}>{deltaLabel(prev ? toNumber(prev.profit) : undefined, toNumber(row.profit))}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada jurnal pada rentang ini.</p>
    {/if}
  </div>
  <DataTable
    columns={[
      { key: 'code', label: 'Kode', sortable: true },
      { key: 'name', label: 'Akun', sortable: true },
      { key: 'type', label: 'Tipe' },
      { key: 'debitTotal', label: 'Debit', align: 'right', render: (r: any) => money(r.debitTotal) },
      { key: 'creditTotal', label: 'Kredit', align: 'right', render: (r: any) => money(r.creditTotal) },
      { key: 'net', label: 'Net', align: 'right', render: (r: any) => money(r.net) },
    ]}
    data={profitLoss?.rows ?? []}
    total={profitLoss?.rows.length ?? 0}
    pageSize={12}
    loading={loading}
    searchable={true}
  />
{:else if activeTab === 'balance-sheet'}
  <div class="card p-5 mb-4">
    <h3 class="mb-4 font-semibold">Neraca per Bulan</h3>
    {#if (monthlyBalanceSheet?.rows ?? []).length > 0}
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th class="pb-2 pr-4 font-medium">Bulan</th>
              <th class="pb-2 pr-4 text-right font-medium">Total Aset</th>
              <th class="pb-2 pr-4 text-right font-medium">Kewajiban</th>
              <th class="pb-2 pr-4 text-right font-medium">Ekuitas</th>
              <th class="pb-2 pr-4 text-right font-medium">Kewajiban + Ekuitas</th>
              <th class="pb-2 text-right font-medium">Δ Aset vs Bulan Lalu</th>
            </tr>
          </thead>
          <tbody>
            {#each monthlyBalanceSheet?.rows ?? [] as row, i (row.month)}
              {@const prev = (monthlyBalanceSheet?.rows ?? [])[i - 1]}
              <tr class="border-b border-[hsl(var(--border))] last:border-0">
                <td class="py-2 pr-4">{monthName(row.month)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.assets)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.liabilities)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.equity)}</td>
                <td class="py-2 pr-4 text-right font-semibold tabular-nums">{money(row.liabilitiesPlusEquity)}</td>
                <td class="py-2 text-right text-xs tabular-nums" class:text-emerald-600={deltaTone(prev ? toNumber(prev.assets) : undefined, toNumber(row.assets)) === 'up'} class:text-red-600={deltaTone(prev ? toNumber(prev.assets) : undefined, toNumber(row.assets)) === 'down'}>{deltaLabel(prev ? toNumber(prev.assets) : undefined, toNumber(row.assets))}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada jurnal pada rentang ini.</p>
    {/if}
  </div>
  <DataTable
    columns={[
      { key: 'code', label: 'Kode', sortable: true },
      { key: 'name', label: 'Akun', sortable: true },
      { key: 'type', label: 'Tipe' },
      { key: 'balance', label: 'Saldo', align: 'right', render: (r: any) => money(r.balance) },
    ]}
    data={balanceSheet?.rows ?? []}
    total={balanceSheet?.rows.length ?? 0}
    pageSize={12}
    loading={loading}
    searchable={true}
  />
{:else if activeTab === 'cash-flow'}
  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
    <MetricCard label="Arus Kas Operasi" value={cashOperating} loading={loading} format="currency" />
    <MetricCard label="Arus Kas Investasi" value={cashInvesting} loading={loading} format="currency" />
    <MetricCard label="Arus Kas Pendanaan" value={cashFinancing} loading={loading} format="currency" />
    <MetricCard label="Net Arus Kas" value={cashNet} loading={loading} format="currency" />
  </div>
  <div class="card p-5 mb-4">
    <h3 class="mb-4 font-semibold">Arus Kas per Bulan</h3>
    {#if (monthlyCashFlow?.rows ?? []).length > 0}
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th class="pb-2 pr-4 font-medium">Bulan</th>
              <th class="pb-2 pr-4 text-right font-medium">Operasi</th>
              <th class="pb-2 pr-4 text-right font-medium">Investasi</th>
              <th class="pb-2 pr-4 text-right font-medium">Pendanaan</th>
              <th class="pb-2 pr-4 text-right font-medium">Net</th>
              <th class="pb-2 text-right font-medium">Δ Net vs Bulan Lalu</th>
            </tr>
          </thead>
          <tbody>
            {#each monthlyCashFlow?.rows ?? [] as row, i (row.month)}
              {@const prev = (monthlyCashFlow?.rows ?? [])[i - 1]}
              <tr class="border-b border-[hsl(var(--border))] last:border-0">
                <td class="py-2 pr-4">{monthName(row.month)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.operating)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.investing)}</td>
                <td class="py-2 pr-4 text-right tabular-nums">{money(row.financing)}</td>
                <td class="py-2 pr-4 text-right font-semibold tabular-nums" class:text-emerald-600={toNumber(row.net) >= 0} class:text-red-600={toNumber(row.net) < 0}>{money(row.net)}</td>
                <td class="py-2 text-right text-xs tabular-nums" class:text-emerald-600={deltaTone(prev ? toNumber(prev.net) : undefined, toNumber(row.net)) === 'up'} class:text-red-600={deltaTone(prev ? toNumber(prev.net) : undefined, toNumber(row.net)) === 'down'}>{deltaLabel(prev ? toNumber(prev.net) : undefined, toNumber(row.net))}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada jurnal pada rentang ini.</p>
    {/if}
  </div>
  <div class="card p-5 mb-4">
    <div class="flex flex-wrap items-center gap-2 text-xs">
      {#each [
        { key: 'operating', label: 'Operasi' },
        { key: 'investing', label: 'Investasi' },
        { key: 'financing', label: 'Pendanaan' },
      ] as cat}
        <span class="rounded-full px-2.5 py-1 font-medium" class:bg-emerald-100={cat.key === 'operating'} class:text-emerald-700={cat.key === 'operating'} class:bg-sky-100={cat.key === 'investing'} class:text-sky-700={cat.key === 'investing'} class:bg-violet-100={cat.key === 'financing'} class:text-violet-700={cat.key === 'financing'}>
          {cat.label}
        </span>
      {/each}
    </div>
  </div>
  <DataTable
    columns={[
      { key: 'date', label: 'Tanggal', sortable: true },
      { key: 'description', label: 'Deskripsi', sortable: true },
      { key: 'accountName', label: 'Akun Kas', sortable: true },
      { key: 'type', label: 'Kategori', render: (r: any) => r.type },
      { key: 'inflow', label: 'Masuk', align: 'right', render: (r: any) => (toNumber(r.inflow) > 0 ? money(r.inflow) : '-') },
      { key: 'outflow', label: 'Keluar', align: 'right', render: (r: any) => (toNumber(r.outflow) > 0 ? money(r.outflow) : '-') },
    ]}
    data={cashFlow?.rows ?? []}
    total={cashFlow?.rows.length ?? 0}
    pageSize={12}
    loading={loading}
    searchable={true}
  />
{:else if activeTab === 'aging'}
  <div class="grid gap-6 lg:grid-cols-2">
    <div class="card p-5">
      <h3 class="mb-4 font-semibold">Piutang per Bucket</h3>
      <div class="space-y-3">
        {#each Object.entries(receivableAging?.buckets ?? {}) as [bucket, data]}
          <div class="flex items-center justify-between rounded-md border border-[hsl(var(--border))] px-3 py-2 text-sm">
            <span class="capitalize">{bucket}</span>
            <span class="font-medium tabular-nums">{money(data.total)} · {data.items.length} invoice</span>
          </div>
        {/each}
      </div>
    </div>
    <div>
      <DataTable
        columns={[
          { key: 'supplierName', label: 'Supplier', sortable: true },
          { key: 'received', label: 'Diterima', align: 'right', render: (r: any) => money(r.received) },
          { key: 'paid', label: 'Dibayar', align: 'right', render: (r: any) => money(r.paid) },
          { key: 'outstanding', label: 'Outstanding', align: 'right', render: (r: any) => money(r.outstanding) },
          { key: 'bucket', label: 'Bucket' },
        ]}
        data={payableAging?.rows ?? []}
        total={payableAging?.rows.length ?? 0}
        loading={loading}
        searchable={true}
      />
    </div>
  </div>
{:else if activeTab === 'stock'}
  <DataTable
    columns={[
      { key: 'sku', label: 'SKU', sortable: true },
      { key: 'productName', label: 'Produk', sortable: true },
      { key: 'quantity', label: 'Qty', align: 'right', render: (r: any) => formatNumber(toNumber(r.quantity)) },
      { key: 'averageCost', label: 'Avg Cost', align: 'right', render: (r: any) => money(r.averageCost) },
      { key: 'value', label: 'Nilai', align: 'right', render: (r: any) => money(r.value) },
    ]}
    data={stockValuation?.rows ?? []}
    total={stockValuation?.rows.length ?? 0}
    pageSize={12}
    loading={loading}
    searchable={true}
  />
{/if}

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title={`Laporan Keuangan — ${exportKinds.find((k) => k.value === exportKind)?.label}`}
  subtitle={`Periode ${startDate} s/d ${endDate}`}
  columns={exportColumns}
  rows={exportRows}
  filename={`laporan-${exportKind}`}
/>
