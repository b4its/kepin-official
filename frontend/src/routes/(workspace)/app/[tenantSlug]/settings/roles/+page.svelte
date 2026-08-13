<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { tenantApi } from '$lib/stores/data';
  import { Shield, UserCog } from '@lucide/svelte';

  type Role = { id: string; name: string };

  const slug = $derived($page.params.tenantSlug || '');
  let roles = $state<Role[]>([]);
  let loading = $state(false);
  let error = $state('');

  async function loadRoles() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      roles = await tenantApi.getRoles(slug) as Role[];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat role';
    } finally {
      loading = false;
    }
  }

  function description(roleId: string) {
    return roleId === 'tenant_owner'
      ? 'Semua akses organisasi, anggota, sidebar, billing, dan proses tutup buku.'
      : 'Akses operasional standar sesuai izin backend; aksi owner-only disembunyikan.';
  }

  $effect(() => { if (slug) void loadRoles(); });
</script>

<PageHeader title="Peran & Izin" description="Role aktif dari backend" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Peran' }]} />

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="space-y-3 max-w-2xl" data-tour="roles-list">
  {#if loading}
    {#each Array(2) as _}
      <div class="card p-4"><div class="skeleton h-10 w-full"></div></div>
    {/each}
  {:else}
    {#each roles as role}
      <div class="card p-4 flex items-center gap-3">
        {#if role.id === 'tenant_owner'}
          <UserCog class="w-6 h-6 text-[var(--color-kepin-blue)] shrink-0" />
        {:else}
          <Shield class="w-6 h-6 text-[var(--color-kepin-blue)] shrink-0" />
        {/if}
        <div>
          <p class="font-medium text-sm">{role.name}</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">{description(role.id)}</p>
        </div>
      </div>
    {:else}
      <div class="card p-4 text-sm text-[hsl(var(--muted-foreground))]">Backend belum mengembalikan role.</div>
    {/each}
  {/if}
</div>
