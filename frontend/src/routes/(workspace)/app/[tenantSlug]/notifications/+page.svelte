<script lang="ts">
  import { Inbox, CheckCheck } from '@lucide/svelte';
  import { page } from '$app/stores';
  import { notifications, markAllNotifRead } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { showToast } from '$lib/stores/toast';
  import { formatRelativeTime } from '$lib/utils/time';
  import type { Notification } from '$lib/api/types';
  import Button from '$lib/components/ui/Button.svelte';

  const tenantSlug = $derived($page.params.tenantSlug || '');

  function goTo(id: string) {
    window.location.href = `/app/${tenantSlug}/notifications/${id}`;
  }

  const unreadCount = $derived($notifications.filter(n => !n.read).length);

  const PAGE_SIZE = 20;
  let pageNo = $state(1);
  const totalPages = $derived(Math.max(1, Math.ceil($notifications.length / PAGE_SIZE)));
  const paged = $derived($notifications.slice((pageNo - 1) * PAGE_SIZE, pageNo * PAGE_SIZE));

  const typeIcon = {
    info: 'bg-blue-500/10 text-blue-500',
    warning: 'bg-yellow-500/10 text-yellow-500',
    success: 'bg-green-500/10 text-green-500',
    error: 'bg-red-500/10 text-red-500',
  };

  async function markAll() {
    try {
      await markAllNotifRead();
      showToast('Semua notifikasi ditandai dibaca', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Gagal menandai notifikasi', 'error');
    }
  }
</script>

<PageHeader title="Notifikasi" description="Pemberitahuan dan aktivitas terbaru" breadcrumbs={[{ label: 'Notifikasi' }]}>
  {#snippet actions()}
    {#if unreadCount > 0}
      <Button variant="secondary" onclick={markAll}>
        <CheckCheck class="w-4 h-4" />
        Tandai Dibaca
      </Button>
    {/if}
  {/snippet}
</PageHeader>

{#if $notifications.length === 0}
  <div class="flex flex-col items-center justify-center py-20 text-[hsl(var(--muted-foreground))]">
    <Inbox class="w-12 h-12 mb-3" />
    <p class="text-sm font-medium">Tidak ada notifikasi</p>
    <p class="text-xs mt-1">Semua notifikasi akan muncul di sini</p>
  </div>
{:else}
  <div class="space-y-1">
    {#each paged as n}
      <button
        onclick={() => goTo(n.id)}
        class="w-full text-left flex items-start gap-3 px-4 py-3 rounded-md hover:bg-[hsl(var(--accent))] transition-colors border border-transparent hover:border-[hsl(var(--border))]"
      >
        <div class="w-2 h-2 rounded-full mt-1.5 shrink-0 {n.read ? 'bg-transparent' : 'bg-[hsl(var(--primary))]'}" />
        <div class="flex-1 min-w-0">
          <p class="text-sm {n.read ? '' : 'font-semibold'}">{n.title || n.message}</p>
          {#if n.title && n.message}<p class="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{n.message}</p>{/if}
          <p class="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{formatRelativeTime(n.createdAt)}</p>
        </div>
      </button>
    {/each}
  </div>
  {#if totalPages > 1}
    <div class="flex items-center justify-between mt-4 text-xs text-[hsl(var(--muted-foreground))]">
      <span>Menampilkan {paged.length} dari {$notifications.length} notifikasi</span>
      <div class="flex items-center gap-1">
        <button
          class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
          disabled={pageNo <= 1}
          onclick={() => pageNo -= 1}
        >Sebelumnya</button>
        <span class="px-2 tabular-nums">Halaman {pageNo} / {totalPages}</span>
        <button
          class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
          disabled={pageNo >= totalPages}
          onclick={() => pageNo += 1}
        >Berikutnya</button>
      </div>
    </div>
  {/if}
{/if}
