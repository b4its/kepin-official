<script lang="ts">
  import { KeyRound, Lock, RefreshCw, ShieldCheck, ShieldOff } from '@lucide/svelte';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { api } from '$lib/api/client';
  import { changePassword } from '$lib/stores/auth';
  import { showToast } from '$lib/stores/toast';

  let enabled = $state(false);
  let setupAt = $state<string | null>(null);
  let loading = $state(true);
  let error = $state('');
  let setupSecret = $state('');
  let setupUri = $state('');
  let showSetup = $state(false);
  let showRecovery = $state(false);
  let recoveryCodes = $state<string[]>([]);
  let code = $state('');
  let codes = $state(Array(6).fill(''));
  let busy = $state(false);
  let copying = $state(false);

  let pwCurrent = $state('');
  let pwNew = $state('');
  let pwConfirm = $state('');
  let pwSaving = $state(false);
  let pwError = $state('');

  async function loadStatus() {
    loading = true;
    error = '';
    try {
      const res = await api<{ enabled: boolean; setup_at?: string | null }>('/auth/mfa/status');
      enabled = res.enabled;
      setupAt = res.setup_at || null;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat status MFA';
    } finally {
      loading = false;
    }
  }

  async function startSetup() {
    busy = true;
    try {
      const res = await api<{ secret: string; otpauth_uri: string }>('/auth/mfa/setup', {
        method: 'POST',
        body: JSON.stringify({}),
      });
      setupSecret = res.secret;
      setupUri = res.otpauth_uri;
      code = '';
      codes = Array(6).fill('');
      showSetup = true;
      showRecovery = false;
    } catch (err: any) {
      showToast(err?.message || 'Gagal memulai setup MFA', 'error');
    } finally {
      busy = false;
    }
  }

  async function enableMfa() {
    busy = true;
    try {
      const res = await api<{ recovery_codes: string[] }>('/auth/mfa/enable', {
        method: 'POST',
        body: JSON.stringify({ code: code }),
      });
      recoveryCodes = res.recovery_codes || [];
      showSetup = false;
      showRecovery = true;
      enabled = true;
      setupAt = new Date().toISOString();
      showToast('MFA berhasil diaktifkan', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Kode verifikasi salah', 'error');
    } finally {
      busy = false;
    }
  }

  async function disableMfa() {
    busy = true;
    try {
      await api('/auth/mfa/disable', {
        method: 'POST',
        body: JSON.stringify({ code: code }),
      });
      enabled = false;
      setupAt = null;
      code = '';
      codes = Array(6).fill('');
      showToast('MFA berhasil dinonaktifkan', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Kode verifikasi salah', 'error');
    } finally {
      busy = false;
    }
  }

  function copyRecoveryCodes() {
    navigator.clipboard.writeText(recoveryCodes.join('\n'));
    showToast('Recovery codes disalin ke clipboard', 'success');
  }

  function handleInput(e: Event, i: number) {
    const input = e.target as HTMLInputElement;
    if (input.value && i < 5) {
      const next = document.getElementById(`setup-code-${i + 1}`);
      next?.focus();
    }
  }

  function handlePaste(e: ClipboardEvent) {
    const data = e.clipboardData?.getData('text');
    if (data?.length === 6) {
      codes = data.split('');
      code = data;
    }
  }

  async function savePassword() {
    pwError = '';
    if (pwNew !== pwConfirm) {
      pwError = 'Konfirmasi password tidak sama.';
      return;
    }
    pwSaving = true;
    const result = await changePassword(pwCurrent, pwNew);
    pwSaving = false;
    if (result.success) {
      pwCurrent = '';
      pwNew = '';
      pwConfirm = '';
      showToast('Password berhasil diganti', 'success');
    } else {
      pwError = result.error || 'Gagal mengganti password';
      showToast(pwError, 'error');
    }
  }

  $effect(() => { void loadStatus(); });
</script>

<PageHeader title="Keamanan" description="Verifikasi dua langkah (MFA) untuk akun Anda" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Keamanan' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadStatus} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="card p-6 max-w-2xl space-y-4" data-tour="security-settings">
  {#if loading}
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat status keamanan…</p>
  {:else if enabled}
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center shrink-0">
        <ShieldCheck class="w-5 h-5 text-green-600" />
      </div>
      <div class="flex-1">
        <h2 class="font-semibold">Verifikasi dua langkah aktif</h2>
        <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
          Akun Anda dilindungi dengan kode dari aplikasi authenticator saat login.
          {#if setupAt}Diaktifkan sejak {new Date(setupAt).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}.{/if}
        </p>
        <div class="mt-4">
          <Button variant="destructive" onclick={() => { code = ''; codes = Array(6).fill(''); showSetup = true; }} disabled={busy}>
            <ShieldOff class="w-4 h-4" /> Nonaktifkan MFA
          </Button>
        </div>
      </div>
    </div>
  {:else}
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 bg-[var(--color-kepin-blue)]/10 rounded-full flex items-center justify-center shrink-0">
        <KeyRound class="w-5 h-5 text-[var(--color-kepin-blue)]" />
      </div>
      <div class="flex-1">
        <h2 class="font-semibold">Verifikasi dua langkah belum aktif</h2>
        <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
          Tambahkan lapisan keamanan ekstra: setiap login memerlukan kode 6 digit dari aplikasi authenticator
          (Google Authenticator, Authy, 1Password, dan sejenisnya).
        </p>
        <div class="mt-4">
          <Button onclick={startSetup} loading={busy}><ShieldCheck class="w-4 h-4" /> Aktifkan MFA</Button>
        </div>
      </div>
    </div>
  {/if}
</div>

<div class="card p-6 max-w-2xl mt-6 space-y-4">
  <div class="flex items-start gap-4">
    <div class="w-10 h-10 bg-[var(--color-kepin-blue)]/10 rounded-full flex items-center justify-center shrink-0">
      <Lock class="w-5 h-5 text-[var(--color-kepin-blue)]" />
    </div>
    <div class="flex-1">
      <h2 class="font-semibold">Ganti Password</h2>
      <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
        Gunakan minimal 8 karakter. Sesi yang sudah aktif tetap berlaku sampai token kedaluwarsa.
      </p>
      <form onsubmit={(e) => { e.preventDefault(); void savePassword(); }} class="mt-4 space-y-4 max-w-sm">
        <div>
          <label class="label-text mb-1 block" for="pw-current">Password Saat Ini</label>
          <input id="pw-current" type="password" bind:value={pwCurrent} placeholder="Password saat ini" required class="input-field" />
        </div>
        <div>
          <label class="label-text mb-1 block" for="pw-new">Password Baru</label>
          <input id="pw-new" type="password" bind:value={pwNew} placeholder="Min. 8 karakter" required minlength={8} class="input-field" />
        </div>
        <div>
          <label class="label-text mb-1 block" for="pw-confirm">Konfirmasi Password Baru</label>
          <input id="pw-confirm" type="password" bind:value={pwConfirm} placeholder="Ulangi password baru" required class="input-field" />
        </div>
        {#if pwError}
          <p class="text-sm text-[var(--color-kepin-danger)]">{pwError}</p>
        {/if}
        <Button type="submit" loading={pwSaving}>Ganti Password</Button>
      </form>
    </div>
  </div>
</div>

{#if showSetup && !enabled}
  <Modal title="Aktifkan Verifikasi Dua Langkah" open={showSetup} onclose={() => showSetup = false}>
    <form onsubmit={(e) => { e.preventDefault(); void enableMfa(); }} class="space-y-4">
      <ol class="list-decimal pl-5 text-sm space-y-2 text-[hsl(var(--muted-foreground))]">
        <li>Buka aplikasi authenticator di ponsel Anda.</li>
        <li>Tambahkan akun baru, lalu pindai / masukkan kode berikut:</li>
      </ol>
      <div class="rounded-lg border border-dashed border-[hsl(var(--input))] p-4 text-center space-y-2">
        <p class="text-xs text-[hsl(var(--muted-foreground))]">Kode manual (base32)</p>
        <p class="font-mono text-sm tracking-widest break-all">{setupSecret}</p>
        <button
          type="button"
          onclick={() => { navigator.clipboard.writeText(setupSecret); showToast('Secret disalin', 'success'); }}
          class="text-xs text-[hsl(var(--primary))] hover:underline"
        >Salin secret</button>
        <details class="text-left">
          <summary class="text-xs cursor-pointer text-[hsl(var(--primary))]">Tampilkan URI otpauth</summary>
          <p class="font-mono text-[11px] break-all mt-2 text-[hsl(var(--muted-foreground))]">{setupUri}</p>
        </details>
      </div>
      <ol class="list-decimal pl-5 text-sm space-y-1 text-[hsl(var(--muted-foreground))]">
        <li value={3}>Masukkan kode 6 digit dari aplikasi untuk mengonfirmasi:</li>
      </ol>
      <div class="flex justify-center gap-2" onpaste={handlePaste}>
        {#each codes as _, i}
          <input
            id="setup-code-{i}"
            type="text"
            maxlength={1}
            bind:value={codes[i]}
            oninput={(e) => { handleInput(e, i); code = codes.join(''); }}
            class="w-10 h-12 text-center text-lg font-bold border border-[hsl(var(--input))] rounded focus-visible:outline-2 focus-visible:outline-[hsl(var(--ring))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
          />
        {/each}
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <Button variant="secondary" type="button" onclick={() => showSetup = false}>Batal</Button>
        <Button type="submit" loading={busy}>Aktifkan MFA</Button>
      </div>
    </form>
  </Modal>
{:else if showSetup && enabled}
  <Modal title="Nonaktifkan Verifikasi Dua Langkah" open={showSetup} onclose={() => { showSetup = false; }}>
    <form onsubmit={(e) => { e.preventDefault(); void disableMfa(); }} class="space-y-4">
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Masukkan kode 6 digit dari aplikasi authenticator untuk mengonfirmasi penonaktifan.</p>
      <div class="flex justify-center gap-2" onpaste={handlePaste}>
        {#each codes as _, i}
          <input
            id="setup-code-{i}"
            type="text"
            maxlength={1}
            bind:value={codes[i]}
            oninput={(e) => { handleInput(e, i); code = codes.join(''); }}
            class="w-10 h-12 text-center text-lg font-bold border border-[hsl(var(--input))] rounded focus-visible:outline-2 focus-visible:outline-[hsl(var(--ring))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
          />
        {/each}
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <Button variant="secondary" type="button" onclick={() => showSetup = false}>Batal</Button>
        <Button type="submit" loading={busy} variant="destructive">Nonaktifkan MFA</Button>
      </div>
    </form>
  </Modal>
{/if}

{#if showRecovery}
  <Modal title="Simpan Recovery Codes Anda" open={showRecovery} onclose={() => { showRecovery = false; }}>
    <div class="space-y-4">
      <p class="text-sm text-[hsl(var(--muted-foreground))]">
        Simpan kode berikut di tempat aman. Setiap kode hanya bisa digunakan <strong>sekali</strong>.
        Jika Anda kehilangan akses ke aplikasi authenticator, kode ini adalah satu-satunya cara masuk ke akun.
      </p>
      <div class="rounded-lg border border-[hsl(var(--input))] divide-y divide-[hsl(var(--input))]">
        {#each recoveryCodes as rc}
          <p class="px-4 py-2 font-mono text-sm text-center tracking-widest">{rc}</p>
        {/each}
      </div>
      <div class="flex justify-end gap-2">
        <Button variant="secondary" onclick={copyRecoveryCodes}>Salin Semua</Button>
        <Button onclick={() => { showRecovery = false; recoveryCodes = []; }}>Saya sudah menyimpannya</Button>
      </div>
    </div>
  </Modal>
{/if}
