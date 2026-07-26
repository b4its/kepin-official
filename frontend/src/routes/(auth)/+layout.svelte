<script lang="ts">
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';

  let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-[hsl(var(--background))]">
  <div class="flex items-center justify-between px-4 py-3 border-b border-[hsl(var(--border))]">
    <a href="/" class="flex items-center gap-2">
      <div class="w-7 h-7 bg-[var(--color-kepin-red)] flex items-center justify-center rounded">
        <span class="text-white font-bold text-xs">K</span>
      </div>
      <span class="font-bold text-sm">KePin</span>
    </a>
    <ThemeMenu />
  </div>
  <main class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      {@render children()}
    </div>
  </main>
</div>
