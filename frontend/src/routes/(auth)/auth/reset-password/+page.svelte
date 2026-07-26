<script lang="ts">
  import { Lock } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let password = $state('');
  let confirm = $state('');
  let loading = $state(false);

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;
    await new Promise(r => setTimeout(r, 1000));
    loading = false;
    window.location.href = '/auth/login';
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <h1 class="text-2xl font-bold">Reset Password</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Buat password baru untuk akun Anda</p>
  </div>

  <form onsubmit={handleSubmit} class="space-y-4">
    <div>
      <label class="label-text mb-1 block" for="new-password">Password Baru</label>
      <div class="relative">
        <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input id="new-password" type="password" bind:value={password} placeholder="Min. 8 karakter" required minlength={8} class="input-field pl-10" />
      </div>
    </div>
    <div>
      <label class="label-text mb-1 block" for="confirm-password">Konfirmasi Password</label>
      <input id="confirm-password" type="password" bind:value={confirm} placeholder="Ulangi password" required class="input-field" />
    </div>
    <Button type="submit" class="w-full" {loading}>
      Reset Password
    </Button>
  </form>
</div>
