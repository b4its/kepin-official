<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { CreditCard } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';

  const invoices = [
    { period: 'Juli 2026', amount: 499000, status: 'paid', date: '1 Jul 2026' },
    { period: 'Juni 2026', amount: 499000, status: 'paid', date: '1 Jun 2026' },
    { period: 'Mei 2026', amount: 499000, status: 'paid', date: '1 Mei 2026' },
    { period: 'April 2026', amount: 499000, status: 'paid', date: '1 Apr 2026' },
  ];
</script>

<PageHeader title="Billing" description="Langganan dan tagihan" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Billing' }]} />

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6 max-w-lg">
  <MetricCard label="Paket" value={0} format="number" />
  <MetricCard label="Tagihan Bulan Ini" value={499000} format="currency" />
  <MetricCard label="Pengguna Terpakai" value={3} format="number" unit="/5" />
</div>

<div class="card p-5 max-w-lg">
  <div class="flex items-center justify-between mb-4">
    <div>
      <h3 class="font-semibold">Paket Premium</h3>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Rp 499.000/bulan · Perpanjangan otomatis</p>
    </div>
    <Button variant="secondary" size="sm">Ubah Paket</Button>
  </div>
  <div class="border-t border-[hsl(var(--border))] pt-4">
    <div class="flex items-center justify-between text-sm mb-1">
      <span class="text-[hsl(var(--muted-foreground))]">Promo Early Adopter 50%</span>
      <span class="font-medium">-Rp 499.000</span>
    </div>
    <div class="flex items-center justify-between text-sm">
      <span class="text-[hsl(var(--muted-foreground))]">Tagihan Efektif</span>
      <span class="font-bold">Rp 499.000/bulan</span>
    </div>
  </div>
</div>

<div class="mt-6">
  <h3 class="font-semibold mb-3">Riwayat Tagihan</h3>
  {#each invoices as inv}
    <div class="flex items-center justify-between py-2 border-b border-[hsl(var(--border))] last:border-0 text-sm">
      <span>{inv.period}</span>
      <span class="tabular-nums">Rp {inv.amount.toLocaleString('id-ID')}</span>
      <span class="badge-success">{inv.status}</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">{inv.date}</span>
    </div>
  {/each}
</div>
