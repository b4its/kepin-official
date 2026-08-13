<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Menu, Bell, HelpCircle, User, LogOut, ArrowLeft, UserCircle, List, UserPlus } from '@lucide/svelte';
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { formatRelativeTime } from '$lib/utils/time';
  import { currentUser, logout, updateProfile } from '$lib/stores/auth';
  import { notifications, markAllNotifRead } from '$lib/stores/data';

  type Props = {
    title: string;
    sidebarOpen: boolean;
    ontogglesidebar: () => void;
    children?: Snippet;
  };

  let {
    title,
    sidebarOpen,
    ontogglesidebar,
    children,
  }: Props = $props();

  let profileOpen = $state(false);
  let showProfileModal = $state(false);
  let showLogoutConfirm = $state(false);
  let notifOpen = $state(false);
  let profileName = $derived($currentUser?.name || 'Pengguna');
  let profileEmail = $derived($currentUser?.email || '');
  let profilePhone = $derived($currentUser?.phone || '');

  let editName = $state('');
  let editEmail = $state('');
  let editPhone = $state('');

  let tenantSlug = $state('');

  $effect(() => {
    if (typeof window !== 'undefined') {
      const parts = window.location.pathname.split('/');
      tenantSlug = parts[2] || '';
    }
  });

  const unreadCount = $derived($notifications.filter(n => !n.read).length);

  function toggleProfile(e: Event) {
    e.stopPropagation();
    profileOpen = !profileOpen;
    notifOpen = false;
  }

  function closeProfile() {
    profileOpen = false;
  }

  function toggleNotif(e: Event) {
    e.stopPropagation();
    notifOpen = !notifOpen;
    profileOpen = false;
  }

  function closeNotif() {
    notifOpen = false;
  }

  function goToNotif(id: string) {
    notifOpen = false;
    window.location.href = `/app/${tenantSlug}/notifications/${id}`;
  }

  function goToNotifList() {
    notifOpen = false;
    window.location.href = `/app/${tenantSlug}/notifications`;
  }

  function openEditProfile() {
    editName = profileName;
    editEmail = profileEmail;
    editPhone = profilePhone;
    closeProfile();
    showProfileModal = true;
  }

  function saveProfile() {
    updateProfile({ name: editName, email: editEmail, phone: editPhone });
    showProfileModal = false;
  }

  function openLogout() {
    closeProfile();
    showLogoutConfirm = true;
  }

  function confirmLogout() {
    showLogoutConfirm = false;
    logout();
    window.location.href = '/';
  }

  function goToLanding() {
    closeProfile();
      window.location.href = `/`;

  }
</script>

