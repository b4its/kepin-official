<script lang="ts">
  import { Sun, Moon, Monitor } from '@lucide/svelte';

  let theme = $state('system');
  let open = $state(false);

  function setTheme(t: string) {
    theme = t;
    open = false;
    const resolved = t === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : t;
    document.documentElement.className = resolved;
    document.cookie = `kepin_theme=${t};path=/;max-age=31536000`;
  }

  const items = [
    { value: 'light', label: 'Terang', icon: Sun },
    { value: 'dark', label: 'Gelap', icon: Moon },
    { value: 'system', label: 'Sistem', icon: Monitor },
  ];
</script>

<div class="relative">
  <button
    class="inline-flex items-center justify-center w-9 h-9 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
    onclick={() => open = !open}
    aria-label="Tema"
  >
    {#if theme === 'light'}
      <Sun class="w-4 h-4" />
    {:else if theme === 'dark'}
      <Moon class="w-4 h-4" />
    {:else}
      <Monitor class="w-4 h-4" />
    {/if}
  </button>

  {#if open}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="fixed inset-0 z-40" onclick={() => open = false} onkeydown={() => open = false}></div>
    <div class="absolute right-0 top-full mt-1 z-50 min-w-[140px] rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--popover))] p-1 shadow-lg">
      {#each items as item}
        <button
          class="flex items-center gap-2 w-full px-3 py-2 text-sm rounded-md transition-colors hover:bg-[hsl(var(--accent))]"
          class:bg-[hsl(var(--accent))]={theme === item.value}
          onclick={() => setTheme(item.value)}
        >
          <item.icon class="w-4 h-4" />
          {item.label}
        </button>
      {/each}
    </div>
  {/if}
</div>
