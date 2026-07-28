<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { transactions, createTransaction, updateTransaction, deleteTransaction } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let totalPemasukan = $derived($transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  let totalPengeluaran = $derived($transactions.filter(t => t.type === 'expense').reduce((s, t) => s + Math.abs(t.amount), 0));
  let rataRataHarian = $derived($transactions.length > 0 ? Math.round(($transactions.reduce((s, t) => s + t.amount, 0)) / Math.max(1, new Set($transactions.map(t => t.date)).size)) : 0);
  let transaksiBulanIni = $derived($transactions.filter(t => new Date(t.date).getMonth() === new Date().getMonth() && new Date(t.date).getFullYear() === new Date().getFullYear()).length);

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ date: '', description: '', accountId: '', type: 'income', amount: 0, status: 'draft' });

  function openCreate() {
    form = { date: '', description: '', accountId: '', type: 'income', amount: 0, status: 'draft' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $transactions[i];
    form = { date: item.date, description: item.description, accountId: item.accountId, type: item.type, amount: item.amount, status: item.status };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    if (editingIndex !== null) {
      await updateTransaction($transactions[editingIndex].id, { ...form });
      showToast('Transaksi berhasil diperbarui', 'success');
    } else {
      await createTransaction({ ...form });
      showToast('Transaksi berhasil ditambahkan', 'success');
    }
    showModal = false;
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteTransaction($transactions[deleteIndex].id);
      deleteIndex = null;
      showToast('Transaksi berhasil dihapus', 'success');
    }
  }
</script>

<PageHeader title="Transaksi" description="Catatan transaksi keuangan">
  {#snippet actions()}
    <Button onclick={openCreate}>+ Transaksi Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Pemasukan" value={totalPemasukan} format="currency" />
  <MetricCard label="Total Pengeluaran" value={totalPengeluaran} format="currency" />
  <MetricCard label="Rata-rata Harian" value={rataRataHarian} format="currency" />
  <MetricCard label="Transaksi Bulan Ini" value={transaksiBulanIni} format="number" />
</div>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'description', label: 'Deskripsi', sortable: true },
    { key: 'accountId', label: 'Akun' },
    { key: 'type', label: 'Tipe', render: (item: any) => item.type === 'income' ? 'Pemasukan' : 'Pengeluaran' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => item.amount > 0 ? `Rp ${item.amount.toLocaleString('id-ID')}` : `(Rp ${Math.abs(item.amount).toLocaleString('id-ID')})` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$transactions}
  total={$transactions.length}
  page={1}
  pageSize={5}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Transaksi' : 'Transaksi Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Tanggal</label>
      <input type="date" bind:value={form.date} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Deskripsi</label>
      <input type="text" bind:value={form.description} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Akun</label>
      <input type="text" bind:value={form.accountId} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Tipe</label>
        <select bind:value={form.type} class="input-field mt-1">
          <option value="income">Pemasukan</option>
          <option value="expense">Pengeluaran</option>
        </select>
      </div>
      <div>
        <label class="label-text">Jumlah (Rp)</label>
        <CurrencyInput value={form.amount} onchange={(v) => form.amount = v} class="input-field mt-1" required />
      </div>
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
  message="Hapus transaksi ini? Tindakan ini tidak dapat dibatalkan."
/>
