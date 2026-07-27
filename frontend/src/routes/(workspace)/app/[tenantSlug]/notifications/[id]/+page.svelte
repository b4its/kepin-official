<script lang="ts">
  import { page } from '$app/stores';
  import { ArrowLeft, Trash2 } from '@lucide/svelte';
  import { notifications, deleteNotification, markNotifRead } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { formatRelativeTime } from '$lib/utils/time';
  import { formatDateTime } from '$lib/utils/date';

  const notification = $derived($notifications.find(n => n.id === $page.params.id));

  $effect(() => {
    if (notification && !notification.read) {
      if ($page.params.id) markNotifRead($page.params.id);
    }
  });

  function goBack() {
    const parts = window.location.pathname.split('/');
    const tenantSlug = parts[2] || '';
    window.location.href = `/app/${tenantSlug}/notifications`;
  }

  function deleteNotif() {
    if ($page.params.id) deleteNotification($page.params.id);
    window.location.href = `/app/${$page.params.tenantSlug}/notifications`;
  }
</script>

<PageHeader
  title="Detail Notifikasi"
  description="Informasi lengkap notifikasi"
  breadcrumbs={[
    { label: 'Notifikasi', href: `/app/${$page.params.tenantSlug}/notifications` },
    { label: 'Detail' },
  ]}
/>

{#if notification}
  <div class="max-w-2xl mx-auto">
    <div class="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-6">
      <div class="flex items-start justify-between mb-4">
        <div>
          <p class="font-semibold">{notification.message}</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">
            {formatRelativeTime(notification.createdAt)}
          </p>
        </div>
      </div>

      <div class="space-y-3 text-sm text-[hsl(var(--muted-foreground))]">
        <div class="flex justify-between py-2 border-t border-[hsl(var(--border))]">
          <span>Waktu</span>
          <span class="text-[hsl(var(--foreground))]">{formatDateTime(notification.createdAt)}</span>
        </div>
        <div class="flex justify-between py-2 border-t border-[hsl(var(--border))]">
          <span>Status</span>
          <span class="text-[hsl(var(--foreground))]">{notification.read ? 'Sudah dibaca' : 'Belum dibaca'}</span>
        </div>
      </div>

      <div class="flex gap-2 mt-6 pt-4 border-t border-[hsl(var(--border))]">
        <Button variant="secondary" onclick={goBack}>
          <ArrowLeft class="w-4 h-4" />
          Kembali
        </Button>
        <Button variant="secondary" onclick={deleteNotif}>
          <Trash2 class="w-4 h-4" />
          Hapus
        </Button>
      </div>
    </div>
  </div>
{:else}
  <div class="flex flex-col items-center justify-center py-20 text-[hsl(var(--muted-foreground))]">
    <p class="text-sm font-medium">Notifikasi tidak ditemukan</p>
    <Button variant="secondary" onclick={goBack} class="mt-4">
      <ArrowLeft class="w-4 h-4" />
      Kembali
    </Button>
  </div>
{/if}
