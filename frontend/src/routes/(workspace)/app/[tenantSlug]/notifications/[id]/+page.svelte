<script lang="ts">
  import { page } from '$app/stores';
  import { ArrowLeft, Trash2 } from '@lucide/svelte';
  import { deleteNotification, markNotifRead, tenantApi } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { formatRelativeTime } from '$lib/utils/time';
  import { formatDateTime } from '$lib/utils/date';
  import { showToast } from '$lib/stores/toast';

  type Detail = { id: string; title: string; message: string; type: string; link?: string | null; readAt?: string | null; createdAt?: string | null; metadata?: Record<string, unknown> };

  const slug = $derived($page.params.tenantSlug || '');
  const id = $derived($page.params.id || '');
  let notification = $state<Detail | null>(null);
  let loading = $state(false);
  let error = $state('');

  async function loadNotification() {
    if (!slug || !id) return;
    loading = true;
    error = '';
    try {
      notification = await tenantApi.getNotification(slug, id) as Detail;
      if (!notification.readAt) await markNotifRead(id);
    } catch (err: any) {
      error = err?.message || 'Notifikasi tidak ditemukan';
    } finally {
      loading = false;
    }
  }

  async function remove() {
    if (!notification || !confirm('Hapus notifikasi ini?')) return;
    try {
      await deleteNotification(notification.id);
      window.location.href = `/app/${slug}/notifications`;
    } catch (err: any) {
      showToast(err?.message || 'Gagal menghapus notifikasi', 'error');
    }
  }

  function goBack() { window.location.href = `/app/${slug}/notifications`; }
  $effect(() => { if (slug && id) void loadNotification(); });
</script>

<PageHeader title="Detail Notifikasi" description="Informasi lengkap notifikasi" breadcrumbs={[{ label: 'Notifikasi', href: `/app/${slug}/notifications` }, { label: 'Detail' }]} />

{#if loading}
  <div class="card max-w-2xl mx-auto p-6"><div class="skeleton h-24 w-full"></div></div>
{:else if notification}
  <div class="max-w-2xl mx-auto"><div class="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-6"><div class="flex items-start justify-between mb-4"><div><p class="font-semibold">{notification.title}</p><p class="text-sm mt-2">{notification.message}</p><p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">{formatRelativeTime(notification.createdAt || '')}</p></div></div><div class="space-y-3 text-sm text-[hsl(var(--muted-foreground))]"><div class="flex justify-between py-2 border-t border-[hsl(var(--border))]"><span>Waktu</span><span class="text-[hsl(var(--foreground))]">{formatDateTime(notification.createdAt || '')}</span></div><div class="flex justify-between py-2 border-t border-[hsl(var(--border))]"><span>Status</span><span class="text-[hsl(var(--foreground))]">{notification.readAt ? 'Sudah dibaca' : 'Belum dibaca'}</span></div>{#if notification.link}<div class="border-t border-[hsl(var(--border))] pt-3"><a class="text-[hsl(var(--primary))] hover:underline" href={notification.link}>Buka tautan terkait</a></div>{/if}</div><div class="flex gap-2 mt-6 pt-4 border-t border-[hsl(var(--border))]"><Button variant="secondary" onclick={goBack}><ArrowLeft class="w-4 h-4" />Kembali</Button><Button variant="secondary" onclick={remove}><Trash2 class="w-4 h-4" />Hapus</Button></div></div></div>
{:else}
  <div class="flex flex-col items-center justify-center py-20 text-[hsl(var(--muted-foreground))]"><p class="text-sm font-medium">{error || 'Notifikasi tidak ditemukan'}</p><Button variant="secondary" onclick={goBack} class="mt-4"><ArrowLeft class="w-4 h-4" />Kembali</Button></div>
{/if}
