<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { currentRole, customers, invoices, createInvoice, deleteInvoice, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Plus, RefreshCw } from '@lucide/svelte';

  type Line = { itemName: string; quantity: string; unit: string; unitPrice: string; taxRate: string; discountAmount: string };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  const rows = $derived($invoices.map((i) => ({ ...i, customerName: $customers.find((c) => c.id === i.customerId)?.name || i.customerName || '' })));
  const totalPiutang = $derived($invoices.filter(i => !['paid', 'cancelled'].includes(i.status)).reduce((s, i) => s + (i.total - i.paidAmount), 0));
  const jatuhTempo = $derived($invoices.filter(i => ['sent', 'partial', 'posted'].includes(i.status)).reduce((s, i) => s + (i.total - i.paidAmount), 0));
  const invoiceBulanIni = $derived($invoices.filter(i => new Date(i.date).getMonth() === new Date().getMonth() && new Date(i.date).getFullYear() === new Date().getFullYear()).length);
  const rataRata = $derived($invoices.length ? Math.round($invoices.reduce((s, i) => s + i.total, 0) / $invoices.length) : 0);
  let showModal = $state(false);
  let showExport = $state(false);
  let deleteIndex = $state<number | null>(null);
  let saving = $state(false);
  let form = $state({ customerId: '', invoiceDate: '', dueDate: '', notes: '', lines: [] as Line[] });
  const draftTotal = $derived(form.lines.reduce((sum, line) => sum + Number(line.quantity || 0) * Number(line.unitPrice || 0) * (1 + Number(line.taxRate || 0) / 100) - Number(line.discountAmount || 0), 0));

  const exportColumns = [{ key: 'number', label: 'No. Invoice' }, { key: 'customerName', label: 'Pelanggan' }, { key: 'date', label: 'Tanggal' }, { key: 'dueDate', label: 'Jatuh Tempo' }, { key: 'total', label: 'Total', render: (r: any) => `Rp ${Number(r.total).toLocaleString('id-ID')}` }, { key: 'paidAmount', label: 'Dibayar', render: (r: any) => `Rp ${Number(r.paidAmount).toLocaleString('id-ID')}` }, { key: 'status', label: 'Status' }];

  function defaultLine(): Line { return { itemName: '', quantity: '1', unit: 'pcs', unitPrice: '', taxRate: '0', discountAmount: '0' }; }
  function openCreate() { const today = new Date().toISOString().slice(0, 10); form = { customerId: '', invoiceDate: today, dueDate: today, notes: '', lines: [defaultLine()] }; showModal = true; }
  function addLine() { form.lines = [...form.lines, defaultLine()]; }
  function removeLine(index: number) { if (form.lines.length > 1) form.lines = form.lines.filter((_, current) => current !== index); }

  async function save() {
    if (!slug || !isOwner) return;
    saving = true;
    try {
      await createInvoice({ ...form, lines: form.lines.map((line) => ({ ...line, unitPrice: line.unitPrice || '0' })) });
      showModal = false;
      showToast('Invoice draft berhasil dibuat', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal membuat invoice', 'error'); }
    finally { saving = false; }
  }
  async function removeDraft() { if (deleteIndex === null) return; try { await deleteInvoice($invoices[deleteIndex].id); showToast('Invoice draft dihapus', 'success'); } catch (err: any) { showToast(err?.message || 'Gagal menghapus invoice', 'error'); } finally { deleteIndex = null; } }
  async function post(item: any) { if (!slug || !isOwner) return; try { await tenantApi.postInvoice(slug, item.id); showToast('Invoice berhasil diposting', 'success'); window.location.reload(); } catch (err: any) { showToast(err?.message || 'Gagal memposting invoice', 'error'); } }
  async function reverse(item: any) { if (!slug || !isOwner || !confirm('Reverse invoice posted ini?')) return; try { await tenantApi.reverseInvoice(slug, item.id); showToast('Invoice reversal berhasil dibuat', 'success'); window.location.reload(); } catch (err: any) { showToast(err?.message || 'Gagal reverse invoice', 'error'); } }
</script>

<PageHeader title="Invoice" description="Draft dan posting faktur penjualan melalui backend" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Invoice' }]}> 
  {#snippet actions()}<Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>{#if isOwner}<Button onclick={openCreate} tourHook="add-invoice"><Plus class="w-4 h-4" /> Invoice Baru</Button>{/if}{/snippet}
</PageHeader>
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Invoice ditampilkan read-only. Hanya owner dapat membuat, posting, atau reverse invoice.</div>{/if}
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"><MetricCard label="Total Piutang" value={totalPiutang} format="currency" /><MetricCard label="Outstanding" value={jatuhTempo} format="currency" /><MetricCard label="Invoice Bulan Ini" value={invoiceBulanIni} format="number" /><MetricCard label="Rata-rata" value={rataRata} format="currency" /></div>
<DataTable columns={[{ key: 'number', label: 'No. Invoice', sortable: true }, { key: 'customerName', label: 'Pelanggan', sortable: true }, { key: 'date', label: 'Tanggal' }, { key: 'dueDate', label: 'Jatuh Tempo' }, { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` }, { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` }]} data={rows} total={rows.length} pageSize={10} searchable={true}>
  {#snippet rowActions(item: any, i: number)}{#if isOwner && item.status === 'draft'}<button class="text-xs text-[var(--color-kepin-green)] hover:underline mr-2" onclick={() => post(item)}>Post</button><button class="text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => deleteIndex = i}>Hapus</button>{/if}{#if isOwner && item.status === 'posted'}<button class="text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => reverse(item)}>Reverse</button>{/if}{/snippet}
</DataTable>
<Modal title="Invoice Baru" open={showModal} onclose={() => showModal = false}><form onsubmit={save} class="space-y-4"><div class="grid sm:grid-cols-2 gap-4"><div><label class="label-text" for="invoice-customer">Pelanggan</label><select id="invoice-customer" bind:value={form.customerId} class="input-field mt-1" required><option value="">Pilih pelanggan</option>{#each $customers as customer}<option value={customer.id}>{customer.name}</option>{/each}</select></div><div><label class="label-text" for="invoice-date">Tanggal</label><input id="invoice-date" type="date" bind:value={form.invoiceDate} class="input-field mt-1" required /></div><div><label class="label-text" for="invoice-due">Jatuh Tempo</label><input id="invoice-due" type="date" bind:value={form.dueDate} class="input-field mt-1" required /></div><div><label class="label-text" for="invoice-notes">Catatan</label><input id="invoice-notes" bind:value={form.notes} class="input-field mt-1" /></div></div><div class="space-y-2"><div class="flex justify-between items-center"><h3 class="text-sm font-semibold">Item</h3><Button size="sm" variant="secondary" type="button" onclick={addLine}>+ Item</Button></div>{#each form.lines as line, index}<div class="grid grid-cols-12 gap-2 rounded border border-[hsl(var(--border))] p-2"><input class="input-field col-span-4" bind:value={line.itemName} placeholder="Nama item" required /><input class="input-field col-span-2" type="number" min="0.01" step="0.01" bind:value={line.quantity} placeholder="Qty" required /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.unitPrice} placeholder="Harga" required /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.taxRate} placeholder="Pajak %" /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.discountAmount} placeholder="Diskon" />{#if form.lines.length > 1}<button type="button" class="col-span-12 text-right text-xs text-[var(--color-kepin-danger)]" onclick={() => removeLine(index)}>Hapus item</button>{/if}</div>{/each}</div><div class="rounded bg-[hsl(var(--muted))] p-3 text-sm font-semibold">Estimasi total: Rp {draftTotal.toLocaleString('id-ID')}</div><div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button><Button type="submit" loading={saving}>Simpan Draft</Button></div></form></Modal>
<ExportModal open={showExport} onclose={() => showExport = false} title="Daftar Invoice" subtitle="Data faktur penjualan" columns={exportColumns} rows={rows} filename="invoice" />
