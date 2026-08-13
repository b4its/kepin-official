<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { inventoryLocations, loadStockMovements, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Boxes, Minus, Plus, Search, Trash2 } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  let stockMap = $state<Record<string, number>>({});
  let cart = $state<Record<string, number>>({});
  let search = $state('');
  let catalog = $state<any[]>([]);
  let known = $state<Record<string, any>>({});
  let pageNo = $state(1);
  let catalogTotal = $state(0);
  let catalogLoading = $state(false);
  const PAGE_SIZE = 24;
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  let stockProduct = $state<any | null>(null);
  let stockMode = $state<'in' | 'out'>('in');
  let stockQty = $state(1);
  let stockReason = $state('');
  let stockSaving = $state(false);
  let checkoutSaving = $state(false);

  async function refreshStock() {
    try {
      const res: any = await tenantApi.getStockBalances(slug);
      const map: Record<string, number> = {};
      for (const sb of Array.isArray(res) ? res : []) {
        const pid = sb.productId || sb.product_id;
        map[pid] = (map[pid] || 0) + parseFloat(sb.quantity || '0');
      }
      stockMap = map;
      void loadStockMovements(slug);
    } catch {
      /* biarkan data lama */
    }
  }

  function mapProduct(p: any) {
    return {
      id: p.id,
      sku: p.sku || '',
      name: p.name,
      category: p.category || '',
      unit: p.unit || 'pcs',
      price: parseFloat(p.salePrice || p.sale_price || '0'),
      cost: parseFloat(p.costPrice || p.cost_price || '0'),
      stock: parseFloat(p.stock || '0'),
      minStock: parseFloat(p.minimumStock || p.minimum_stock || '0'),
      location: p.location || '',
      status: p.status,
    };
  }

  async function loadCatalog(q = search, p = pageNo) {
    catalogLoading = true;
    try {
      const res: any = await tenantApi.getProducts(slug, q || undefined, PAGE_SIZE, p);
      const items = Array.isArray(res.items) ? res.items : [];
      catalog = items.map(mapProduct);
      catalogTotal = res.total ?? 0;
      const next = { ...known };
      for (const item of catalog) next[item.id] = item;
      known = next;
    } catch {
      /* biarkan data lama */
    } finally {
      catalogLoading = false;
    }
  }

  function productOf(pid: string) {
    return known[pid];
  }

  const totalPages = $derived(Math.max(1, Math.ceil(catalogTotal / PAGE_SIZE)));

  function goToPage(p: number) {
    if (p < 1 || p > totalPages || p === pageNo) return;
    pageNo = p;
    void loadCatalog(search, p);
    document.querySelector('main')?.scrollTo({ top: 0 });
  }

  $effect(() => {
    if (slug) void refreshStock();
  });

  $effect(() => {
    if (!slug) return;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      pageNo = 1;
      void loadCatalog(search, 1);
    }, search ? 250 : 0);
    return () => clearTimeout(searchTimer);
  });

  const locationId = $derived(
    $inventoryLocations.find((l) => l.status === 'active')?.id ||
      $inventoryLocations[0]?.id ||
      ''
  );

  const cartEntries = $derived(Object.entries(cart));
  const cartCount = $derived(cartEntries.reduce((s, [, qty]) => s + qty, 0));
  const cartTotal = $derived(
    cartEntries.reduce((sum, [pid, qty]) => {
      return sum + qty * (productOf(pid)?.price || 0);
    }, 0)
  );

  function addToCart(pid: string) {
    cart = { ...cart, [pid]: (cart[pid] || 0) + 1 };
  }

  function changeQty(pid: string, delta: number) {
    const next = (cart[pid] || 0) + delta;
    const nextCart = { ...cart };
    if (next <= 0) delete nextCart[pid];
    else nextCart[pid] = next;
    cart = nextCart;
  }

  function removeFromCart(pid: string) {
    const nextCart = { ...cart };
    delete nextCart[pid];
    cart = nextCart;
  }

  function openStock(p: any) {
    stockProduct = p;
    stockMode = 'in';
    stockQty = 1;
    stockReason = '';
  }

  function stockOf(p: any): number {
    return stockMap[p.id] ?? p.stock ?? 0;
  }

  async function saveStock() {
    if (!stockProduct || !locationId) {
      showToast('Tidak ada lokasi inventaris aktif', 'error');
      return;
    }
    const qty = Number(stockQty);
    if (!Number.isFinite(qty) || qty <= 0) {
      showToast('Jumlah harus lebih dari 0', 'error');
      return;
    }
    stockSaving = true;
    try {
      if (stockMode === 'in') {
        await tenantApi.createStockReceipt(slug, {
          productId: stockProduct.id,
          locationId,
          quantity: String(qty),
          unitCost: String(stockProduct.cost || '0'),
          reason: stockReason || 'Penambahan stok manual (POS)',
        });
      } else {
        await tenantApi.createStockIssue(slug, {
          productId: stockProduct.id,
          locationId,
          quantity: String(qty),
          reason: stockReason || 'Pengurangan stok manual (POS)',
        });
      }
      showToast(
        `Stok ${stockProduct.name} ${stockMode === 'in' ? 'ditambah' : 'dikurangi'} ${qty} ${stockProduct.unit || 'pcs'}`,
        'success'
      );
      stockProduct = null;
      await refreshStock();
    } catch (err: any) {
      showToast(err?.message || 'Gagal mengubah stok', 'error');
    } finally {
      stockSaving = false;
    }
  }

  async function checkout() {
    const items = cartEntries.map(([pid, qty]) => ({ product_id: pid, quantity: String(qty) }));
    if (!items.length) return;
    checkoutSaving = true;
    try {
      const res: any = await tenantApi.createPosCheckout(slug, { items });
      showToast(`Checkout ${res.checkoutNumber || 'POS'} berhasil — stok terpotong & tercatat`, 'success');
      cart = {};
      await refreshStock();
    } catch (err: any) {
      showToast(err?.message || 'Gagal checkout', 'error');
    } finally {
      checkoutSaving = false;
    }
  }
