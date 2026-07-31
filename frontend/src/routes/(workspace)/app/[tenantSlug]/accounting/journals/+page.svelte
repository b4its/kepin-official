<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { accounts, currentRole, journalEntries, loadJournals, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Plus, RefreshCw } from '@lucide/svelte';

  type Line = { accountId: string; description: string; debit: string; credit: string };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  let showExport = $state(false);
  let showModal = $state(false);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let form = $state({ journalDate: '', reference: '', description: '', lines: [] as Line[] });

  const totalDebit = $derived(form.lines.reduce((sum, line) => sum + amount(line.debit), 0));
  const totalCredit = $derived(form.lines.reduce((sum, line) => sum + amount(line.credit), 0));
  const balanced = $derived(form.lines.length >= 2 && totalDebit > 0 && totalDebit === totalCredit);

  const exportColumns = [
    { key: 'date', label: 'Tanggal' },
    { key: 'reference', label: 'Nomor/Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Dibuat' },
  ];

  function amount(value: string) {
    const parsed = Number(value || 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function format(value: number) {
    return `Rp ${value.toLocaleString('id-ID')}`;
  }

  function openCreate() {
    const today = new Date().toISOString().slice(0, 10);
    form = {
      journalDate: today,
      reference: '',
      description: '',
      lines: [
        { accountId: '', description: '', debit: '', credit: '' },
        { accountId: '', description: '', debit: '', credit: '' },
      ],
    };
    showModal = true;
  }

  function addLine() {
    form.lines = [...form.lines, { accountId: '', description: '', debit: '', credit: '' }];
  }

  function removeLine(index: number) {
    if (form.lines.length <= 2) return;
    form.lines = form.lines.filter((_, current) => current !== index);
  }

  async function refresh() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      await loadJournals(slug);
    } catch (err: any) {
      error = err?.message || 'Gagal memuat jurnal';
    } finally {
      loading = false;
    }
  }

  async function saveDraft() {
    if (!slug || !isOwner || !balanced) return;
    saving = true;
    try {
      await tenantApi.createJournal(slug, {
        ...form,
        lines: form.lines.map((line) => ({ ...line, debit: line.debit || '0', credit: line.credit || '0' })),
      });
      showModal = false;
      showToast('Jurnal draft berhasil dibuat', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal membuat jurnal', 'error');
    } finally {
      saving = false;
    }
  }

  async function post(id: string) {
    if (!slug || !isOwner) return;
    try {
      await tenantApi.postJournal(slug, id);
      showToast('Jurnal berhasil diposting ke buku besar', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal memposting jurnal', 'error');
    }
  }

  async function reverse(id: string) {
    if (!slug || !isOwner || !confirm('Reverse jurnal posted ini?')) return;
    try {
      await tenantApi.reverseJournal(slug, id);
      showToast('Jurnal reversal berhasil dibuat', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal melakukan reversal jurnal', 'error');
    }
  }

  $effect(() => { if (slug) void refresh(); });
</script>

<PageHeader title="Jurnal" description="Draft, posting, dan reversal melalui Central Posting Engine" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Jurnal' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true} disabled={Boolean(error) || loading}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button variant="secondary" onclick={refresh} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}<Button onclick={openCreate}><Plus class="w-4 h-4" /> Jurnal Baru</Button>{/if}
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Daftar jurnal bersifat read-only. Hanya owner dapat membuat, posting, atau reverse jurnal.</div>{/if}

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'reference', label: 'Nomor/Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
    { key: 'createdAt', label: 'Dibuat' },
  ]}
  data={$journalEntries}
  total={$journalEntries.length}
  pageSize={10}
  loading={loading}
  searchable={true}
>
  {#snippet rowActions(item: any)}
    {#if isOwner && item.status === 'draft'}<button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => post(item.id)}>Post</button>{/if}
    {#if isOwner && item.status === 'posted'}<button class="ml-2 text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => reverse(item.id)}>Reverse</button>{/if}
  {/snippet}
</DataTable>

<Modal title="Jurnal Baru" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={saveDraft} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4"><div><label class="label-text" for="journal-date">Tanggal</label><input id="journal-date" type="date" bind:value={form.journalDate} class="input-field mt-1" required /></div><div><label class="label-text" for="journal-reference">Referensi</label><input id="journal-reference" bind:value={form.reference} class="input-field mt-1" /></div></div>
    <div><label class="label-text" for="journal-description">Deskripsi</label><input id="journal-description" bind:value={form.description} class="input-field mt-1" required /></div>
    <div class="space-y-2"><div class="flex items-center justify-between"><h3 class="text-sm font-semibold">Baris Jurnal</h3><Button size="sm" variant="secondary" type="button" onclick={addLine}>+ Baris</Button></div>{#each form.lines as line, index}<div class="grid grid-cols-12 gap-2 rounded border border-[hsl(var(--border))] p-2"><select class="input-field col-span-5" bind:value={line.accountId} required><option value="">Pilih akun</option>{#each $accounts.filter((account) => account.status === 'active') as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}</select><input class="input-field col-span-3" bind:value={line.description} placeholder="Deskripsi" /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.debit} placeholder="Debit" /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.credit} placeholder="Kredit" />{#if form.lines.length > 2}<button type="button" class="col-span-12 text-right text-xs text-[var(--color-kepin-danger)]" onclick={() => removeLine(index)}>Hapus baris</button>{/if}</div>{/each}</div>
    <div class="rounded bg-[hsl(var(--muted))] p-3 text-sm flex justify-between"><span>Debit {format(totalDebit)} · Kredit {format(totalCredit)}</span><span class={balanced ? 'text-[var(--color-kepin-green)]' : 'text-[var(--color-kepin-danger)]'}>{balanced ? 'Balanced' : 'Belum balanced'}</span></div>
    <div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button><Button type="submit" loading={saving} disabled={!balanced}>Simpan Draft</Button></div>
  </form>
</Modal>

<ExportModal open={showExport} onclose={() => showExport = false} title="Jurnal Akuntansi" subtitle="Daftar entri jurnal dari backend" columns={exportColumns} rows={$journalEntries} filename="jurnal" />
