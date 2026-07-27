<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { invoices, createInvoice, updateInvoice, deleteInvoice } from '$lib/stores/data';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ number: '', customerName: '', date: '', items: 0, total: 0, status: 'pending' });

  function openCreate() {
    form = { number: '', customerName: '', date: '', items: 0, total: 0, status: 'pending' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $invoices[i];
    form = { number: item.number, customerName: item.customerName, date: item.date, items: 0, total: item.total, status: item.status };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    const data = { number: form.number, customerName: form.customerName, date: form.date, total: form.total, status: form.status };
    if (editingIndex !== null) {
      updateInvoice($invoices[editingIndex].id, data);
    } else {
      createInvoice(data);
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

<PageHeader title="Pesanan Pembelian" description="Purchase order" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pesanan' }]}>
  {#snippet actions()}
    <Button onclick={openCreate}>+ PO Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'number', label: 'No. PO', sortable: true },
    { key: 'customerName', label: 'Pemasok', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'items', label: 'Item', align: 'right' },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$invoices}
  total={18}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit PO' : 'PO Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">No. PO</label>
        <input type="text" bind:value={form.number} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="pending">Pending</option>
          <option value="received">Received</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>
    <div>
      <label class="label-text">Pemasok</label>
      <input type="text" bind:value={form.customerName} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Tanggal</label>
        <input type="date" bind:value={form.date} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Jumlah Item</label>
        <input type="number" bind:value={form.items} class="input-field mt-1" required />
      </div>
    </div>
    <div>
      <label class="label-text">Total (Rp)</label>
        <CurrencyInput value={form.total} onchange={(v) => form.total = v} class="input-field mt-1" required />
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
  message="Hapus purchase order ini? Tindakan ini tidak dapat dibatalkan."
/>