<header class="sticky top-0 z-30 h-14 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]/95 backdrop-blur">
    <div class="flex items-center justify-between h-full px-3 sm:px-4 gap-2">
    <div class="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
      <button
        onclick={ontogglesidebar}
        class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]"
        aria-label="Toggle menu"
      >
        <Menu class="w-4 h-4" />
      </button>
      <span class="font-semibold text-sm truncate max-w-[110px] sm:max-w-none">{title}</span>
    </div>
    {#if children}
      <div class="hidden sm:flex items-center gap-2">
        {@render children()}
      </div>
    {/if}
    <div class="flex items-center gap-1">
      <button
        onclick={() => { window.location.href = `/app/${tenantSlug}/tutorial`; }}
        class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]"
        aria-label="Buka halaman tutorial"
        title="Tutorial langkah demi langkah"
      >
        <HelpCircle class="w-4 h-4" />
      </button>
      <ThemeMenu />
      <div class="relative">
        {#if notifOpen}
          <div class="fixed inset-0 z-40" onclick={closeNotif}></div>
        {/if}
        <button
          onclick={toggleNotif}
          class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))] relative"
          aria-label="Notifikasi"
        >
          <Bell class="w-4 h-4" />
          {#if unreadCount > 0}
            <span class="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 flex items-center justify-center rounded-full bg-[var(--color-kepin-danger)] text-[8px] font-bold text-white leading-none">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          {/if}
        </button>
        {#if notifOpen}
          <div
            class="absolute right-0 top-full mt-1 w-[min(20rem,calc(100vw-1rem))] bg-[hsl(var(--card))] border border-[hsl(var(--border))] shadow-lg z-50"
            onclick={(e) => e.stopPropagation()}
          >
            <div class="px-4 py-3 border-b border-[hsl(var(--border))]">
              <p class="text-sm font-semibold">Notifikasi</p>
            </div>
            <div class="max-h-64 overflow-y-auto">
              {#each $notifications.slice(0, 5) as n}
                <button
                  onclick={() => goToNotif(n.id)}
                  class="w-full text-left flex items-start gap-3 px-4 py-3 hover:bg-[hsl(var(--accent))] transition-colors border-b border-[hsl(var(--border))] last:border-b-0"
                >
                  <div class="w-2 h-2 rounded-full mt-1.5 shrink-0 {n.read ? 'bg-transparent' : 'bg-[hsl(var(--primary))]'}" />
                  <div class="flex-1 min-w-0">
                    <p class="text-xs {n.read ? '' : 'font-semibold'} truncate">{n.message}</p>
                    <p class="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{formatRelativeTime(n.createdAt)}</p>
                  </div>
                </button>
              {/each}
            </div>
            <button
              onclick={goToNotifList}
              class="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[hsl(var(--primary))] hover:bg-[hsl(var(--accent))] transition-colors border-t border-[hsl(var(--border))]"
            >
              <List class="w-4 h-4" />
              Lihat Semua Notifikasi
            </button>
          </div>
        {/if}
      </div>

      <div class="relative">
        {#if profileOpen}
          <div class="fixed inset-0 z-40" onclick={closeProfile}></div>
        {/if}
        <button
          onclick={toggleProfile}
          class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]"
          aria-label="Profil"
        >
          <User class="w-4 h-4" />
        </button>
        {#if profileOpen}
          <div
            class="absolute right-0 top-full mt-1 w-[min(12rem,calc(100vw-1rem))] bg-[hsl(var(--card))] border border-[hsl(var(--border))] shadow-lg z-50"
            onclick={(e) => e.stopPropagation()}
          >
            <div class="px-4 py-3 border-b border-[hsl(var(--border))]">
              <p class="text-sm font-semibold truncate">{profileName}</p>
              <p class="text-xs text-[hsl(var(--muted-foreground))] truncate">{profileEmail}</p>
            </div>
            <div class="py-1">
              <button
                onclick={openEditProfile}
                class="flex items-center gap-3 w-full px-4 py-2 text-sm text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <UserCircle class="w-4 h-4 shrink-0" />
                Edit Profil
              </button>
              <button
                onclick={goToLanding}
                class="flex items-center gap-3 w-full px-4 py-2 text-sm text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <ArrowLeft class="w-4 h-4 shrink-0" />
                Kembali ke Beranda
              </button>
              <button
                onclick={() => { window.location.href = '/auth/join-company'; }}
                class="flex items-center gap-3 w-full px-4 py-2 text-sm text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <UserPlus class="w-4 h-4 shrink-0" />
                Gabung Perusahaan Lain
              </button>
              <button
                onclick={openLogout}
                class="flex items-center gap-3 w-full px-4 py-2 text-sm text-[var(--color-kepin-danger)] hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <LogOut class="w-4 h-4 shrink-0" />
                Logout
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</header>

<Modal title="Edit Profil" open={showProfileModal} onclose={() => showProfileModal = false}>
  <form onsubmit={saveProfile} class="space-y-4">
    <div>
      <label class="label-text">Nama Lengkap</label>
      <input type="text" bind:value={editName} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Email</label>
      <input type="email" bind:value={editEmail} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Telepon</label>
      <input type="text" bind:value={editPhone} class="input-field mt-1" />
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showProfileModal = false}>Batal</Button>
      <Button type="submit">Simpan</Button>
    </div>
  </form>
</Modal>

<ConfirmDialog
  open={showLogoutConfirm}
  onclose={() => showLogoutConfirm = false}
  onconfirm={confirmLogout}
  title="Logout"
  message="Apakah Anda yakin ingin keluar?"
  confirmText="Logout"
/>
