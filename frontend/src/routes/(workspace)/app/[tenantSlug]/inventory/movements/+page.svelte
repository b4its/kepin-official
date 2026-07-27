<script lang="ts">
  import { stockMovements } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { Download } from '@lucide/svelte';

  let showExport = $state(false);

  const exportColumns = [
    { key: 'date', label: 'Tanggal' },
    { key: 'productName', label: 'Produk' },
    { key: 'type', label: 'Tipe' },
    { key: 'quantity', label: 'Qty' },
    { key: 'beforeStock', label: 'Stok Awal' },
    { key: 'afterStock', label: 'Stok Akhir' },
    { key: 'reason', label: 'Alasan' },
  ];
</script>

<PageHeader title="Pergerakan Stok" description="Riwayat pergerakan inventaris" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Pergerakan' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'productName', label: 'Produk', sortable: true },
    { key: 'type', label: 'Tipe', render: (item: any) => `<span class="badge-${item.type}">${item.type}</span>` },
    { key: 'quantity', label: 'Qty', align: 'right' },
    { key: 'beforeStock', label: 'Stok Awal', align: 'right' },
    { key: 'afterStock', label: 'Stok Akhir', align: 'right' },
    { key: 'reason', label: 'Alasan' },
  ]}
  data={$stockMovements}
  total={256}
  page={1}
  pageSize={5}
  searchable={true}
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Pergerakan Stok"
  subtitle="Riwayat mutasi inventaris"
  columns={exportColumns}
  rows={$stockMovements}
  filename="pergerakan-stok"
/>
