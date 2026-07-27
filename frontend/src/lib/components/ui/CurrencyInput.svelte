<script lang="ts">
  type Props = {
    value?: number;
    onchange?: (value: number) => void;
    required?: boolean;
    disabled?: boolean;
    placeholder?: string;
    class?: string;
  };

  let { value = 0, onchange, required = false, disabled = false, placeholder = '0', class: className = '' }: Props = $props();

  function format(n: number): string {
    return n.toLocaleString('id-ID');
  }

  let display = $state(format(value));

  function handleInput(e: Event) {
    const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
    const num = raw === '' ? 0 : parseInt(raw, 10);
    display = raw === '' ? '' : format(num);
    onchange?.(num);
  }

  function handleBlur() {
    if (display === '' || display === '0') {
      display = '0';
      onchange?.(0);
    }
  }

  $effect(() => {
    display = format(value);
  });
</script>

<input
  type="text"
  inputmode="numeric"
  value={display}
  oninput={handleInput}
  onblur={handleBlur}
  {required}
  {disabled}
  {placeholder}
  class={className}
/>
