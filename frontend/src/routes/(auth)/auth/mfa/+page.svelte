<script lang="ts">
  import { Shield } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let codes = $state(Array(6).fill(''));
  let loading = $state(false);

  function handleInput(e: Event, i: number) {
    const input = e.target as HTMLInputElement;
    if (input.value && i < 5) {
      const next = document.getElementById(`mfa-${i + 1}`);
      next?.focus();
    }
  }

  function handlePaste(e: ClipboardEvent) {
    const data = e.clipboardData?.getData('text');
    if (data?.length === 6) {
      codes = data.split('');
    }
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <div class="w-12 h-12 bg-[var(--color-kepin-blue)] rounded-full flex items-center justify-center mx-auto mb-4">
      <Shield class="w-6 h-6 text-white" />
    </div>
    <h1 class="text-2xl font-bold">Verifikasi Dua Langkah</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Masukkan kode 6 digit dari aplikasi authenticator Anda</p>
  </div>

  <form class="space-y-6">
    <div class="flex justify-center gap-2" onpaste={handlePaste}>
      {#each codes as _, i}
        <input
          id="mfa-{i}"
          type="text"
          maxlength={1}
          bind:value={codes[i]}
          oninput={(e) => handleInput(e, i)}
          class="w-10 h-12 text-center text-lg font-bold border border-[hsl(var(--input))] rounded focus-visible:outline-2 focus-visible:outline-[hsl(var(--ring))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
        />
      {/each}
    </div>
    <Button type="submit" class="w-full" {loading}>
      Verifikasi
    </Button>
  </form>

  <div class="mt-4 text-center space-y-2">
    <p class="text-sm">
      <a href="/auth/login" class="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">Gunakan recovery code</a>
    </p>
  </div>
</div>
