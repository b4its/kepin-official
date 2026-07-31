<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { adminApi } from '$lib/stores/data';
  import { CheckCircle, RefreshCw, XCircle } from '@lucide/svelte';

  let health = $state<any>(null);
  let loading = $state(false);
  let error = $state('');

  async function loadHealth() {
    loading = true;
    error = '';
    try {
      health = await adminApi.getHealthSummary();
    } catch (err: any) {
      error = err?.message || 'Gagal memuat health summary';
    } finally {
      loading = false;
    }
  }

  $effect(() => { void loadHealth(); });
</script>

<PageHeader title="Keamanan Platform" description="Status sistem dari backend health summary">
  {#snippet actions()}
    <Button variant="secondary" onclick={loadHealth} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="space-y-3 max-w-2xl">
  {#each [
    { name: 'Platform Status', status: health?.status || 'unknown', desc: 'Status operasional aplikasi' },
    { name: 'Database', status: health?.database || 'unknown', desc: 'Koneksi database backend' },
    { name: 'Version', status: health?.version || 'unknown', desc: 'Versi aplikasi yang dilaporkan backend' },
    { name: 'Uptime', status: health?.uptime ?? 'not-reported', desc: 'Uptime backend, jika tersedia' },
  ] as check}
    <div class="card p-4 flex items-center gap-3">
      {#if check.status === 'operational' || check.status === 'healthy'}
        <CheckCircle class="w-5 h-5 text-[var(--color-kepin-green)] shrink-0" />
      {:else}
        <XCircle class="w-5 h-5 text-[var(--color-kepin-yellow)] shrink-0" />
      {/if}
      <div>
        <p class="font-medium text-sm">{check.name}: {check.status}</p>
        <p class="text-xs text-[hsl(var(--muted-foreground))]">{check.desc}</p>
      </div>
    </div>
  {/each}
</div>
