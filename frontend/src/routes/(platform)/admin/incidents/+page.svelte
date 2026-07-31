<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { adminApi } from '$lib/stores/data';
  import { RefreshCw } from '@lucide/svelte';

  let incidents = $state<any[]>([]);
  let loading = $state(false);
  let error = $state('');

  async function loadIncidents() {
    loading = true;
    error = '';
    try {
      const res: any = await adminApi.getIncidents();
      incidents = res.items || [];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat insiden';
    } finally {
      loading = false;
    }
  }

  $effect(() => { void loadIncidents(); });
</script>

<PageHeader title="Insiden Keamanan" description="Insiden platform dari backend">
  {#snippet actions()}
    <Button variant="secondary" onclick={loadIncidents} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<DataTable
  columns={[
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Deskripsi' },
    { key: 'severity', label: 'Severitas' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Dibuat', render: (r: any) => r.createdAt || r.created_at || '-' },
  ]}
  data={incidents}
  total={incidents.length}
  loading={loading}
  searchable={true}
/>
