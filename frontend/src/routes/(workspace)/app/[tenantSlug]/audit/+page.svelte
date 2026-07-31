<script lang="ts">
  import { page } from '$app/stores';
  import { auditEvents, loadAuditEvents } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { Download, RefreshCw } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');
  let showExport = $state(false);
  let selected = $state<any>(null);
  let loading = $state(false);
  let error = $state('');

  const exportColumns = [
    { key: 'timestamp', label: 'Waktu' },
    { key: 'actor', label: 'Pelaku' },
    { key: 'action', label: 'Aksi' },
    { key: 'module', label: 'Modul' },
    { key: 'objectType', label: 'Tipe Objek' },
    { key: 'objectId', label: 'Objek' },
    { key: 'requestId', label: 'Request ID' },
  ];

  function pretty(value: unknown) {
    return value ? JSON.stringify(value, null, 2) : '-';
  }

  async function refresh() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      await loadAuditEvents(slug);
    } catch (err: any) {
      error = err?.message || 'Gagal memuat audit trail';
    } finally {
      loading = false;
    }
  }

  $effect(() => { if (slug) void refresh(); });
</script>

<PageHeader title="Audit Trail" description="Riwayat perubahan dari backend" breadcrumbs={[{ label: 'Audit Trail' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true} disabled={loading || Boolean(error)}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button variant="secondary" onclick={refresh} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}

<DataTable
  columns={[
    { key: 'timestamp', label: 'Waktu', sortable: true },
    { key: 'actor', label: 'Pelaku', sortable: true },
    { key: 'action', label: 'Aksi' },
    { key: 'module', label: 'Modul' },
    { key: 'objectType', label: 'Tipe' },
    { key: 'objectId', label: 'Objek' },
  ]}
  data={$auditEvents}
  total={$auditEvents.length}
  pageSize={20}
  loading={loading}
  searchable={true}
>
  {#snippet rowActions(item: any)}
    <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => selected = item}>Detail</button>
  {/snippet}
</DataTable>

<Modal title="Detail Audit Event" open={selected !== null} onclose={() => selected = null}>
  {#if selected}
    <div class="space-y-4 text-sm">
      <div class="grid grid-cols-2 gap-3"><p><strong>Waktu:</strong> {selected.timestamp}</p><p><strong>Pelaku:</strong> {selected.actor || '-'}</p><p><strong>Aksi:</strong> {selected.action}</p><p><strong>Modul:</strong> {selected.module || '-'}</p><p><strong>Objek:</strong> {selected.objectType} · {selected.objectId}</p><p><strong>Request:</strong> {selected.requestId || '-'}</p></div>
      <div><p class="font-semibold mb-1">Before</p><pre class="overflow-x-auto rounded bg-[hsl(var(--muted))] p-3 text-xs">{pretty(selected.before)}</pre></div>
      <div><p class="font-semibold mb-1">After</p><pre class="overflow-x-auto rounded bg-[hsl(var(--muted))] p-3 text-xs">{pretty(selected.after)}</pre></div>
    </div>
  {/if}
</Modal>

<ExportModal open={showExport} onclose={() => showExport = false} title="Audit Trail" subtitle="Riwayat aktivitas backend" columns={exportColumns} rows={$auditEvents} filename="audit-trail" />
