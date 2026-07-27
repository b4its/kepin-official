<script lang="ts">
  import { stockMovements } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';
</script>

<PageHeader title="Pergerakan Stok" description="Riwayat pergerakan inventaris" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Pergerakan' }]} />

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
