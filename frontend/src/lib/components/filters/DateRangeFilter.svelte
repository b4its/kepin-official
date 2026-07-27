<script lang="ts">
  import type { Preset } from '$lib/utils/dateRange';
  import { presetLabels } from '$lib/utils/dateRange';

  type Props = {
    onChange?: (preset: Preset, startDate: string, endDate: string) => void;
  };

  let { onChange }: Props = $props();

  let preset = $state<Preset>('1week');
  let customStart = $state('');
  let customEnd = $state('');

  function selectPreset(p: Preset) {
    preset = p;
    if (p !== 'custom') {
      const now = new Date();
      const end = now.toISOString().slice(0, 10);
      const days = { '1week': 7, '2week': 14, '3week': 21, '1month': 30 }[p] ?? 7;
      const start = new Date(now.getTime() - days * 86400000).toISOString().slice(0, 10);
      onChange?.(p, start, end);
    }
  }

  function applyCustom() {
    if (customStart && customEnd) {
      onChange?.('custom', customStart, customEnd);
    }
  }
</script>

<div class="flex flex-wrap items-center gap-2">
  {#each Object.entries(presetLabels) as [key, label]}
    <button
      onclick={() => selectPreset(key as Preset)}
      class="px-3 py-1.5 text-xs rounded-md transition-colors border"
      class:bg-[hsl(var(--primary))]={preset === key}
      class:text-white={preset === key}
      class:border-[hsl(var(--primary))]={preset === key}
      class:bg-transparent={preset !== key}
      class:border-[hsl(var(--border))]={preset !== key}
      class:text-[hsl(var(--muted-foreground))]={preset !== key}
    >
      {label}
    </button>
  {/each}
  {#if preset === 'custom'}
    <div class="flex items-center gap-2">
      <input
        type="date"
        bind:value={customStart}
        class="input-field text-xs h-8 px-2 w-36"
      />
      <span class="text-xs text-[hsl(var(--muted-foreground))]">s/d</span>
      <input
        type="date"
        bind:value={customEnd}
        class="input-field text-xs h-8 px-2 w-36"
      />
      <button onclick={applyCustom} class="px-3 py-1.5 text-xs rounded-md bg-[hsl(var(--primary))] text-white">Terapkan</button>
    </div>
  {/if}
</div>
