<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { api } from '$lib/api/client';
  import { accounts, currentRole, tenantApi, transactions } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Pencil, RefreshCw, Trash2 } from '@lucide/svelte';

  type BankAccount = { id: string; accountId: string; accountName?: string; bankName: string; maskedNumber: string; status: string; glBalance?: string; statementCount?: number; statementTotal?: string; unmatchedCount?: number; unmatchedTotal?: string };
  type BankTransaction = { id: string; bankAccountId: string; externalId: string; transactionDate: string; description: string; amount: string; matched?: boolean };
  type Match = { id: string; bankTransactionId: string; transactionId: string; confidence: string; status: string; matchedAt?: string | null; note?: string };
  type MatchCandidate = { id: string; transactionNumber: string; transactionDate: string; description: string; amount: string; score: number };
  type Suggestion = { bankTransaction: BankTransaction; candidates: MatchCandidate[] };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  const postedTransactions = $derived($transactions.filter((txn) => txn.status === 'posted'));
  let matches = $state<Match[]>([]);
  let bankAccounts = $state<BankAccount[]>([]);
  let bankTransactions = $state<BankTransaction[]>([]);
  let selectedBank = $state('');
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let showBankAccount = $state(false);
  let showBankTransaction = $state(false);
  let showMatch = $state(false);
  let showSuggest = $state(false);
  let showImportCsv = $state(false);
  let editingBank = $state<BankAccount | null>(null);
  let suggestionTxn = $state<BankTransaction | null>(null);
  let suggestions = $state<MatchCandidate[]>([]);
  let suggestLoading = $state(false);
  let suggestApplying = $state(false);
  let importCsvForm = $state({ bankAccountId: '', csv: '' });
  let importResult = $state<{ created: number; skipped: number; errors: string[] } | null>(null);
  let importing = $state(false);
  let bulkResult = $state<{ matched: number; skipped: { externalId: string; reason: string }[] } | null>(null);
  let bulkLoading = $state(false);
  let showBulkResult = $state(false);
  let accountForm = $state({ accountId: '', bankName: '', maskedNumber: '', status: 'active' });
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
        tenantApi.getBankTransactions(slug, `?pageSize=100${selectedBank ? `&bankAccountId=${selectedBank}` : ''}`),
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

  function openCreateBank() {
    editingBank = null;
    accountForm = { accountId: '', bankName: '', maskedNumber: '', status: 'active' };
    showBankAccount = true;
  }

  function openEditBank(bank: BankAccount) {
    editingBank = bank;
    accountForm = { accountId: bank.accountId, bankName: bank.bankName, maskedNumber: bank.maskedNumber, status: bank.status };
    showBankAccount = true;
  }

  async function saveBankAccount() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      if (editingBank) {
        const payload: any = { bankName: accountForm.bankName, maskedNumber: accountForm.maskedNumber };
        const status = accountForm.status ?? editingBank.status;
        if (status !== editingBank.status) payload.status = status;
        await tenantApi.updateBankAccount(slug, editingBank.id, payload);
        showToast('Rekening bank diperbarui', 'success');
      } else {
        await tenantApi.createBankAccount(slug, accountForm);
        showToast('Rekening bank berhasil ditambahkan', 'success');
      }
      showBankAccount = false;
      accountForm = { accountId: '', bankName: '', maskedNumber: '', status: 'active' };
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal menyimpan rekening bank', 'error'); }
    finally { saving = false; }
  }

  async function deleteBank(bank: BankAccount) {
    if (!slug || !isOwner) return;
    if (!confirm(`Hapus rekening bank "${bank.bankName}"?`)) return;
    try {
      await tenantApi.deleteBankAccount(slug, bank.id);
      showToast('Rekening bank dihapus', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal menghapus rekening bank', 'error'); }
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

  function openImportCsv() {
    importCsvForm = { bankAccountId: bankAccounts.find((b) => b.status === 'active')?.id ?? '', csv: '' };
    importResult = null;
    showImportCsv = true;
  }

  async function importCsv() {
    if (!slug || !isOwner) return;
    importing = true;
    importResult = null;
    try {
      importResult = await tenantApi.importBankTransactionsCsv(slug, importCsvForm);
      showToast(`${importResult.created} transaksi diimpor dari CSV`, 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal mengimpor CSV', 'error'); }
    finally { importing = false; }
  }

  async function deleteBankTransaction(txn: BankTransaction) {
    if (!slug || !isOwner) return;
    if (!confirm(`Hapus transaksi bank ${txn.externalId}?`)) return;
    try {
      await tenantApi.deleteBankTransaction(slug, txn.id);
      showToast('Transaksi bank dihapus', 'success');
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal menghapus transaksi bank', 'error'); }
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

  async function openSuggest(txn: BankTransaction) {
    if (!slug) return;
    suggestionTxn = txn;
    suggestions = [];
    showSuggest = true;
    suggestLoading = true;
    try {
      const res = await tenantApi.getReconciliationSuggestions(slug, `?bankAccountId=${txn.bankAccountId}`);
      const item = (res?.items ?? []).find((s: Suggestion) => s.bankTransaction.id === txn.id);
      suggestions = item?.candidates ?? [];
    } catch (err: any) {
      showToast(err?.message || 'Gagal memuat saran', 'error');
      showSuggest = false;
    } finally {
      suggestLoading = false;
    }
  }

  async function applySuggestion(candidate: MatchCandidate) {
    if (!slug || !isOwner || !suggestionTxn) return;
    suggestApplying = true;
    try {
      const match = await tenantApi.createReconciliationMatch(slug, {
        bankTransactionId: suggestionTxn.id,
        transactionId: candidate.id,
        confidence: String(candidate.score),
        note: 'saran otomatis',
      });
      await tenantApi.confirmReconciliationMatch(slug, match.id);
      showToast('Saran diterapkan dan match dikonfirmasi', 'success');
      showSuggest = false;
      suggestionTxn = null;
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal menerapkan saran', 'error'); }
    finally { suggestApplying = false; }
  }

  async function bulkApply() {
    if (!slug || !isOwner) return;
    const unmatched = bankTransactions.filter((t) => !t.matched).length;
    const label = bankAccounts.find((b) => b.id === selectedBank)?.bankName ?? 'semua rekening';
    if (!confirm(`Cocokkan ${unmatched} statement belum dicocokkan di ${label} dengan saran skor >= 90? Statement tanpa kandidat cukup yakin akan dilewati.`)) return;
    bulkLoading = true;
    try {
      bulkResult = await tenantApi.bulkAutoMatch(slug, { minScore: 90, ...(selectedBank ? { bankAccountId: selectedBank } : {}) }) as { matched: number; skipped: { externalId: string; reason: string }[] };
      showToast(`${bulkResult.matched} statement dicocokkan otomatis`, bulkResult.matched > 0 ? 'success' : 'info');
      showBulkResult = true;
      await loadAll();
    } catch (err: any) { showToast(err?.message || 'Gagal mencocokkan otomatis', 'error'); }
    finally { bulkLoading = false; }
  }

  $effect(() => { if (slug) void loadAll(); });
</script>

<PageHeader title="Rekonsiliasi Bank" description="Impor transaksi bank dan cocokkan dengan transaksi posted" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Rekonsiliasi' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={loadAll} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}
      <Button variant="secondary" onclick={openCreateBank}>+ Rekening Bank</Button>
      <Button variant="secondary" onclick={() => showBankTransaction = true} disabled={bankAccounts.length === 0}>+ Impor Bank Txn</Button>
      <Button variant="secondary" onclick={openImportCsv} disabled={bankAccounts.length === 0}>+ Impor CSV</Button>
      <Button variant="secondary" onclick={bulkApply} loading={bulkLoading} disabled={!bankTransactions.some((t) => !t.matched)}>Cocokkan Semua Saran</Button>
      <Button onclick={() => showMatch = true} disabled={bankTransactions.length === 0 || postedTransactions.length === 0}>+ Buat Match</Button>
    {/if}
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Rekonsiliasi ditampilkan read-only. Hanya owner yang dapat mengimpor dan mengonfirmasi match.</div>{/if}

<div class="card p-5 mb-6">
  <div class="flex items-center justify-between mb-3">
    <h3 class="font-semibold">Rekening Bank</h3>
  </div>
  <div class="space-y-2">
    {#each bankAccounts as bank}
      <div class="flex items-center justify-between gap-3 rounded-lg border border-[hsl(var(--border))] px-4 py-3">
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <p class="truncate font-medium">{bank.bankName}</p>
            <span class="rounded-full px-2 py-0.5 text-xs {bank.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-zinc-100 text-zinc-600'}">{bank.status === 'active' ? 'Aktif' : 'Nonaktif'}</span>
          </div>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">{bank.maskedNumber || '-'} · {bank.accountName || bank.accountId}</p>
          <div class="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
            <span class="rounded bg-[hsl(var(--muted))] px-2 py-0.5 font-medium tabular-nums">Saldo Buku: {formatIDR(Number(bank.glBalance ?? 0))}</span>
            {#if (bank.statementCount ?? 0) > 0}
              <span class="rounded bg-[hsl(var(--muted))] px-2 py-0.5 tabular-nums">{bank.statementCount} transaksi · {formatIDR(Number(bank.statementTotal ?? 0))}</span>
            {/if}
            {#if (bank.unmatchedCount ?? 0) > 0}
              <span class="rounded bg-amber-100 px-2 py-0.5 font-medium text-amber-700 tabular-nums">{bank.unmatchedCount} belum dicocokkan · {formatIDR(Number(bank.unmatchedTotal ?? 0))}</span>
            {/if}
          </div>
        </div>
        {#if isOwner}
          <div class="flex items-center gap-1">
            <button class="rounded p-1.5 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]" onclick={() => openEditBank(bank)} title="Edit"><Pencil class="w-4 h-4" /></button>
            <button class="rounded p-1.5 text-red-500 hover:bg-red-50" onclick={() => deleteBank(bank)} title="Hapus"><Trash2 class="w-4 h-4" /></button>
          </div>
        {/if}
      </div>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada rekening bank.</p>
    {/each}
  </div>
</div>

<h3 class="font-semibold mb-3">Transaksi Bank ({bankTransactions.length})</h3>
<div class="mb-3 flex items-center gap-2">
  <label class="text-sm text-[hsl(var(--muted-foreground))]" for="bank-txn-filter">Rekening:</label>
  <select id="bank-txn-filter" bind:value={selectedBank} class="input-field w-64" onchange={() => loadAll()}>
    <option value="">Semua rekening</option>
    {#each bankAccounts as bank}<option value={bank.id}>{bank.bankName} · {bank.maskedNumber || '-'}</option>{/each}
  </select>
</div>
<DataTable columns={[
  { key: 'transactionDate', label: 'Tanggal' },
  { key: 'externalId', label: 'External ID' },
  { key: 'description', label: 'Deskripsi' },
  { key: 'amount', label: 'Jumlah', align: 'right' },
  { key: 'matched', label: 'Status', render: (r: any) => r.matched ? '<span class="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">Terkait</span>' : '<span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">Belum dicocokkan</span>' },
]} data={bankTransactions} total={bankTransactions.length} loading={loading} searchable={true}>
  {#snippet rowActions(item: BankTransaction)}
    {#if !item.matched}
      <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => openSuggest(item)} title="Lihat saran pencocokan">Saran</button>
    {/if}
    {#if isOwner}
      <button class="rounded p-1 text-red-500 hover:bg-red-50" onclick={() => deleteBankTransaction(item)} title="Hapus"><Trash2 class="w-4 h-4" /></button>
    {/if}
  {/snippet}
</DataTable>

<h3 class="font-semibold mb-3 mt-6">Candidate Match ({matches.length})</h3>
<DataTable columns={[{ key: 'id', label: 'ID' }, { key: 'bankTransactionId', label: 'Bank Txn' }, { key: 'transactionId', label: 'Transaksi' }, { key: 'confidence', label: 'Confidence', align: 'right' }, { key: 'status', label: 'Status' }, { key: 'matchedAt', label: 'Matched At' }, { key: 'note', label: 'Catatan' }]} data={matches} total={matches.length} loading={loading} searchable={true}>
  {#snippet rowActions(item: Match)}
    {#if isOwner && item.status === 'candidate'}<button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => confirmMatch(item.id)}>Konfirmasi</button>{/if}
  {/snippet}
</DataTable>

<Modal title={editingBank ? 'Edit Rekening Bank' : 'Tambah Rekening Bank'} open={showBankAccount} onclose={() => showBankAccount = false}>
  <form onsubmit={saveBankAccount} class="space-y-4">
    {#if !editingBank}
      <div>
        <label class="label-text" for="bank-gl">Akun GL Aset</label>
        <select id="bank-gl" bind:value={accountForm.accountId} class="input-field mt-1" required>
          <option value="">Pilih akun</option>
          {#each $accounts.filter((a) => a.type === 'asset' && a.status === 'active') as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}
        </select>
      </div>
    {/if}
    <div>
      <label class="label-text" for="bank-name">Nama Bank</label>
      <input id="bank-name" bind:value={accountForm.bankName} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="bank-number">Nomor Tersamarkan</label>
      <input id="bank-number" bind:value={accountForm.maskedNumber} class="input-field mt-1" placeholder="**** 1234" />
    </div>
    {#if editingBank}
      <div>
        <label class="label-text" for="bank-status">Status</label>
        <select id="bank-status" bind:value={accountForm.status} class="input-field mt-1">
          <option value="active">Aktif</option>
          <option value="inactive">Nonaktif</option>
        </select>
      </div>
    {/if}
    <div class="flex justify-end gap-2">
      <Button variant="secondary" type="button" onclick={() => showBankAccount = false}>Batal</Button>
      <Button type="submit" loading={saving}>Simpan</Button>
    </div>
  </form>
</Modal>
<Modal title="Impor Transaksi Bank" open={showBankTransaction} onclose={() => showBankTransaction = false}>
  <form onsubmit={saveBankTransaction} class="space-y-4">
    <div>
      <label class="label-text" for="bank-account">Rekening</label>
      <select id="bank-account" bind:value={bankTxnForm.bankAccountId} class="input-field mt-1" required>
        <option value="">Pilih rekening</option>
        {#each bankAccounts.filter((b) => b.status === 'active') as bank}<option value={bank.id}>{bank.bankName} · {bank.maskedNumber}</option>{/each}
      </select>
    </div>
    <div>
      <label class="label-text" for="external-id">External ID</label>
      <input id="external-id" bind:value={bankTxnForm.externalId} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="bank-date">Tanggal</label>
      <input id="bank-date" type="date" bind:value={bankTxnForm.transactionDate} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="bank-amount">Jumlah</label>
      <input id="bank-amount" type="number" bind:value={bankTxnForm.amount} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="bank-description">Deskripsi</label>
      <input id="bank-description" bind:value={bankTxnForm.description} class="input-field mt-1" />
    </div>
    <div class="flex justify-end gap-2">
      <Button variant="secondary" type="button" onclick={() => showBankTransaction = false}>Batal</Button>
      <Button type="submit" loading={saving}>Impor</Button>
    </div>
  </form>
</Modal>
<Modal title="Buat Candidate Match" open={showMatch} onclose={() => showMatch = false}>
  <form onsubmit={saveMatch} class="space-y-4">
    <div>
      <label class="label-text" for="match-bank">Transaksi Bank</label>
      <select id="match-bank" bind:value={matchForm.bankTransactionId} class="input-field mt-1" required>
        <option value="">Pilih transaksi bank</option>
        {#each bankTransactions as txn}<option value={txn.id}>{txn.transactionDate} · {txn.description} · {txn.amount}</option>{/each}
      </select>
    </div>
    <div>
      <label class="label-text" for="match-internal">Transaksi Internal Posted</label>
      <select id="match-internal" bind:value={matchForm.transactionId} class="input-field mt-1" required>
        <option value="">Pilih transaksi</option>
        {#each postedTransactions as txn}<option value={txn.id}>{txn.date} · {txn.description} · {txn.amount}</option>{/each}
      </select>
    </div>
    <div>
      <label class="label-text" for="match-note">Catatan</label>
      <input id="match-note" bind:value={matchForm.note} class="input-field mt-1" />
    </div>
    <div class="flex justify-end gap-2">
      <Button variant="secondary" type="button" onclick={() => showMatch = false}>Batal</Button>
      <Button type="submit" loading={saving}>Buat Match</Button>
    </div>
  </form>
</Modal>
<Modal title="Impor Statement CSV" open={showImportCsv} onclose={() => showImportCsv = false}>
  <form onsubmit={importCsv} class="space-y-4">
    <div>
      <label class="label-text" for="csv-bank">Rekening</label>
      <select id="csv-bank" bind:value={importCsvForm.bankAccountId} class="input-field mt-1" required>
        <option value="">Pilih rekening</option>
        {#each bankAccounts.filter((b) => b.status === 'active') as bank}<option value={bank.id}>{bank.bankName} · {bank.maskedNumber}</option>{/each}
      </select>
    </div>
    <div>
      <label class="label-text" for="csv-text">Isi CSV</label>
      <textarea id="csv-text" bind:value={importCsvForm.csv} rows={8} class="input-field mt-1 font-mono text-xs" placeholder={'tanggal;deskripsi;jumlah\n2026-06-15;Pembayaran pelanggan;150000\n2026-06-16;Bayar supplier;-25000'} required />
      <p class="mt-1 text-xs text-[hsl(var(--muted-foreground))]">Format per baris: tanggal (YYYY-MM-DD); deskripsi; jumlah. Jumlah boleh negatif, titik ribuan & koma desimal didukung. Baris sama tidak akan diimpor dua kali.</p>
    </div>
    {#if importResult}
      <div class="rounded-lg border border-[hsl(var(--border))] p-3 text-sm">
        <p class="font-medium">{importResult.created} diimpor · {importResult.skipped} dilewati</p>
        {#if importResult.errors.length > 0}
          <ul class="mt-1 list-inside list-disc text-xs text-red-600">
            {#each importResult.errors as err}<li>{err}</li>{/each}
          </ul>
        {/if}
      </div>
    {/if}
    <div class="flex justify-end gap-2">
      <Button variant="secondary" type="button" onclick={() => showImportCsv = false}>Tutup</Button>
      <Button type="submit" loading={importing}>Impor CSV</Button>
    </div>
  </form>
</Modal>
<Modal title={suggestionTxn ? `Saran Pencocokan · ${suggestionTxn.externalId}` : 'Saran Pencocokan'} open={showSuggest} onclose={() => showSuggest = false}>
  {#if suggestLoading}
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Mencari kandidat transaksi internal…</p>
  {:else if suggestions.length === 0}
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Tidak ada transaksi internal dengan jumlah yang sama dalam ±7 hari.</p>
  {:else}
    <p class="mb-3 text-sm text-[hsl(var(--muted-foreground))]">
      Transaksi bank {suggestionTxn?.transactionDate} · {formatIDR(Number(suggestionTxn?.amount ?? 0))} · {suggestionTxn?.description || '-'}
    </p>
    <div class="space-y-2">
      {#each suggestions as candidate}
        <div class="flex items-center justify-between gap-3 rounded-lg border border-[hsl(var(--border))] px-3 py-2">
          <div class="min-w-0">
            <p class="truncate text-sm font-medium">{candidate.transactionNumber} · {candidate.transactionDate}</p>
            <p class="truncate text-xs text-[hsl(var(--muted-foreground))]">{candidate.description || '-'} · {formatIDR(Number(candidate.amount))}</p>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <span class="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-medium text-sky-700">Skor {candidate.score}</span>
            {#if isOwner}
              <Button variant="secondary" size="sm" loading={suggestApplying} onclick={() => applySuggestion(candidate)}>Cocokkan</Button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
    {#if !isOwner}
      <p class="mt-3 text-xs text-[hsl(var(--muted-foreground))]">Read-only: hanya owner yang dapat menerapkan saran.</p>
    {/if}
  {/if}
</Modal>
<Modal title="Hasil Cocokkan Semua Saran" open={showBulkResult} onclose={() => showBulkResult = false}>
  <p class="text-sm">
    <span class="font-semibold text-[var(--color-kepin-green)]">{bulkResult?.matched ?? 0} statement</span> dicocokkan otomatis dan dikonfirmasi.
  </p>
  {#if (bulkResult?.skipped?.length ?? 0) > 0}
    <div class="mt-3">
      <p class="mb-1 text-sm font-medium">Dilewati ({bulkResult?.skipped.length}):</p>
      <ul class="max-h-56 space-y-1 overflow-y-auto rounded-lg border border-[hsl(var(--border))] p-3 text-xs">
        {#each bulkResult?.skipped ?? [] as item}
          <li class="flex items-center justify-between gap-2">
            <span class="truncate font-medium">{item.externalId}</span>
            <span class="shrink-0 text-[hsl(var(--muted-foreground))]">{item.reason}</span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
  <div class="mt-4 flex justify-end">
    <Button variant="secondary" onclick={() => showBulkResult = false}>Tutup</Button>
  </div>
</Modal>
