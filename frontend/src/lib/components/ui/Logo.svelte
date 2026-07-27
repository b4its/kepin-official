<script lang="ts">
  import { cn } from '$lib/utils/cn';

  type Props = {
    height?: number;
    class?: string;
    showText?: boolean;
  };

  let { height = 28, class: className = '', showText = true }: Props = $props();
</script>

<img
  src="/media/logo/kepin-light.png"
  alt="KePin"
  class={cn('dark:hidden', className)}
  style="height: {height}px; width: auto;"
/>
<img
  src="/media/logo/kepin-dark.png"
  alt="KePin"
  class={cn('hidden dark:block', className)}
  style="height: {height}px; width: auto;"
/>