<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const branches = [
    { name: 'Toko Pusat', code: 'PST', city: 'Jakarta', isMain: true, status: 'active' },
    { name: 'Cabang Bandung', code: 'BDG', city: 'Bandung', isMain: false, status: 'active' },
    { name: 'Cabang Surabaya', code: 'SBY', city: 'Surabaya', isMain: false, status: 'active' },
  ];
</script>

<PageHeader title="Cabang" description="Manajemen cabang bisnis" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Cabang' }]}>
  {#snippet actions()}
    <Button variant="secondary">+ Cabang Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama Cabang', sortable: true },
    { key: 'code', label: 'Kode' },
    { key: 'city', label: 'Kota' },
    { key: 'isMain', label: 'Pusat', render: (item: any) => item.isMain ? 'Ya' : 'Tidak' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={branches}
  total={3}
/>