</script>

<PageHeader title="Point of Sales" description="Kasir — produk dari workspace Anda, stok terkelola otomatis" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Point of Sales' }]}>
</PageHeader>

<div class="grid lg:grid-cols-3 gap-6">
  <div class="lg:col-span-2">
    <div class="flex items-center gap-2 mb-4 card px-3 py-2">
      <Search class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
      <input
        type="search"
        bind:value={search}
        placeholder="Cari produk, SKU, kategori..."
        class="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-[hsl(var(--muted-foreground))]"
      />
    </div>

    {#if catalog.length === 0}
      <div class="card p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
        Tidak ada produk. Tambahkan produk di menu Inventaris → Produk.
      </div>
    {:else}
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {#each catalog as p}
          <div class="card p-4 flex flex-col gap-3">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="text-sm font-semibold truncate">{p.name}</p>
                <p class="text-xs text-[hsl(var(--muted-foreground))]">{p.sku}</p>
              </div>
              {#if stockOf(p) <= 0}
                <span class="badge-danger text-[10px]">Habis</span>
              {:else if stockOf(p) <= p.minStock}
                <span class="badge-warning text-[10px]">Stok {stockOf(p)}</span>
              {:else}
                <span class="badge-success text-[10px]">Stok {stockOf(p)}</span>
              {/if}
            </div>
            <p class="text-sm font-semibold tabular-nums">{formatIDR(p.price)}</p>
            <div class="flex gap-2">
              <Button size="sm" class="flex-1" onclick={() => addToCart(p.id)}>
                <Plus class="w-3.5 h-3.5" /> Keranjang
              </Button>
              <Button size="sm" variant="secondary" onclick={() => openStock(p)}>
                <Boxes class="w-3.5 h-3.5" /> Stok
              </Button>
            </div>
          </div>
        {/each}
      </div>
      <div class="flex items-center justify-between mt-4 text-xs text-[hsl(var(--muted-foreground))]">
        <span>Menampilkan {catalog.length} dari {catalogTotal} produk</span>
        <div class="flex items-center gap-1">
          <button
            class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
            disabled={pageNo <= 1 || catalogLoading}
            onclick={() => goToPage(pageNo - 1)}
          >Sebelumnya</button>
          <span class="px-2 tabular-nums">Halaman {pageNo} / {totalPages}</span>
          <button
            class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
            disabled={pageNo >= totalPages || catalogLoading}
            onclick={() => goToPage(pageNo + 1)}
          >Berikutnya</button>
        </div>
      </div>
    {/if}
  </div>

  <div class="lg:sticky lg:top-4 h-fit">
    <div class="card p-5">
      <h3 class="font-semibold mb-3">Keranjang ({cartCount})</h3>
      {#if cartEntries.length === 0}
        <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">
          Belum ada item. Klik "+ Keranjang" pada produk.
        </p>
      {:else}
        <div class="space-y-3 mb-4 max-h-72 overflow-y-auto pr-1">
          {#each cartEntries as [pid, qty]}
            {#if productOf(pid)}
              <div class="flex items-center justify-between gap-2 border-b border-[hsl(var(--border))] pb-2">
                <div class="min-w-0">
                  <p class="text-sm font-medium truncate">{productOf(pid)?.name}</p>
                  <p class="text-xs text-[hsl(var(--muted-foreground))] tabular-nums">
                    {formatIDR((productOf(pid)?.price || 0) * qty)}
                  </p>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                  <button
                    class="p-1 rounded hover:bg-[hsl(var(--accent))]"
                    onclick={() => changeQty(pid, -1)}
                    aria-label="Kurangi jumlah"
                  >
                    <Minus class="w-3.5 h-3.5" />
                  </button>
                  <span class="w-8 text-center text-sm tabular-nums">{qty}</span>
                  <button
                    class="p-1 rounded hover:bg-[hsl(var(--accent))]"
                    onclick={() => changeQty(pid, 1)}
                    aria-label="Tambah jumlah"
                  >
                    <Plus class="w-3.5 h-3.5" />
                  </button>
                  <button
                    class="p-1 rounded hover:bg-[hsl(var(--accent))] text-[var(--color-kepin-danger)]"
                    onclick={() => removeFromCart(pid)}
                    aria-label="Hapus item"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            {/if}
          {/each}
        </div>
      {/if}

      <div class="flex items-center justify-between border-t border-[hsl(var(--border))] pt-3 mb-4">
        <span class="text-sm text-[hsl(var(--muted-foreground))]">Total</span>
        <span class="text-lg font-semibold tabular-nums">{formatIDR(cartTotal)}</span>
      </div>

      <Button class="w-full" disabled={cartEntries.length === 0} loading={checkoutSaving} onclick={checkout}>
        Bayar & Kurangi Stok
      </Button>
      <p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">
        Checkout memotong stok secara otomatis dan tercatat di halaman Pergerakan Stok.
      </p>
    </div>
  </div>
</div>

<Modal
  title={stockProduct ? `Atur Stok — ${stockProduct.name}` : 'Atur Stok'}
  open={stockProduct !== null}
  onclose={() => stockProduct = null}
  size="sm"
>
  {#if stockProduct}
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-2">
        <button
          class="rounded-md border px-3 py-2 text-sm font-medium transition-colors {stockMode === 'in' ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]' : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]'}"
          onclick={() => stockMode = 'in'}
        >
          + Tambah stok
        </button>
        <button
          class="rounded-md border px-3 py-2 text-sm font-medium transition-colors {stockMode === 'out' ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]' : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]'}"
          onclick={() => stockMode = 'out'}
        >
          − Kurangi stok
        </button>
      </div>

      <div>
        <label class="label-text">Jumlah ({stockProduct.unit || 'pcs'})</label>
        <input type="number" min="1" step="1" bind:value={stockQty} class="input-field mt-1" aria-label="Jumlah stok" />
      </div>

      <div>
        <label class="label-text">Alasan (opsional)</label>
        <input type="text" bind:value={stockReason} class="input-field mt-1" placeholder="cth: stok masuk dari supplier" />
      </div>

      <p class="text-xs text-[hsl(var(--muted-foreground))]">
        Stok saat ini: <span class="font-medium tabular-nums">{stockOf(stockProduct)}</span> {stockProduct.unit || 'pcs'}
        {#if stockMode === 'in'}→ menjadi <span class="font-medium tabular-nums">{stockOf(stockProduct) + (Number(stockQty) || 0)}</span>{:else}→ menjadi <span class="font-medium tabular-nums">{Math.max(0, stockOf(stockProduct) - (Number(stockQty) || 0))}</span>{/if}
      </p>

      <div class="flex justify-end gap-2 pt-2">
        <Button variant="secondary" onclick={() => stockProduct = null}>Batal</Button>
        <Button onclick={saveStock} loading={stockSaving}>
          {stockMode === 'in' ? 'Tambah Stok' : 'Kurangi Stok'}
        </Button>
      </div>
    </div>
  {/if}
</Modal>