<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { accounts, createAccount, updateAccount, deleteAccount } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download } from '@lucide/svelte';

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ code: '', name: '', type: 'Asset', balance: 0, status: 'active' });

  const exportColumns = [
    { key: 'code', label: 'Kode' },
    { key: 'name', label: 'Nama Akun' },
    { key: 'type', label: 'Tipe' },
    { key: 'balance', label: 'Saldo', render: (r: any) => `Rp ${Math.abs(Number(r.balance)).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status' },
  ];

  function openCreate() {
    form = { code: '', name: '', type: 'Asset', balance: 0, status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    form = { ...$accounts[i] };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = { code: form.code, name: form.name, type: form.type.toLowerCase(), balance: String(form.balance), status: form.status };
    if (editingIndex !== null) {
      await updateAccount($accounts[editingIndex].id, data);
      showToast('Akun berhasil diperbarui', 'success');
    } else {
      await createAccount(data);
      showToast('Akun berhasil ditambahkan', 'success');
    }
    showModal = false;
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteAccount($accounts[deleteIndex].id);
      deleteIndex = null;
      showToast('Akun berhasil dihapus', 'success');
    }
  }
</script>

<PageHeader title="Chart of Accounts" description="Daftar akun akuntansi" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Chart of Accounts' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Akun Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'code', label: 'Kode', sortable: true },
    { key: 'name', label: 'Nama Akun', sortable: true },
    { key: 'type', label: 'Tipe' },
    { key: 'balance', label: 'Saldo', align: 'right', render: (item: any) => `Rp ${Math.abs(item.balance).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$accounts}
  total={$accounts.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Akun' : 'Akun Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Kode</label>
        <input type="text" bind:value={form.code} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Tipe</label>
        <select bind:value={form.type} class="input-field mt-1">
          <option value="Asset">Asset</option>
          <option value="Liability">Liability</option>
          <option value="Equity">Equity</option>
          <option value="Income">Income</option>
          <option value="Expense">Expense</option>
        </select>
      </div>
    </div>
    <div>
      <label class="label-text">Nama Akun</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Saldo Awal (Rp)</label>
      <CurrencyInput value={form.balance} onchange={(v) => form.balance = v} class="input-field mt-1" />
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
  message="Hapus akun ini? Tindakan ini tidak dapat dibatalkan."
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Chart of Accounts"
  subtitle="Daftar akun akuntansi"
  columns={exportColumns}
  rows={$accounts}
  filename="chart-of-accounts"
/>
