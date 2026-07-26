<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Menu, Bell, HelpCircle, User } from '@lucide/svelte';
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';

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
</script>

<header class="sticky top-0 z-30 h-14 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]/95 backdrop-blur">
  <div class="flex items-center justify-between h-full px-4 gap-2">
    <div class="flex items-center gap-3">
      <button
        onclick={ontogglesidebar}
        class="lg:hidden inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]"
        aria-label="Toggle menu"
      >
        <Menu class="w-4 h-4" />
      </button>
      <span class="font-semibold text-sm truncate max-w-[200px] sm:max-w-none">{title}</span>
    </div>
    {#if children}
      <div class="hidden sm:flex items-center gap-2">
        {@render children()}
      </div>
    {/if}
    <div class="flex items-center gap-1">
      <ThemeMenu />
      <button class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]" aria-label="Notifikasi">
        <Bell class="w-4 h-4" />
      </button>
      <button class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]" aria-label="Bantuan">
        <HelpCircle class="w-4 h-4" />
      </button>
      <button class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]" aria-label="Profil">
        <User class="w-4 h-4" />
      </button>
    </div>
  </div>
</header>
