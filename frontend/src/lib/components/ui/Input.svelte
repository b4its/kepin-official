<script lang="ts">
  import { cn } from '$lib/utils/cn';

  type Props = {
    value?: string;
    oninput?: (e: Event) => void;
    placeholder?: string;
    type?: string;
    disabled?: boolean;
    required?: boolean;
    name?: string;
    class?: string;
    error?: string;
  };

  let {
    value = '',
    oninput,
    placeholder = '',
    type = 'text',
    disabled = false,
    required = false,
    name,
    class: className = '',
    error,
    ...rest
  }: Props = $props();
</script>

<input
  {type}
  {name}
  {value}
  {placeholder}
  {disabled}
  {required}
  {oninput}
  aria-invalid={!!error}
  aria-describedby={error ? `${name}-error` : undefined}
  class={cn(
    'flex h-10 w-full rounded border bg-[hsl(var(--background))] px-3 py-2 text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[hsl(var(--ring))] disabled:opacity-50 disabled:cursor-not-allowed',
    error ? 'border-[hsl(var(--destructive))]' : 'border-[hsl(var(--input))]',
    className
  )}
  {...rest}
/>
