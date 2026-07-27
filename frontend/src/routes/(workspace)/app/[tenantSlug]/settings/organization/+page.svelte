<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let companyName = $state('Toko Maju Jaya');
  let legalName = $state('UD Toko Maju Jaya');
  let sector = $state('Ritel');
  let timezone = $state('Asia/Jakarta');

  let showModal = $state(false);
  let editForm = $state({ companyName: '', legalName: '', sector: '', timezone: '' });

  function openEdit() {
    editForm = { companyName, legalName, sector, timezone };
    showModal = true;
  }

  function save() {
    companyName = editForm.companyName;
    legalName = editForm.legalName;
    sector = editForm.sector;
    timezone = editForm.timezone;
    showModal = false;
  }
</script>

<PageHeader title="Organisasi" description="Profil dan pengaturan organisasi" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Organisasi' }]}>
  {#snippet actions()}
    <Button onclick={openEdit}>Edit Profil</Button>
  {/snippet}
</PageHeader>

<div class="card p-6 max-w-2xl space-y-4">
  <div class="grid sm:grid-cols-2 gap-4">
    <div>
      <p class="label-text mb-1">Nama Tampilan</p>
      <p class="text-sm">{companyName}</p>
    </div>
    <div>
      <p class="label-text mb-1">Nama Legal</p>
      <p class="text-sm">{legalName}</p>
    </div>
    <div>
      <p class="label-text mb-1">Sektor</p>
      <p class="text-sm">{sector}</p>
    </div>
    <div>
      <p class="label-text mb-1">Zona Waktu</p>
      <p class="text-sm">{timezone}</p>
    </div>
  </div>
</div>

<Modal title="Edit Profil Organisasi" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Nama Tampilan</label>
        <input type="text" bind:value={editForm.companyName} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Nama Legal</label>
        <input type="text" bind:value={editForm.legalName} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Sektor</label>
        <select bind:value={editForm.sector} class="input-field mt-1">
          <option value="Ritel">Ritel</option>
          <option value="F&B">F&B</option>
          <option value="Manufaktur">Manufaktur</option>
          <option value="Jasa">Jasa</option>
        </select>
      </div>
      <div>
        <label class="label-text">Zona Waktu</label>
        <select bind:value={editForm.timezone} class="input-field mt-1">
          <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
          <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
          <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
        </select>
      </div>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit">Simpan Perubahan</Button>
    </div>
  </form>
</Modal>