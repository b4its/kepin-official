<script lang="ts">
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  type Props = {
    labels: string[];
    values: number[];
    colors?: string[];
    height?: number;
    class?: string;
    donut?: boolean;
  };

  let { labels, values, colors, height = 200, class: className = '', donut = false }: Props = $props();

  function getColors() {
    const isDark = document.documentElement.classList.contains('dark');
    return { text: isDark ? '#a1a1aa' : '#71717a' };
  }

  function buildChart() {
    if (chart) chart.destroy();
    const c = getColors();
    const defaultColors = ['#059669', '#1559c7', '#f2c230', '#dc2626', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
    chart = new Chart(canvas, {
      type: donut ? 'doughnut' : 'pie',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors || defaultColors.slice(0, labels.length),
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: c.text, boxWidth: 12, padding: 12 } },
        },
        cutout: donut ? '60%' : undefined,
      },
    });
  }

  $effect(() => {
    if (!canvas) return;
    buildChart();
    const mo = new MutationObserver(() => buildChart());
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => { chart?.destroy(); mo.disconnect(); };
  });
</script>

<div class={className} style="height: {height}px">
  <canvas bind:this={canvas} />
</div>
