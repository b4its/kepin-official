<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { mainTour, tourPageLabels, groupStepsByPhase } from '$lib/config/tour';
  import { requestTourStart, stepUrl } from '$lib/stores/tour';
  import { Play, MousePointerClick, MapPin, ListOrdered, CheckCircle2, BookOpen } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  const totalSteps = mainTour.steps.length;
  const totalPages = $derived(new Set(mainTour.steps.map((s) => s.page)).size);
  const groups = $derived(groupStepsByPhase(mainTour));

  function labelOf(pageKey: string): string {
    return tourPageLabels[pageKey] || pageKey || 'Dashboard';
  }

  function startTourFrom(index: number) {
    requestTourStart(mainTour, index);
    const target = stepUrl(mainTour.steps[index], slug);
    if ($page.url.pathname !== target) {
      setTimeout(() => { void goto(target); }, 100);
    }
  }
</script>

<PageHeader
  title="Tutorial"
  description="Panduan langkah demi langkah seluruh aplikasi KePin — dari halaman awal hingga pengaturan lengkap."
  breadcrumbs={[{ label: 'Bantuan' }, { label: 'Tutorial' }]}
/>

<!-- Hero -->
<div class="card mb-6 p-6 sm:p-8 relative overflow-hidden">
  <div class="max-w-3xl">
    <Badge variant="info" class="mb-3">
      <MousePointerClick class="w-3 h-3 mr-1" /> Tur interaktif dengan Driver.js
    </Badge>
    <h2 class="text-2xl sm:text-3xl font-bold mb-2">Jelajahi KePin Langkah demi Langkah</h2>
    <p class="text-sm sm:text-base text-[hsl(var(--muted-foreground))] leading-relaxed mb-4">
      Tutorial ini berjalan langsung di aplikasi: setiap langkah menyorot elemen asli di layar
      (tombol, formulir, tabel) dengan penjelasan lengkap. Tur berjalan menyeluruh dari halaman
      awal, login, hingga seluruh modul workspace — klik <b>Lanjut</b> untuk berpindah langkah,
      dan <b>Kembali</b> untuk mengulang.
    </p>
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <Button size="lg" onclick={() => startTourFrom(0)}>
        <Play class="w-4 h-4" /> Mulai Tur dari Awal
      </Button>
      <div class="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
        <span class="inline-flex items-center gap-1.5"><ListOrdered class="w-4 h-4" /> {totalSteps} langkah</span>
        <span class="inline-flex items-center gap-1.5"><MapPin class="w-4 h-4" /> {totalPages} halaman</span>
        <span class="inline-flex items-center gap-1.5"><BookOpen class="w-4 h-4" /> {mainTour.phases.length} bab</span>
      </div>
    </div>
    <div class="grid sm:grid-cols-3 gap-3 text-sm">
      <div class="rounded-lg bg-[hsl(var(--muted))]/50 p-3 flex gap-2">
        <CheckCircle2 class="w-4 h-4 shrink-0 text-[hsl(var(--primary))] mt-0.5" />
        <p class="text-[hsl(var(--muted-foreground))]">Ikuti berurutan dari langkah 1, atau mulai langsung dari bagian yang Anda butuhkan.</p>
      </div>
      <div class="rounded-lg bg-[hsl(var(--muted))]/50 p-3 flex gap-2">
        <MousePointerClick class="w-4 h-4 shrink-0 text-[hsl(var(--primary))] mt-0.5" />
        <p class="text-[hsl(var(--muted-foreground))]">Tur otomatis berpindah halaman dan menunggu konten dimuat sebelum menyorot elemen.</p>
      </div>
      <div class="rounded-lg bg-[hsl(var(--muted))]/50 p-3 flex gap-2">
        <CheckCircle2 class="w-4 h-4 shrink-0 text-[hsl(var(--primary))] mt-0.5" />
        <p class="text-[hsl(var(--muted-foreground))]">Bisa diulang kapan saja — dari ikon <b>?</b> di bilah atas atau menu Tutorial di sidebar.</p>
      </div>
    </div>
  </div>
</div>

<!-- Langkah-langkah per bab -->
{#each mainTour.phases as phase}
  {#if (groups.get(phase.key) || []).length > 0}
    <section class="mb-8">
      <div class="flex items-center gap-3 mb-3">
        <h2 class="text-lg font-bold">{phase.label}</h2>
        <span class="text-xs text-[hsl(var(--muted-foreground))]">{(groups.get(phase.key) || []).length} langkah</span>
      </div>
      <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">{phase.description}</p>

      <div class="space-y-3">
        {#each groups.get(phase.key) || [] as step, i}
          {@const globalIndex = mainTour.steps.indexOf(step)}
          <div class="card p-4 sm:p-5 flex flex-col sm:flex-row sm:items-start gap-4">
            <div
              class="w-10 h-10 shrink-0 rounded-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] flex items-center justify-center font-bold text-sm"
            >
              {globalIndex + 1}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <h3 class="font-semibold">{step.title}</h3>
                <Badge variant="neutral">{labelOf(step.page)}</Badge>
                {#if step.element}
                  <Badge variant="info">menyorot elemen</Badge>
                {/if}
              </div>
              <p class="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">{step.description}</p>
            </div>
            <div class="sm:shrink-0">
              <Button variant="secondary" size="sm" onclick={() => startTourFrom(globalIndex)}>
                <Play class="w-3.5 h-3.5" /> Mulai dari sini
              </Button>
            </div>
          </div>
        {/each}
      </div>
    </section>
  {/if}
{/each}

<div class="card p-6 text-center mb-4">
  <h2 class="text-lg font-bold mb-1">Siap memulai?</h2>
  <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">
    Jalankan tur penuh dari awal dan kuasai KePin dalam hitungan menit.
  </p>
  <Button size="lg" onclick={() => startTourFrom(0)}>
    <Play class="w-4 h-4" /> Mulai Tur dari Awal
  </Button>
</div>
