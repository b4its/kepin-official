<script lang="ts">
  import { cn } from '$lib/utils/cn';

  type Props = {
    value?: string;
    onchange?: (e: Event) => void;
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    name?: string;
    class?: string;
    error?: string;
    options: { value: string; label: string }[];
  };

  let {
    value = '',
    onchange,
    placeholder = 'Pilih...',
    disabled = false,
    required = false,
    name,
    class: className = '',
    error,
    options,
    ...rest
  }: Props = $props();
</script>

<select
  {name}
  {value}
  {disabled}
  {required}
  {onchange}
  aria-invalid={!!error}
  class={cn(
    'flex h-10 w-full rounded border bg-[hsl(var(--background))] px-3 py-2 text-sm text-[hsl(var(--foreground))] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[hsl(var(--ring))] disabled:opacity-50 disabled:cursor-not-allowed',
    error ? 'border-[hsl(var(--destructive))]' : 'border-[hsl(var(--input))]',
    className
  )}
  {...rest}
>
  <option value="" disabled>{placeholder}</option>
  {#each options as option}
    <option value={option.value}>{option.label}</option>
  {/each}
</select>
