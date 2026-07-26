<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { Shield, UserCog, Eye, Users } from '@lucide/svelte';

  const roles = [
    { name: 'Owner', icon: UserCog, users: 1, permissions: 'Semua akses termasuk billing dan manajemen anggota' },
    { name: 'Admin', icon: Shield, users: 1, permissions: 'Konfigurasi organisasi, kelola akses pengguna' },
    { name: 'Finance', icon: Eye, users: 2, permissions: 'Transaksi, jurnal, rekonsiliasi, dan laporan' },
    { name: 'Staff', icon: Users, users: 2, permissions: 'Input transaksi, invoice, dan stok sesuai izin' },
  ];
</script>

<PageHeader title="Peran & Izin" description="Kelola peran dan hak akses" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Peran' }]} />

<div class="space-y-3 max-w-2xl">
  {#each roles as role}
    <div class="card p-4 flex items-center gap-3">
      <role.icon class="w-6 h-6 text-[var(--color-kepin-blue)] shrink-0" />
      <div>
        <p class="font-medium text-sm">{role.name} ({role.users} pengguna)</p>
        <p class="text-xs text-[hsl(var(--muted-foreground))]">{role.permissions}</p>
      </div>
    </div>
  {/each}
</div>
