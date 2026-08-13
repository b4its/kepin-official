<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { currentRole, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { CalendarDays, Lock, LockOpen, Plus, RefreshCw } from '@lucide/svelte';

  type Period = { id: string; name: string; startDate: string; endDate: string; status: string };
  type FiscalYear = { id: string; name: string; startDate: string; endDate: string; status: string; periods: Period[] };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  let years = $state<FiscalYear[]>([]);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let showModal = $state(false);
  let form = $state({ name: '', startDate: '', endDate: '' });

  const statusLabel = (status: string) => ({
    open: 'Terbuka',
    closed: 'Ditutup',
    soft_closed: 'Soft Closed',
    locked: 'Terkunci',
  })[status] ?? status;

  function formatDate(value: string) {
    if (!value) return '-';
    const [y, m, d] = value.slice(0, 10).split('-');
    return `${d}-${m}-${y}`;
  }

  async function loadAll() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      years = (await tenantApi.getFiscalYears(slug)) as FiscalYear[];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat tahun buku';
    } finally {
      loading = false;
    }
  }

  async function saveFiscalYear() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      await tenantApi.createFiscalYear(slug, { name: form.name, startDate: form.startDate, endDate: form.endDate });
      showModal = false;
      form = { name: '', startDate: '', endDate: '' };
      showToast('Tahun buku berhasil dibuat', 'success');
      await loadAll();
    } catch (err: any) {
      showToast(err?.message || 'Gagal membuat tahun buku', 'error');
    } finally {
      saving = false;
    }
  }

  async function togglePeriod(period: Period, target: 'close' | 'reopen') {
    if (!slug || !isOwner) return;
    try {
      if (target === 'close') {
        await tenantApi.closePeriod(slug, period.id);
        showToast(`${period.name} ditutup`, 'success');
      } else {
        await tenantApi.reopenPeriod(slug, period.id);
        showToast(`${period.name} dibuka kembali`, 'success');
      }
      await loadAll();
    } catch (err: any) {
      showToast(err?.message || 'Gagal mengubah periode', 'error');
    }
  }

  async function toggleFiscalYear(year: FiscalYear) {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      if (year.status === 'open') {
        await tenantApi.closeFiscalYear(slug, year.id);
        showToast('Tahun buku ditutup', 'success');
      } else {
        await tenantApi.reopenFiscalYear(slug, year.id);
        showToast('Tahun buku dibuka kembali', 'success');
      }
      await loadAll();
    } catch (err: any) {
      showToast(err?.message || 'Gagal mengubah tahun buku', 'error');
    } finally {
      saving = false;
    }
  }

  $effect(() => { if (slug) void loadAll(); });

  const YEARS_PAGE_SIZE = 10;
  let yearPage = $state(1);
  const yearTotalPages = $derived(Math.max(1, Math.ceil(years.length / YEARS_PAGE_SIZE)));
  const visibleYears = $derived(years.slice((yearPage - 1) * YEARS_PAGE_SIZE, yearPage * YEARS_PAGE_SIZE));

  function setYearPage(p: number) {
    if (p < 1 || p > yearTotalPages) return;
    yearPage = p;
  }
</script>

<PageHeader title="Tahun Buku" description="Kelola tahun buku dan periode akuntansi" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Tahun Buku' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadAll} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}
      <Button onclick={() => showModal = true}><Plus class="w-4 h-4" /> Buat Tahun Buku</Button>
    {/if}
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Tahun buku ditampilkan read-only. Hanya owner yang dapat membuat atau menutup tahun buku.</div>{/if}

<div class="space-y-6">
  {#each visibleYears as year (year.id)}
    <div class="card p-5">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-3">
          <CalendarDays class="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
          <div>
            <h3 class="font-semibold">{year.name}</h3>
            <p class="text-sm text-[hsl(var(--muted-foreground))]">{formatDate(year.startDate)} s/d {formatDate(year.endDate)}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="rounded-full px-3 py-1 text-xs font-medium {year.status === 'open' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}">{statusLabel(year.status)}</span>
          {#if isOwner}
            <Button variant="secondary" onclick={() => toggleFiscalYear(year)} loading={saving}>
              {#if year.status === 'open'}
                <Lock class="w-4 h-4" /> Tutup Tahun Buku
              {:else}
                <LockOpen class="w-4 h-4" /> Buka Kembali
              {/if}
            </Button>
          {/if}
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm" data-tour="fiscal-years-table">
          <thead>
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs uppercase text-[hsl(var(--muted-foreground))]">
              <th class="py-2 pr-4">Periode</th>
              <th class="py-2 pr-4">Rentang</th>
              <th class="py-2 pr-4">Status</th>
              <th class="py-2 text-right">{#if isOwner}Aksi{/if}</th>
            </tr>
          </thead>
          <tbody>
            {#each year.periods as period (period.id)}
              <tr class="border-b border-[hsl(var(--border))] last:border-0">
                <td class="py-2 pr-4 font-medium">{period.name}</td>
                <td class="py-2 pr-4 text-[hsl(var(--muted-foreground))]">{formatDate(period.startDate)} s/d {formatDate(period.endDate)}</td>
                <td class="py-2 pr-4"><span class="rounded-full px-2 py-0.5 text-xs {period.status === 'open' ? 'bg-green-100 text-green-700' : period.status === 'locked' ? 'bg-red-100 text-red-700' : 'bg-zinc-100 text-zinc-600'}">{statusLabel(period.status)}</span></td>
                <td class="py-2 text-right">
                  {#if isOwner}
                    {#if period.status === 'open'}
                      <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => togglePeriod(period, 'close')}>Tutup</button>
                    {:else if period.status !== 'locked'}
                      <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => togglePeriod(period, 'reopen')}>Buka</button>
                    {/if}
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {:else}
    <div class="card p-10 text-center text-sm text-[hsl(var(--muted-foreground))]">Belum ada tahun buku. Buat tahun buku pertama untuk memulai periode akuntansi.</div>
  {/each}
  {#if yearTotalPages > 1}
    <div class="flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
      <span>Menampilkan {visibleYears.length} dari {years.length} tahun buku</span>
      <div class="flex items-center gap-1">
        <button
          class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
          disabled={yearPage <= 1}
          onclick={() => setYearPage(yearPage - 1)}
        >Sebelumnya</button>
        <span class="px-2 tabular-nums">Halaman {yearPage} / {yearTotalPages}</span>
        <button
          class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
          disabled={yearPage >= yearTotalPages}
          onclick={() => setYearPage(yearPage + 1)}
        >Berikutnya</button>
      </div>
    </div>
  {/if}
</div>

<Modal title="Buat Tahun Buku" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={saveFiscalYear} class="space-y-4">
    <div>
      <label class="label-text" for="fy-name">Nama (opsional)</label>
      <input id="fy-name" bind:value={form.name} class="input-field mt-1" placeholder="Tahun Buku 2031" />
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="fy-start">Tanggal Mulai</label>
        <input id="fy-start" type="date" bind:value={form.startDate} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text" for="fy-end">Tanggal Akhir</label>
        <input id="fy-end" type="date" bind:value={form.endDate} class="input-field mt-1" required />
      </div>
    </div>
    <div class="flex justify-end gap-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" loading={saving}>Simpan</Button>
    </div>
  </form>
</Modal>
