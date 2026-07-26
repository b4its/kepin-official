<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let companyName = $state('Toko Maju Jaya');
  let legalName = $state('UD Toko Maju Jaya');
  let sector = $state('Ritel');
  let timezone = $state('Asia/Jakarta');
</script>

<PageHeader title="Organisasi" description="Profil dan pengaturan organisasi" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Organisasi' }]} />

<div class="card p-6 max-w-2xl">
  <form class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text mb-1 block" for="company-name">Nama Tampilan</label>
        <input id="company-name" bind:value={companyName} class="input-field" />
      </div>
      <div>
        <label class="label-text mb-1 block" for="legal-name">Nama Legal</label>
        <input id="legal-name" bind:value={legalName} class="input-field" />
      </div>
      <div>
        <label class="label-text mb-1 block" for="sector">Sektor</label>
        <select id="sector" bind:value={sector} class="input-field">
          <option value="Ritel">Ritel</option>
          <option value="F&B">F&B</option>
          <option value="Manufaktur">Manufaktur</option>
          <option value="Jasa">Jasa</option>
        </select>
      </div>
      <div>
        <label class="label-text mb-1 block" for="timezone">Zona Waktu</label>
        <select id="timezone" bind:value={timezone} class="input-field">
          <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
          <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
          <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
        </select>
      </div>
    </div>
    <Button type="submit">Simpan Perubahan</Button>
  </form>
</div>
