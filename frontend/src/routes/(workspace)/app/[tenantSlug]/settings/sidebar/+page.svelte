<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import {
    sidebarSettings,
    saveSidebarSettings,
    currentRole,
  } from '$lib/stores/data';
  import { clientNavigation } from '$lib/config/navigation';
  import { page } from '$app/stores';
  import { Eye, EyeOff, LayoutGrid, Lock, CheckSquare } from '@lucide/svelte';
  import { goto } from '$app/navigation';

  const slug = $derived($page.params.tenantSlug);
  const isOwner = $derived($currentRole === 'tenant_owner');

  // local copy to edit without immediate effect
  let localSettings = $state<Record<string, boolean>>({});
  let saved = $state(false);
  let saving = $state(false);

  // initialise from store when it loads
  $effect(() => {
    localSettings = { ...$sidebarSettings };
  });

  // redirect non-owners
  $effect(() => {
    if ($currentRole !== null && $currentRole !== 'tenant_owner') {
      goto(`/app/${slug}`);
    }
  });

  function isEnabled(key: string): boolean {
    return localSettings[key] !== false;
  }

  function toggle(key: string) {
    localSettings = { ...localSettings, [key]: !isEnabled(key) };
  }

  function enableAll() {
    const next: Record<string, boolean> = {};
    clientNavigation.forEach(g =>
      g.items.forEach(item => { if (!item.pinned) next[item.key] = true; })
    );
    localSettings = next;
  }

  function disableAll() {
    const next: Record<string, boolean> = {};
    clientNavigation.forEach(g =>
      g.items.forEach(item => { if (!item.pinned) next[item.key] = false; })
    );
    localSettings = next;
  }

  async function handleSave() {
    saving = true;
    try {
      await saveSidebarSettings(localSettings, slug);
      saved = true;
      setTimeout(() => (saved = false), 2500);
    } finally {
      saving = false;
    }
  }

  // count enabled non-pinned items
  const enabledCount = $derived(
    clientNavigation
      .flatMap(g => g.items)
      .filter(item => !item.pinned && isEnabled(item.key)).length
  );
  const totalCount = $derived(
    clientNavigation.flatMap(g => g.items).filter(item => !item.pinned).length
  );
</script>

<PageHeader
  title="Kustomisasi Sidebar"
  description="Aktifkan atau nonaktifkan menu yang tampil di sidebar untuk semua anggota organisasi ini"
  breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Kustomisasi Sidebar' }]}
>
  {#snippet actions()}
    <span class="text-xs text-[hsl(var(--muted-foreground))] self-center">
      {enabledCount}/{totalCount} menu aktif
    </span>
    <Button variant="secondary" size="sm" onclick={enableAll}>Aktifkan Semua</Button>
    <Button variant="secondary" size="sm" onclick={disableAll}>Nonaktifkan Semua</Button>
    <Button size="sm" onclick={handleSave} loading={saving} disabled={saving}>
      {saved ? '✓ Tersimpan' : 'Simpan Perubahan'}
    </Button>
  {/snippet}
</PageHeader>

{#if !isOwner && $currentRole !== null}
  <div class="card p-6 text-center text-sm text-[hsl(var(--muted-foreground))]">
    <Lock class="w-8 h-8 mx-auto mb-2 opacity-40" />
    Hanya <strong>tenant_owner</strong> yang dapat mengakses halaman ini.
  </div>
{:else}
  <!-- info banner -->
  <div class="rounded-lg border border-[hsl(var(--primary)/0.3)] bg-[hsl(var(--primary)/0.05)] px-4 py-3 mb-6 text-sm text-[hsl(var(--foreground))]">
    <strong>Catatan:</strong> Perubahan berlaku untuk semua anggota organisasi secara real-time. Menu yang dinonaktifkan tidak akan tampil di sidebar siapapun.
    Menu yang terkunci (<Lock class="w-3 h-3 inline mb-0.5" />) selalu tampil dan tidak dapat dinonaktifkan.
  </div>

  <div class="grid gap-5">
    {#each clientNavigation as group}
      <div class="card overflow-hidden">
        <!-- group header -->
        <div class="px-4 py-3 border-b border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.4)] flex items-center justify-between">
          <h3 class="text-sm font-semibold">{group.label}</h3>
          <span class="text-xs text-[hsl(var(--muted-foreground))]">
            {group.items.filter(i => i.pinned || isEnabled(i.key)).length}/{group.items.length} aktif
          </span>
        </div>

        <!-- items -->
        <div class="divide-y divide-[hsl(var(--border))]">
          {#each group.items as item}
            <div class="flex items-center justify-between px-4 py-3 transition-colors hover:bg-[hsl(var(--accent)/0.4)]">
              <div class="flex items-center gap-3">
                <item.icon class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
                <span class="text-sm font-medium">{item.label}</span>
                {#if item.pinned}
                  <span class="inline-flex items-center gap-1 text-[10px] text-[hsl(var(--muted-foreground))] border border-[hsl(var(--border))] rounded px-1.5 py-0.5">
                    <Lock class="w-2.5 h-2.5" /> Terkunci
                  </span>
                {/if}
              </div>

              {#if item.pinned}
                <!-- pinned — always on, not toggleable -->
                <div class="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
                  <Eye class="w-4 h-4" />
                  <span>Selalu aktif</span>
                </div>
              {:else}
                <!-- toggle button -->
                <button
                  onclick={() => toggle(item.key)}
                  class={[
                    'relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[hsl(var(--ring))]',
                    isEnabled(item.key)
                      ? 'bg-[hsl(var(--primary))]'
                      : 'bg-[hsl(var(--muted))]'
                  ].join(' ')}
                  role="switch"
                  aria-checked={isEnabled(item.key)}
                  aria-label={`${isEnabled(item.key) ? 'Nonaktifkan' : 'Aktifkan'} menu ${item.label}`}
                >
                  <span
                    class={[
                      'pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform',
                      isEnabled(item.key) ? 'translate-x-5' : 'translate-x-0'
                    ].join(' ')}
                  ></span>
                </button>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>

  <!-- sticky save bar at bottom -->
  <div class="sticky bottom-0 left-0 right-0 mt-6 -mx-3 sm:-mx-6 lg:-mx-8 px-3 sm:px-6 lg:px-8 py-3 bg-[hsl(var(--background)/0.9)] backdrop-blur border-t border-[hsl(var(--border))] flex items-center justify-between gap-3">
    <p class="text-xs text-[hsl(var(--muted-foreground))]">
      {enabledCount} dari {totalCount} menu diaktifkan
    </p>
    <div class="flex items-center gap-2">
      <Button variant="secondary" size="sm" onclick={enableAll}>Aktifkan Semua</Button>
      <Button size="sm" onclick={handleSave} loading={saving} disabled={saving}>
        {saved ? '✓ Tersimpan' : 'Simpan Perubahan'}
      </Button>
    </div>
  </div>
{/if}
