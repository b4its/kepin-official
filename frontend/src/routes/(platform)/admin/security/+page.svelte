<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { Shield, CheckCircle, XCircle } from '@lucide/svelte';
  import { adminTenants } from '$lib/stores/data';

  const checks = [
    { name: 'Audit Trail', status: 'active', desc: 'Semua tenant mencatat audit event' },
    { name: 'MFA Adoption', status: 'warning', desc: '65% pengguna telah mengaktifkan MFA' },
    { name: 'Session Management', status: 'active', desc: 'Tidak ada session mencurigakan' },
    { name: 'Encryption', status: 'active', desc: 'TLS 1.3 dan AES-256 aktif' },
    { name: 'API Rate Limit', status: 'active', desc: 'Tidak ada anomali traffic' },
  ];
</script>

<PageHeader title="Keamanan Platform" description="Status keamanan dan kepatuhan" />

<div class="space-y-3">
  {#each checks as check}
    <div class="card p-4 flex items-center gap-3">
      {#if check.status === 'active'}
        <CheckCircle class="w-5 h-5 text-[var(--color-kepin-green)] shrink-0" />
      {:else}
        <XCircle class="w-5 h-5 text-[var(--color-kepin-yellow)] shrink-0" />
      {/if}
      <div>
        <p class="font-medium text-sm">{check.name}</p>
        <p class="text-xs text-[hsl(var(--muted-foreground))]">{check.desc}</p>
      </div>
    </div>
  {/each}
</div>
