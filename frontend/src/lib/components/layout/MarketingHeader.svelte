<script lang="ts">
  import { Menu, X, Building2, HelpCircle } from '@lucide/svelte';
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { landingAnchors } from '$lib/config/navigation';
  import { mainTour } from '$lib/config/tour';
  import { requestTourStart } from '$lib/stores/tour';

  let mobileOpen = $state(false);
  let scrolled = $state(false);
  let linkHref = $state('');
  let linkText = $state('');

  function startTour() {
    requestTourStart(mainTour, 0);
  }

  function onScroll() {
    scrolled = window.scrollY > 20;
  }

  $effect(() => {
    window.addEventListener('scroll', onScroll);
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('kepin_token');
      if (token) {
        const user = JSON.parse(localStorage.getItem('kepin_session') || '{}');
        const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
        if (user.isSuperadmin) {
          linkHref = '/admin';
          linkText = 'Panel';
        } else if (tenants.length > 0) {
          linkHref = `/app/${tenants[0].slug}`;
          linkText = tenants[0].name || 'Dashboard';
        } else {
          linkHref = '/auth/onboarding';
          linkText = 'Lengkapi Profil';
        }
      }
    }
    return () => window.removeEventListener('scroll', onScroll);
  });
</script>

<header
  data-tour="landing-header"
  class="fixed top-0 left-0 right-0 z-50 transition-all duration-200"
  class:bg-[hsl(var(--card))]= {scrolled}
  class:shadow-sm= {scrolled}
  class:bg-transparent= {!scrolled}
>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16 sm:h-20">
      <a href="/" class="flex items-center gap-2">
        <Logo height={28} />
      </a>

      <nav class="hidden lg:flex items-center gap-1">
        {#each landingAnchors as anchor}
          <a
            href={anchor.href}
            class="px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] transition-colors rounded-md hover:bg-[hsl(var(--accent))]"
          >
            {anchor.label}
          </a>
        {/each}
      </nav>

      <div class="flex items-center gap-2 sm:gap-3">
        <button
          onclick={startTour}
          class="inline-flex items-center justify-center w-9 h-9 rounded-md hover:bg-[hsl(var(--accent))]"
          aria-label="Buka tutorial langkah demi langkah"
          title="Tutorial langkah demi langkah"
        >
          <HelpCircle class="w-4 h-4" />
        </button>
        <ThemeMenu />
        {#if linkHref}
          <a href={linkHref} class="btn-primary btn-sm hidden sm:inline-flex">
            <Building2 class="w-4 h-4" />
            {linkText}
          </a>
        {:else}
          <a href="/auth/login" class="btn-ghost btn-sm hidden sm:inline-flex" data-tour="cta-login">
            Masuk
          </a>
          <a href="/auth/register" class="btn-primary btn-sm" data-tour="cta-register">
            Coba Gratis
          </a>
        {/if}
        <button
          class="lg:hidden inline-flex items-center justify-center w-9 h-9 rounded-md hover:bg-[hsl(var(--accent))]"
          onclick={() => mobileOpen = !mobileOpen}
          aria-label="Menu"
        >
          {#if mobileOpen}
            <X class="w-5 h-5" />
          {:else}
            <Menu class="w-5 h-5" />
          {/if}
        </button>
      </div>
    </div>
  </div>

  {#if mobileOpen}
    <div class="lg:hidden border-t border-[var(--color-line)] bg-[var(--color-surface)]">
      <div class="px-4 py-3 space-y-1">
        {#each landingAnchors as anchor}
          <a
            href={anchor.href}
            class="block px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] rounded-md hover:bg-[hsl(var(--accent))]"
            onclick={() => mobileOpen = false}
          >
            {anchor.label}
          </a>
        {/each}
        <hr class="my-2 border-[var(--color-line)]">
        {#if linkHref}
          <a href={linkHref} class="block px-3 py-2 text-sm font-medium text-[hsl(var(--primary))]">
            <Building2 class="w-4 h-4 inline" /> {linkText}
          </a>
        {:else}
          <a href="/auth/login" class="block px-3 py-2 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)]">
            Masuk
          </a>
          <a href="/auth/register" class="block px-3 py-2 text-sm font-medium text-[hsl(var(--primary))]">
            Coba Gratis
          </a>
        {/if}
      </div>
    </div>
  {/if}
</header>