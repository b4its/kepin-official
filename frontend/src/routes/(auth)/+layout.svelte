<script lang="ts">
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';

  let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-[hsl(var(--background))]">
  <div class="flex items-center justify-between px-4 py-3 border-b border-[hsl(var(--border))]">
    <a href="/" class="flex items-center gap-2">
      <Logo height={24} />
    </a>
    <ThemeMenu />
  </div>
  <main class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      {@render children()}
    </div>
  </main>
</div>