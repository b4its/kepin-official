<script lang="ts">
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { HelpCircle } from '@lucide/svelte';
  import { mainTour } from '$lib/config/tour';
  import { requestTourStart } from '$lib/stores/tour';

  let { children } = $props();

  function startTour() {
    requestTourStart(mainTour, 0);
  }
</script>

<div class="min-h-screen flex flex-col bg-[hsl(var(--background))]">
  <header class="flex items-center justify-between px-4 py-3 border-b border-[hsl(var(--border))]">
    <a href="/" class="flex items-center gap-2">
      <Logo height={24} />
    </a>
    <div class="flex items-center gap-1">
      <button
        onclick={startTour}
        class="inline-flex items-center justify-center w-8 h-8 rounded-md hover:bg-[hsl(var(--accent))]"
        aria-label="Buka tutorial langkah demi langkah"
        title="Tutorial langkah demi langkah"
      >
        <HelpCircle class="w-4 h-4" />
      </button>
      <ThemeMenu />
    </div>
  </header>
  <main class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      {@render children()}
    </div>
  </main>
</div>