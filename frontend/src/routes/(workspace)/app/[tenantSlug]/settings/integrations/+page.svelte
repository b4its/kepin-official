<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { Link, Unlink, RefreshCw } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const integrations = [
    { name: 'BCA API', icon: Link, status: 'connected', desc: 'Rekonsiliasi otomatis' },
    { name: 'POS System', icon: Unlink, status: 'disconnected', desc: 'Sinkronisasi penjualan' },
    { name: 'WhatsApp', icon: Link, status: 'connected', desc: 'Notifikasi invoice' },
  ];
</script>

<PageHeader title="Integrasi" description="Hubungkan KePin dengan layanan lain" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Integrasi' }]} />

<div class="space-y-3 max-w-lg">
  {#each integrations as int}
    <div class="card p-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <int.icon class="w-5 h-5 text-[var(--color-kepin-blue)] shrink-0" />
        <div>
          <p class="font-medium text-sm">{int.name}</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">{int.desc}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        {#if int.status === 'connected'}
          <span class="badge-success">Terhubung</span>
          <Button variant="ghost" size="sm">Putuskan</Button>
        {:else}
          <span class="badge-neutral">Putus</span>
          <Button variant="secondary" size="sm">Hubungkan</Button>
        {/if}
      </div>
    </div>
  {/each}
</div>
