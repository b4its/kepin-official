<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils/cn';

  type Props = {
    variant?: 'primary' | 'secondary' | 'ghost' | 'destructive';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    disabled?: boolean;
    class?: string;
    href?: string;
    /** Hook unik untuk panduan tur (driver.js). */
    tourHook?: string;
    children: Snippet;
    onclick?: (e: MouseEvent) => void;
    type?: 'button' | 'submit' | 'reset';
  };

  let {
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    class: className = '',
    href,
    tourHook,
    children,
    onclick,
    type = 'button',
    ...rest
  }: Props = $props();

  const baseClass = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 whitespace-nowrap focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[hsl(var(--ring))] disabled:opacity-50 disabled:cursor-not-allowed';

  const variants: Record<string, string> = {
    primary: 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] border border-[hsl(var(--primary))] hover:opacity-90',
    secondary: 'bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))] border border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]',
    ghost: 'bg-transparent text-[hsl(var(--foreground))] border border-transparent hover:bg-[hsl(var(--accent))]',
    destructive: 'bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))] border border-[hsl(var(--destructive))] hover:opacity-90',
  };

  const sizes: Record<string, string> = {
    sm: 'px-3 py-1 text-xs h-8',
    md: 'px-4 py-2 text-sm h-10',
    lg: 'px-6 py-3 text-base h-12',
  };
</script>

{#if href}
  <a
    href={href}
    data-tour={tourHook}
    class={cn(baseClass, variants[variant], sizes[size], className)}
    {...rest}
  >
    {#if loading}
      <span class="sr-only">Memproses</span>
    {/if}
    {@render children()}
  </a>
{:else}
  <button
      type={type}
      disabled={disabled || loading}
      data-tour={tourHook}
    aria-busy={loading}
    class={cn(baseClass, variants[variant], sizes[size], className)}
    {onclick}
    {...rest}
  >
    {#if loading}
      <span class="sr-only">Memproses</span>
    {/if}
    {@render children()}
  </button>
{/if}
