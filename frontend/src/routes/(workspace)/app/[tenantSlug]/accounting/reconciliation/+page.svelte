<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { api } from '$lib/api/client';
  import { accounts, currentRole, tenantApi, transactions } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { RefreshCw } from '@lucide/svelte';

  type BankAccount = { id: string; accountId: string; accountName?: string; bankName: string; maskedNumber: string; status: string };
  type BankTransaction = { id: string; bankAccountId: string; externalId: string; transactionDate: string; description: string; amount: string };
  type Match = { id: string; bankTransactionId: string; transactionId: string; confidence: string; status: string; matchedAt?: string | null; note?: string };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  const postedTransactions = $derived($transactions.filter((txn) => txn.status === 'posted'));
  let matches = $state<Match[]>([]);
  let bankAccounts = $state<BankAccount[]>([]);
  let bankTransactions = $state<BankTransaction[]>([]);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let showBankAccount = $state(false);
  let showBankTransaction = $state(false);
  let showMatch = $state(false);
  let accountForm = $state({ accountId: '', bankName: '', maskedNumber: '' });
  let bankTxnForm = $state({ bankAccountId: '', externalId: '', transactionDate: '', description: '', amount: '' });
  let matchForm = $state({ bankTransactionId: '', transactionId: '', confidence: '100', note: '' });

  async function loadAll() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      const [matchRes, accountRes, txnRes] = await Promise.all([
        api(`/tenants/${slug}/reconciliation`),
        tenantApi.getBankAccounts(slug),
        tenantApi.getBankTransactions(slug),
      ]) as any[];
      matches = matchRes.items || [];
      bankAccounts = accountRes || [];
      bankTransactions = txnRes.items || [];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat rekonsiliasi';
    } finally {
      loading = false;
    }
  }

  async function saveBankAccount() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      await tenantApi.createBankAccount(slug, accountForm);
      showBankAccount = false;
      accountForm = { accountId: '', bankName: '', maskedNumber: '' };
      showToast('Rekening bank berhasil ditambahkan', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal menambah rekening bank', 'error'); }
    finally { saving = false; }
  }

  async function saveBankTransaction() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      await tenantApi.createBankTransaction(slug, bankTxnForm);
      showBankTransaction = false;
      bankTxnForm = { bankAccountId: '', externalId: '', transactionDate: '', description: '', amount: '' };
      showToast('Transaksi bank berhasil diimpor', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal mengimpor transaksi bank', 'error'); }
    finally { saving = false; }
  }

  async function saveMatch() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      await tenantApi.createReconciliationMatch(slug, matchForm);
      showMatch = false;
      matchForm = { bankTransactionId: '', transactionId: '', confidence: '100', note: '' };
      showToast('Candidate match berhasil dibuat', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal membuat match', 'error'); }
    finally { saving = false; }
  }

  async function confirmMatch(id: string) {
    if (!slug || !isOwner) return;
    try {
      await tenantApi.confirmReconciliationMatch(slug, id);
      showToast('Match berhasil dikonfirmasi', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal mengonfirmasi match', 'error'); }
  }

  $effect(() => { if (slug) void loadAll(); });
</script>

<PageHeader title="Rekonsiliasi Bank" description="Impor transaksi bank dan cocokkan dengan transaksi posted" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Rekonsiliasi' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={loadAll} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}
      <Button variant="secondary" onclick={() => showBankAccount = true}>+ Rekening Bank</Button>
      <Button variant="secondary" onclick={() => showBankTransaction = true} disabled={bankAccounts.length === 0}>+ Impor Bank Txn</Button>
      <Button onclick={() => showMatch = true} disabled={bankTransactions.length === 0 || postedTransactions.length === 0}>+ Buat Match</Button>
    {/if}
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Rekonsiliasi ditampilkan read-only. Hanya owner yang dapat mengimpor dan mengonfirmasi match.</div>{/if}

<div class="grid gap-6 lg:grid-cols-2 mb-6">
  <div class="card p-5"><h3 class="font-semibold mb-3">Rekening Bank</h3>{#each bankAccounts as bank}<p class="text-sm py-2 border-b border-[hsl(var(--border))]">{bank.bankName} · {bank.maskedNumber || '-'} · {bank.accountName || bank.accountId}</p>{:else}<p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada rekening bank.</p>{/each}</div>
  <div class="card p-5"><h3 class="font-semibold mb-3">Transaksi Bank Terbaru</h3>{#each bankTransactions.slice(0, 5) as txn}<p class="text-sm py-2 border-b border-[hsl(var(--border))]">{txn.transactionDate} · {txn.description} · Rp {Number(txn.amount).toLocaleString('id-ID')}</p>{:else}<p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada transaksi bank yang diimpor.</p>{/each}</div>
</div>

<DataTable columns={[{ key: 'id', label: 'ID' }, { key: 'bankTransactionId', label: 'Bank Txn' }, { key: 'transactionId', label: 'Transaksi' }, { key: 'confidence', label: 'Confidence', align: 'right' }, { key: 'status', label: 'Status' }, { key: 'matchedAt', label: 'Matched At' }, { key: 'note', label: 'Catatan' }]} data={matches} total={matches.length} loading={loading} searchable={true}>
  {#snippet rowActions(item: Match)}
    {#if isOwner && item.status === 'candidate'}<button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => confirmMatch(item.id)}>Konfirmasi</button>{/if}
  {/snippet}
</DataTable>

<Modal title="Tambah Rekening Bank" open={showBankAccount} onclose={() => showBankAccount = false}><form onsubmit={saveBankAccount} class="space-y-4"><div><label class="label-text" for="bank-gl">Akun GL Aset</label><select id="bank-gl" bind:value={accountForm.accountId} class="input-field mt-1" required><option value="">Pilih akun</option>{#each $accounts.filter((a) => a.type === 'asset' && a.status === 'active') as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}</select></div><div><label class="label-text" for="bank-name">Nama Bank</label><input id="bank-name" bind:value={accountForm.bankName} class="input-field mt-1" required /></div><div><label class="label-text" for="bank-number">Nomor Tersamarkan</label><input id="bank-number" bind:value={accountForm.maskedNumber} class="input-field mt-1" placeholder="**** 1234" /></div><div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showBankAccount = false}>Batal</Button><Button type="submit" loading={saving}>Simpan</Button></div></form></Modal>
<Modal title="Impor Transaksi Bank" open={showBankTransaction} onclose={() => showBankTransaction = false}><form onsubmit={saveBankTransaction} class="space-y-4"><div><label class="label-text" for="bank-account">Rekening</label><select id="bank-account" bind:value={bankTxnForm.bankAccountId} class="input-field mt-1" required><option value="">Pilih rekening</option>{#each bankAccounts as bank}<option value={bank.id}>{bank.bankName} · {bank.maskedNumber}</option>{/each}</select></div><div><label class="label-text" for="external-id">External ID</label><input id="external-id" bind:value={bankTxnForm.externalId} class="input-field mt-1" required /></div><div><label class="label-text" for="bank-date">Tanggal</label><input id="bank-date" type="date" bind:value={bankTxnForm.transactionDate} class="input-field mt-1" required /></div><div><label class="label-text" for="bank-amount">Jumlah</label><input id="bank-amount" type="number" bind:value={bankTxnForm.amount} class="input-field mt-1" required /></div><div><label class="label-text" for="bank-description">Deskripsi</label><input id="bank-description" bind:value={bankTxnForm.description} class="input-field mt-1" /></div><div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showBankTransaction = false}>Batal</Button><Button type="submit" loading={saving}>Impor</Button></div></form></Modal>
<Modal title="Buat Candidate Match" open={showMatch} onclose={() => showMatch = false}><form onsubmit={saveMatch} class="space-y-4"><div><label class="label-text" for="match-bank">Transaksi Bank</label><select id="match-bank" bind:value={matchForm.bankTransactionId} class="input-field mt-1" required><option value="">Pilih transaksi bank</option>{#each bankTransactions as txn}<option value={txn.id}>{txn.transactionDate} · {txn.description} · {txn.amount}</option>{/each}</select></div><div><label class="label-text" for="match-internal">Transaksi Internal Posted</label><select id="match-internal" bind:value={matchForm.transactionId} class="input-field mt-1" required><option value="">Pilih transaksi</option>{#each postedTransactions as txn}<option value={txn.id}>{txn.date} · {txn.description} · {txn.amount}</option>{/each}</select></div><div><label class="label-text" for="match-note">Catatan</label><input id="match-note" bind:value={matchForm.note} class="input-field mt-1" /></div><div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showMatch = false}>Batal</Button><Button type="submit" loading={saving}>Buat Match</Button></div></form></Modal>
