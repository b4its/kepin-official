<script lang="ts">
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  type Props = {
    labels: string[];
    datasets: { label: string; data: number[]; color?: string }[];
    height?: number;
    class?: string;
    yFormat?: 'currency' | 'number';
  };

  let { labels, datasets, height = 200, class: className = '', yFormat = 'number' }: Props = $props();

  function getColors() {
    const isDark = document.documentElement.classList.contains('dark');
    return {
      grid: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
      text: isDark ? '#a1a1aa' : '#71717a',
    };
  }

  function formatY(val: number | null) {
    if (val == null) return '';
    if (yFormat === 'currency') return `Rp ${(val / 1000).toFixed(0)}rb`;
    return val.toLocaleString('id-ID');
  }

  function buildChart() {
    if (chart) chart.destroy();
    const c = getColors();
    const defaultColors = ['#059669', '#1559c7', '#f2c230', '#dc2626', '#8b5cf6', '#ec4899'];
    chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: datasets.map((d, i) => ({
          label: d.label,
          data: d.data,
          backgroundColor: d.color || defaultColors[i % defaultColors.length],
          borderRadius: 4,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: datasets.length > 1, labels: { color: c.text, boxWidth: 12, padding: 12 } },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed.y;
                if (val == null) return '';
                return `${ctx.dataset.label}: ${yFormat === 'currency' ? `Rp ${val.toLocaleString('id-ID')}` : val.toLocaleString('id-ID')}`;
              },
            },
          },
        },
        scales: {
          x: { ticks: { color: c.text }, grid: { color: c.grid } },
          y: { ticks: { color: c.text, callback: (val: string | number) => typeof val === 'number' ? formatY(val) : '' }, grid: { color: c.grid } },
        },
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
