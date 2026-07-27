<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { journalEntries } from '$lib/stores/data';
  import { Download } from '@lucide/svelte';

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ date: '', ref: '', desc: '', status: 'draft', total: 0 });

  const exportColumns = [
    { key: 'date', label: 'Tanggal' },
    { key: 'reference', label: 'Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Dibuat' },
  ];

  function openCreate() {
    form = { date: '', ref: '', desc: '', status: 'draft', total: 0 };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const j = $journalEntries[i];
    form = { date: j.date, ref: j.reference, desc: j.description, status: j.status, total: 0 };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    journalEntries.update((list: any[]) => {
      if (editingIndex !== null) {
        return list.map((j, i) => i === editingIndex ? { ...j, ...form } : j);
      } else {
        return [...list, { id: 'JNL-' + Date.now(), date: form.date, description: form.desc, reference: form.ref, status: form.status, lines: [], createdBy: 'User', createdAt: new Date().toISOString() }];
      }
    });
    showModal = false;
  }

  function confirmDelete() {
    if (deleteIndex !== null) {
      journalEntries.update(list => list.filter((_, i) => i !== deleteIndex));
      deleteIndex = null;
    }
  }
</script>

<PageHeader title="Jurnal" description="Jurnal akuntansi" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Jurnal' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Jurnal Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'reference', label: 'Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
    { key: 'createdAt', label: 'Dibuat' },
  ]}
  data={$journalEntries}
  total={64}
  page={1}
  pageSize={5}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Jurnal' : 'Jurnal Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Tanggal</label>
      <input type="date" bind:value={form.date} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Referensi</label>
      <input type="text" bind:value={form.ref} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Deskripsi</label>
      <input type="text" bind:value={form.desc} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="draft">Draft</option>
          <option value="posted">Posted</option>
        </select>
      </div>
      <div>
        <label class="label-text">Total (Rp)</label>
        <CurrencyInput value={form.total} onchange={(v) => form.total = v} class="input-field mt-1" required />
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
  message="Hapus jurnal ini? Tindakan ini tidak dapat dibatalkan."
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Jurnal Akuntansi"
  subtitle="Daftar entri jurnal"
  columns={exportColumns}
  rows={$journalEntries}
  filename="jurnal"
/>
