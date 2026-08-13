<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { page } from '$app/stores';
  import { accounts, currentRole, transactions, createTransaction, updateTransaction, deleteTransaction, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let totalPemasukan = $derived($transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  let totalPengeluaran = $derived($transactions.filter(t => t.type === 'expense').reduce((s, t) => s + Math.abs(t.amount), 0));
  let rataRataHarian = $derived($transactions.length > 0 ? Math.round(($transactions.reduce((s, t) => s + t.amount, 0)) / Math.max(1, new Set($transactions.map(t => t.date)).size)) : 0);
  let transaksiBulanIni = $derived($transactions.filter(t => new Date(t.date).getMonth() === new Date().getMonth() && new Date(t.date).getFullYear() === new Date().getFullYear()).length);

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  let form = $state({ date: '', description: '', accountId: '', counterAccountId: '', type: 'income', amount: 0, status: 'draft' });

  function openCreate() {
    form = { date: new Date().toISOString().slice(0, 10), description: '', accountId: '', counterAccountId: '', type: 'income', amount: 0, status: 'draft' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $transactions[i];
    form = { date: item.date, description: item.description, accountId: item.accountId, counterAccountId: item.counterAccountId || '', type: item.type, amount: item.amount, status: item.status };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const payload = {
      transactionDate: form.date,
      type: form.type,
      description: form.description,
      amount: String(form.amount || '0'),
      accountId: form.accountId,
      counterAccountId: form.counterAccountId || null,
    };
    try {
      if (editingIndex !== null) {
        await updateTransaction($transactions[editingIndex].id, payload);
        showToast('Transaksi berhasil diperbarui', 'success');
      } else {
        await createTransaction(payload);
        showToast('Transaksi draft berhasil ditambahkan', 'success');
      }
      showModal = false;
    } catch (err: any) { showToast(err?.message || 'Gagal menyimpan transaksi', 'error'); }
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      try { await deleteTransaction($transactions[deleteIndex].id); showToast('Transaksi berhasil dihapus', 'success'); }
      catch (err: any) { showToast(err?.message || 'Gagal menghapus transaksi', 'error'); }
      finally { deleteIndex = null; }
    }
  }

  async function post(item: any) {
    if (!slug || !isOwner) return;
    try { await tenantApi.postTransaction(slug, item.id); showToast('Transaksi berhasil diposting', 'success'); window.location.reload(); }
    catch (err: any) { showToast(err?.message || 'Gagal memposting transaksi', 'error'); }
  }

  async function voidTransaction(item: any) {
    if (!slug || !isOwner || !confirm('Void transaksi posted ini?')) return;
    try { await tenantApi.voidTransaction(slug, item.id); showToast('Transaksi berhasil di-void', 'success'); window.location.reload(); }
    catch (err: any) { showToast(err?.message || 'Gagal void transaksi', 'error'); }
  }
</script>

<PageHeader title="Transaksi" description="Catatan transaksi keuangan">
  {#snippet actions()}
    {#if isOwner}<Button onclick={openCreate}>+ Transaksi Baru</Button>{/if}
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Pemasukan" value={totalPemasukan} format="currency" />
  <MetricCard label="Total Pengeluaran" value={totalPengeluaran} format="currency" />
  <MetricCard label="Rata-rata Harian" value={rataRataHarian} format="currency" />
  <MetricCard label="Transaksi Bulan Ini" value={transaksiBulanIni} format="number" />
</div>

<DataTable
  tourHook="transactions-table"
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'description', label: 'Deskripsi', sortable: true },
     { key: 'accountId', label: 'Akun', render: (item: any) => $accounts.find(a => a.id === item.accountId)?.name || item.accountId },
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
    {#if isOwner && item.status === 'draft'}<button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button><button onclick={() => post(item)} class="text-xs text-[var(--color-kepin-green)] hover:underline mr-2">Post</button><button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>{/if}
    {#if isOwner && item.status === 'posted'}<button onclick={() => voidTransaction(item)} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Void</button>{/if}
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Transaksi' : 'Transaksi Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text" for="transaction-date">Tanggal</label>
      <input id="transaction-date" type="date" bind:value={form.date} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="transaction-description">Deskripsi</label>
      <input id="transaction-description" type="text" bind:value={form.description} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="transaction-account">Akun Pendapatan/Beban</label>
      <select id="transaction-account" bind:value={form.accountId} class="input-field mt-1" required><option value="">Pilih akun</option>{#each $accounts.filter(a => a.status === 'active' && (form.type === 'income' ? a.type === 'income' : a.type === 'expense')) as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}</select>
    </div>
    <div><label class="label-text" for="transaction-counter">Akun Lawan (Kas/Bank)</label><select id="transaction-counter" bind:value={form.counterAccountId} class="input-field mt-1" required><option value="">Pilih akun lawan</option>{#each $accounts.filter(a => a.status === 'active' && a.type === 'asset') as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}</select></div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="transaction-type">Tipe</label>
        <select id="transaction-type" bind:value={form.type} class="input-field mt-1">
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
