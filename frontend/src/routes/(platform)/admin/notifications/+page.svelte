<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { subscriberNotifs, type SubscriberNotif } from '$lib/stores/data';
  import { formatNumber } from '$lib/utils/currency';
  import { formatDateTime } from '$lib/utils/date';

  function goToTenant(slug: string) {
    window.location.href = `/app/${slug}`;
  }

  const statusLabel: Record<string, string> = {
    active: 'Aktif',
    expiring: 'Akan Berakhir',
    expired: 'Berakhir',
  };
</script>

<PageHeader title="Notifikasi Langganan" description="Pembelian langganan, perpanjangan, dan masa berlaku" />

<DataTable
  columns={[
    { key: 'tenantName', label: 'Tenant', sortable: true },
    { key: 'buyerName', label: 'Pembeli', sortable: true },
    { key: 'buyerEmail', label: 'Email' },
    { key: 'plan', label: 'Paket' },
    { key: 'amount', label: 'Biaya', align: 'right', render: (item: SubscriberNotif) => item.amount === 0 ? 'Gratis' : `Rp ${formatNumber(item.amount)}` },
    { key: 'joinedAt', label: 'Tanggal Join', render: (item: SubscriberNotif) => formatDateTime(item.joinedAt) },
    { key: 'expiresAt', label: 'Tanggal Berakhir', render: (item: SubscriberNotif) => formatDateTime(item.expiresAt) },
    { key: 'status', label: 'Status', render: (item: SubscriberNotif) => `<span class="badge-${item.status === 'active' ? 'success' : item.status === 'expiring' ? 'warning' : 'danger'}">${statusLabel[item.status]}</span>` },
  ]}
  data={$subscriberNotifs}
  total={$subscriberNotifs.length}
  rowLink={(item: SubscriberNotif) => `/app/${item.tenantSlug}`}
  searchable={true}
/>
