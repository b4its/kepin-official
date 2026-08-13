<script lang="ts">
  import '../app.css';
  import Toast from '$lib/components/ui/Toast.svelte';
  import Tour from '$lib/components/tour/Tour.svelte';

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href="/media/logo/kepin-light.png" />
  <link rel="apple-touch-icon" href="/media/logo/kepin-light.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet" />
</svelte:head>

{@render children()}

<Toast />

<!-- Tur interaktif tersedia di seluruh halaman: landing, auth, dan workspace -->
<Tour />