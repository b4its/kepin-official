<script lang="ts">
  import ThemeMenu from '$lib/components/layout/ThemeMenu.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
</script>

<footer class="bg-[#171714] text-white mt-auto">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      <div class="col-span-2 md:col-span-1">
        <a href="/" class="flex items-center gap-2 mb-4">
          <Logo height={28} />
        </a>
        <p class="text-sm text-gray-400 leading-relaxed">
          Keuangan Pintar untuk UMKM Indonesia. Transparan, aman, dan terpercaya.
        </p>
      </div>

      <div>
        <h4 class="font-semibold text-sm mb-3">Produk</h4>
        <ul class="space-y-2">
          <li><a href="/#fitur" class="text-sm text-gray-400 hover:text-white transition-colors">Fitur</a></li>
          <li><a href="/#harga" class="text-sm text-gray-400 hover:text-white transition-colors">Harga</a></li>
          <li><a href="/security" class="text-sm text-gray-400 hover:text-white transition-colors">Keamanan</a></li>
        </ul>
      </div>

      <div>
        <h4 class="font-semibold text-sm mb-3">Perusahaan</h4>
        <ul class="space-y-2">
          <li><a href="/privacy" class="text-sm text-gray-400 hover:text-white transition-colors">Kebijakan Privasi</a></li>
          <li><a href="/terms" class="text-sm text-gray-400 hover:text-white transition-colors">Syarat & Ketentuan</a></li>
        </ul>
      </div>

      <div>
        <h4 class="font-semibold text-sm mb-3">Bantuan</h4>
        <ul class="space-y-2">
          <li><a href="mailto:hello@kepin.id" class="text-sm text-gray-400 hover:text-white transition-colors">hello@kepin.id</a></li>
          <li><a href="/#faq" class="text-sm text-gray-400 hover:text-white transition-colors">FAQ</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-gray-800 mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
      <p class="text-xs text-gray-500">
        &copy; {new Date().getFullYear()} KePin (Keuangan Pintar). Hak cipta dilindungi.
      </p>
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-500">Tema:</span>
        <ThemeMenu />
      </div>
    </div>
  </div>
</footer>