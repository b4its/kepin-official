<script lang="ts">
  import MarketingHeader from '$lib/components/layout/MarketingHeader.svelte';
  import MarketingFooter from '$lib/components/layout/MarketingFooter.svelte';

  let { children } = $props();
</script>

<MarketingHeader />
<main class="min-h-screen pt-16 sm:pt-20">
  {@render children()}
</main>
<MarketingFooter />
