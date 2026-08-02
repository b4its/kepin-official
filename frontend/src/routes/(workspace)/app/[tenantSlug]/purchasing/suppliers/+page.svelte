<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { suppliers, createSupplier, updateSupplier, deleteSupplier } from '$lib/stores/data';
  import { getSupplierStatement } from '$lib/api/tenants';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Download } from '@lucide/svelte';

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let showStatement = $state(false);
  let statementSupplier = $state<{ id: string; code: string; name: string } | null>(null);
  let statement = $state<{
    opening: string;
    closing: string;
    items: { id: string; date: string; reference: string; description: string; debit: string; credit: string; balance: string }[];
  } | null>(null);
  let statementLoading = $state(false);
  let statementStart = $state('');
  let statementEnd = $state('');

  let form = $state({ code: '', name: '', email: '', phone: '', address: '' });

  const slug = $derived($page.params.tenantSlug || '');

  const exportColumns = [
    { key: 'code', label: 'Kode' },
    { key: 'name', label: 'Nama' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Kota' },
    { key: 'createdAt', label: 'Bergabung' },
  ];

  function openCreate() {
    form = { code: '', name: '', email: '', phone: '', address: '' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $suppliers[i];
    form = { code: item.code || '', name: item.name, email: item.email, phone: item.phone, address: item.address };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = { code: form.code, name: form.name, email: form.email, phone: form.phone, address: form.address };
    if (editingIndex !== null) {
      await updateSupplier($suppliers[editingIndex].id, data);
      showToast('Pemasok berhasil diperbarui', 'success');
    } else {
      await createSupplier(data);
      showToast('Pemasok berhasil ditambahkan', 'success');
    }
    showModal = false;
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteSupplier($suppliers[deleteIndex].id);
      deleteIndex = null;
      showToast('Pemasok berhasil dihapus', 'success');
    }
  }

  async function openStatement(item: { id: string; code: string; name: string }) {
    statementSupplier = { id: item.id, code: item.code, name: item.name };
    statement = null;
    statementStart = '';
    statementEnd = '';
    showStatement = true;
    await loadStatement();
  }

  async function loadStatement() {
    if (!statementSupplier?.id) return;
    statementLoading = true;
    try {
      const params = [];
      if (statementStart) params.push(`&startDate=${statementStart}`);
      if (statementEnd) params.push(`&endDate=${statementEnd}`);
      statement = await getSupplierStatement(slug, statementSupplier.id, params.join('')) as unknown as typeof statement;
    } catch (e) {
      showToast('Gagal memuat kartu hutang', 'error');
    } finally {
      statementLoading = false;
    }
  }
</script>

<PageHeader title="Pemasok" description="Daftar pemasok" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pemasok' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Pemasok Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'code', label: 'Kode', sortable: true },
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Kota' },
    { key: 'createdAt', label: 'Bergabung' },
  ]}
  data={$suppliers}
  total={$suppliers.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openStatement(item)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Statement</button>
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Pemasok' : 'Pemasok Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Kode</label>
      <input type="text" bind:value={form.code} class="input-field mt-1" placeholder="cth: SUP-001" required />
    </div>
    <div>
      <label class="label-text">Nama</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Email</label>
        <input type="email" bind:value={form.email} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Telepon</label>
        <input type="text" bind:value={form.phone} class="input-field mt-1" required />
      </div>
    </div>
    <div>
      <label class="label-text">Kota</label>
      <input type="text" bind:value={form.address} class="input-field mt-1" />
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit">Simpan</Button>
    </div>
  </form>
</Modal>

<ConfirmDialog
  open={deleteIndex !== null}
  onclose={() => deleteIndex = null}
  onconfirm={confirmDelete}
  message="Hapus pemasok ini? Tindakan ini tidak dapat dibatalkan."
/>

<Modal
  title={statementSupplier ? `Kartu Hutang · ${statementSupplier.code} ${statementSupplier.name}` : 'Kartu Hutang'}
  open={showStatement}
  onclose={() => showStatement = false}
>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-2 text-sm">
      <span>Periode:</span>
      <input type="date" bind:value={statementStart} class="input-field w-40" aria-label="Tanggal mulai kartu hutang" />
      <span>s.d.</span>
      <input type="date" bind:value={statementEnd} class="input-field w-40" aria-label="Tanggal akhir kartu hutang" />
      <Button size="sm" variant="secondary" onclick={loadStatement} loading={statementLoading}>Terapkan</Button>
    </div>
    {#if statement}
      <p class="text-xs text-[hsl(var(--muted-foreground))]">
        Saldo awal {formatIDR(Number(statement.opening))} · Saldo akhir {formatIDR(Number(statement.closing))}
      </p>
      <div class="max-h-96 overflow-auto rounded border border-[hsl(var(--border))]">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-[hsl(var(--card))]">
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th class="px-4 py-2">Tanggal</th>
              <th class="px-4 py-2">No. Referensi</th>
              <th class="px-4 py-2">Deskripsi</th>
              <th class="px-4 py-2 text-right">Debit</th>
              <th class="px-4 py-2 text-right">Kredit</th>
              <th class="px-4 py-2 text-right">Saldo</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-[hsl(var(--border))]">
              <td class="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]" colspan="5">Saldo awal</td>
              <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(statement.opening))}</td>
            </tr>
            {#if statement.items.length === 0}
              <tr class="border-b border-[hsl(var(--border))]">
                <td class="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]" colspan="6">Tidak ada mutasi pada periode ini</td>
              </tr>
            {/if}
            {#each statement.items as line}
              <tr class="border-b border-[hsl(var(--border))]">
                <td class="px-4 py-2">{line.date}</td>
                <td class="px-4 py-2 font-mono text-xs">{line.reference}</td>
                <td class="px-4 py-2 text-[hsl(var(--muted-foreground))]">{line.description}</td>
                <td class="px-4 py-2 text-right tabular-nums">{Number(line.debit) !== 0 ? formatIDR(Number(line.debit)) : ''}</td>
                <td class="px-4 py-2 text-right tabular-nums">{Number(line.credit) !== 0 ? formatIDR(Number(line.credit)) : ''}</td>
                <td class="px-4 py-2 text-right font-medium tabular-nums">{formatIDR(Number(line.balance))}</td>
              </tr>
            {/each}
            <tr>
              <td class="px-4 py-2 font-semibold" colspan="5">Saldo akhir</td>
              <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(statement.closing))}</td>
            </tr>
          </tbody>
        </table>
      </div>
    {:else if statementLoading}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat kartu hutang…</p>
    {/if}
  </div>
</Modal>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Daftar Pemasok"
  subtitle="Data pemasok aktif"
  columns={exportColumns}
  rows={$suppliers}
  filename="pemasok"
/>
