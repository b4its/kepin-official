<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { accounts, createAccount, updateAccount, deleteAccount, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ code: '', name: '', type: 'asset', status: 'active' });
  let balances = $state<Record<string, number>>({});

  const typeLabel = (t: string) => ({ asset: 'Asset', liability: 'Liability', equity: 'Equity', income: 'Income', expense: 'Expense' }[t] || t);

  $effect(() => {
    const list = $accounts;
    if (!list.length) { balances = {}; return; }
    void (async () => {
      const b: Record<string, number> = {};
      await Promise.all(list.map(async (a) => {
        try { const r: any = await tenantApi.getAccountBalance(slug, a.id); b[a.id] = parseFloat(r?.balance || '0'); }
        catch { b[a.id] = 0; }
      }));
      balances = b;
    });
  });

  const exportColumns = [
    { key: 'code', label: 'Kode' },
    { key: 'name', label: 'Nama Akun' },
    { key: 'type', label: 'Tipe', render: (r: any) => typeLabel(r.type) },
    { key: 'status', label: 'Status' },
  ];

  function openCreate() {
    form = { code: '', name: '', type: 'asset', status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $accounts[i];
    form = { code: item.code, name: item.name, type: item.type || 'asset', status: item.status || 'active' };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const normalBalance = ['asset', 'expense'].includes(form.type) ? 'debit' : 'credit';
    const data = { code: form.code, name: form.name, type: form.type, normalBalance };
    if (editingIndex !== null) {
      try {
        await updateAccount($accounts[editingIndex].id, { ...data, status: form.status });
        showToast('Akun berhasil diperbarui', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal memperbarui akun', 'error'); }
    } else {
      try {
        await createAccount(data);
        showToast('Akun berhasil ditambahkan', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal menambahkan akun', 'error'); }
    }
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      try { await deleteAccount($accounts[deleteIndex].id); showToast('Akun berhasil dihapus', 'success'); }
      catch (err: any) { showToast(err?.message || 'Gagal menghapus akun', 'error'); }
      finally { deleteIndex = null; }
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
  tourHook="coa-table"
  columns={[
    { key: 'code', label: 'Kode', sortable: true },
    { key: 'name', label: 'Nama Akun', sortable: true },
    { key: 'type', label: 'Tipe', render: (item: any) => typeLabel(item.type) },
    { key: 'balance', label: 'Saldo', align: 'right', render: (item: any) => `Rp ${(balances[item.id] || 0).toLocaleString('id-ID')}` },
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
          <option value="asset">Asset</option>
          <option value="liability">Liability</option>
          <option value="equity">Equity</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
      </div>
    </div>
    <div>
      <label class="label-text">Nama Akun</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    {#if editingIndex !== null}
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
    {/if}
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
