<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { invoices, createInvoice, updateInvoice, deleteInvoice } from '$lib/stores/data';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ number: '', customerName: '', date: '', dueDate: '', total: 0, paidAmount: 0, status: 'draft' });

  function openCreate() {
    form = { number: '', customerName: '', date: '', dueDate: '', total: 0, paidAmount: 0, status: 'draft' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $invoices[i];
    form = { number: item.number, customerName: item.customerName, date: item.date, dueDate: item.dueDate, total: item.total, paidAmount: item.paidAmount, status: item.status };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    if (editingIndex !== null) {
      updateInvoice($invoices[editingIndex].id, { ...form });
    } else {
      createInvoice({ ...form });
    }
    showModal = false;
  }

  function confirmDelete() {
    if (deleteIndex !== null) {
      deleteInvoice($invoices[deleteIndex].id);
      deleteIndex = null;
    }
  }
</script>

<PageHeader title="Invoice" description="Manajemen faktur penjualan" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Invoice' }]}>
  {#snippet actions()}
    <Button onclick={openCreate}>+ Invoice Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Piutang" value={13200000} format="currency" />
  <MetricCard label="Jatuh Tempo" value={5200000} format="currency" />
  <MetricCard label="Invoice Bulan Ini" value={12} format="number" />
  <MetricCard label="Rata-rata" value={2800000} format="currency" />
</div>

<DataTable
  columns={[
    { key: 'number', label: 'No. Invoice', sortable: true },
    { key: 'customerName', label: 'Pelanggan', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'dueDate', label: 'Jatuh Tempo' },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$invoices}
  total={48}
  page={1}
  pageSize={5}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Invoice' : 'Invoice Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">No. Invoice</label>
        <input type="text" bind:value={form.number} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="partial">Partial</option>
          <option value="paid">Paid</option>
          <option value="overdue">Overdue</option>
        </select>
      </div>
    </div>
    <div>
      <label class="label-text">Pelanggan</label>
      <input type="text" bind:value={form.customerName} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Tanggal</label>
        <input type="date" bind:value={form.date} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Jatuh Tempo</label>
        <input type="date" bind:value={form.dueDate} class="input-field mt-1" required />
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Total (Rp)</label>
        <CurrencyInput value={form.total} onchange={(v) => form.total = v} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Dibayar (Rp)</label>
        <CurrencyInput value={form.paidAmount} onchange={(v) => form.paidAmount = v} class="input-field mt-1" />
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
  message="Hapus invoice ini? Tindakan ini tidak dapat dibatalkan."
/>
