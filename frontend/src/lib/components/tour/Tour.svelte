<script lang="ts">
  import { onDestroy } from 'svelte';
  import { beforeNavigate, goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { mainTour } from '$lib/config/tour';
  import {
    tourRunning,
    tourStepIndex,
    tourNonce,
    saveTourState,
    clearTourState,
    loadTourState,
    getTenantSlug,
    stepUrl,
    stepMatchesPath,
    type TourStep,
  } from '$lib/stores/tour';
  import { showToast } from '$lib/stores/toast';

  let driverInstance: any = null;
  let handledNonce = 0;
  // Benar selama goto (perpindahan halaman tur) sedang dijadwalkan/dijalankan —
  // mencegah efek utama melompat ke langkah yang salah sebelum navigasi tiba.
  let navPending = false;
  // Kunci dedupe + token resume: mencegah resume paralel pada (langkah, halaman)
  // yang sama, sementara resume yang lebih baru tetap bisa menggantikannya.
  let resumeKey = '';
  let resumeToken = 0;
  // Nomer sesi drive: bertambah setiap kali driver dihancurkan atau drive baru
  // dimulai. Persiapan drive yang berjalan (import driver.js, resolve elemen)
  // dibatalkan bila nomornya sudah tidak terkini — misalnya ketika halaman
  // berpindah (redirect /auth/onboarding) di tengah persiapan.
  let driveSession = 0;
  const slug = $derived($page.params.tenantSlug || getTenantSlug());
  const totalSteps = mainTour.steps.length;

  function destroyDriver() {
    driveSession++;
    try { driverInstance?.destroy(); } catch { /* noop */ }
    driverInstance = null;
  }

  function finishTour() {
    tourRunning.set(false);
    clearTourState();
    destroyDriver();
    showToast('Tur selesai! Anda sekarang siap menggunakan KePin 🎉', 'success');
  }

  function closeTour() {
    tourRunning.set(false);
    clearTourState();
    destroyDriver();
  }

  // Navigasi apa pun (termasuk redirect halaman seperti /auth/onboarding)
  // menghancurkan driver lama; efek utama akan melanjutkan tur di halaman tujuan.
  beforeNavigate(() => {
    navPending = false;
    destroyDriver();
  });

  async function resolveElement(step: TourStep): Promise<Element | null> {
    if (!step.element) return null;
    // Tunggu elemen muncul (data halaman dimuat asinkron) hingga 2,5 detik.
    // Bila tidak ditemukan (mis. CTA "Coba Gratis" saat sudah login),
    // langkah tetap dijalankan dengan popover di tengah.
    const deadline = Date.now() + 2500;
    while (Date.now() < deadline) {
      try {
        const el = typeof step.element === 'function' ? step.element() : document.querySelector(step.element);
        if (el) return el;
      } catch { /* selector tidak valid — lanjut coba */ }
      await new Promise((r) => setTimeout(r, 150));
    }
    return null;
  }

  async function driveSteps(fromGlobal: number) {
    const session = ++driveSession;
    const currentPath = $page.url.pathname;
    const all = mainTour.steps;

    if (fromGlobal >= all.length || !stepMatchesPath(all[fromGlobal], currentPath, slug)) return false;
    // Rentang maksimal langkah berurutan pada halaman ini yang memuat fromGlobal
    // (langkah-langkah satu halaman selalu berdampingan dalam konfigurasi).
    let start = fromGlobal;
    while (start > 0 && stepMatchesPath(all[start - 1], currentPath, slug)) start--;
    let end = fromGlobal;
    while (end < all.length - 1 && stepMatchesPath(all[end + 1], currentPath, slug)) end++;
    const run = all.slice(start, end + 1);
    const runStartLocal = fromGlobal - start;

    try {
      const { driver } = await import('driver.js');
      await import('driver.js/dist/driver.css');
      // Persiapan dibatalkan bila halaman berpindah / drive lain menang.
      if (session !== driveSession) return false;

      const steps = [];
      for (let k = 0; k < run.length; k++) {
        const step = run[k];
        const g = start + k;
        const el = await resolveElement(step);
        if (session !== driveSession) return false;
        steps.push({
          ...(el ? { element: el } : {}),
          popover: {
            title: step.title,
            description: `<div class="space-y-2"><p class="font-semibold text-base">${step.description}</p></div>`,
            side: step.side || 'bottom',
            align: step.align || 'center',
            showProgress: true,
            progressText: `${g + 1}/${totalSteps}`,
            onNextClick: () => handleNext(g, k, run.length),
            onPrevClick: () => handlePrev(g, k),
            doneBtnText: g === totalSteps - 1 ? 'Selesai' : 'Lanjut',
            nextBtnText: 'Lanjut',
            prevBtnText: 'Kembali',
          },
        });
      }

      const d = driver({
        animate: true,
        smoothScroll: true,
        allowKeyboardControl: true,
        skipMissingElement: true,
        showButtons: ['next', 'previous', 'close'],
        steps,
        onCloseClick: closeTour,
      });
      driverInstance = d;
      d.drive(runStartLocal);
      return true;
    } catch (err) {
      console.error('Tour error:', err);
      closeTour();
      return false;
    }
  }

  function resumeTour(fromGlobal: number, allowSkip = false) {
    // Dedupe: jangan memulai resume paralel untuk langkah yang sama pada
    // halaman yang sama (efek dapat terpicu berulang saat halaman memuat).
    // Resume tetap bisa berjalan setelah halaman berpindah atau langkah lain.
    const key = `${fromGlobal}:${$page.url.pathname}`;
    if (resumeKey === key) return;
    resumeKey = key;
    const token = ++resumeToken;
    void (async () => {
      try {
        const currentPath = $page.url.pathname;
        if (await driveSteps(fromGlobal)) return;

        // Hanya untuk resume pasif (efek/nonce): bila halaman ini memuat langkah
        // tur berikutnya (mis. setelah onboarding me-redirect ke dashboard),
        // lewati langkah yang tidak tercapai dan lanjut dari sana.
        if (allowSkip) {
          const later = mainTour.steps.slice(fromGlobal);
          const skip = later.find((s) => stepMatchesPath(s, currentPath, slug));
          if (skip) {
            const skipIndex = fromGlobal + later.indexOf(skip);
            tourStepIndex.set(skipIndex);
            saveTourState(skip.page, skipIndex);
            if (await driveSteps(skipIndex)) return;
          }
        }

        const nextStep = mainTour.steps.slice(fromGlobal).find((s) => !stepMatchesPath(s, currentPath, slug));
        if (!nextStep) { finishTour(); return; }
        const target = stepUrl(nextStep, slug);
        if (!slug && target.startsWith('/app/')) {
          tourRunning.set(false);
          clearTourState();
          showToast('Silakan masuk terlebih dahulu untuk melanjutkan tur workspace.', 'error');
          return;
        }
        navPending = true;
        setTimeout(() => {
          navPending = false;
          void goto(target);
        }, 150);
      } catch (err) {
        console.error('Tour error:', err);
        closeTour();
      } finally {
        // Hanya resume terbaru yang berhak membersihkan kunci dedupe.
        if (token === resumeToken) resumeKey = '';
      }
    })();
  }

  function handleNext(globalIdx: number, localIdx: number, runLength: number) {
    const nextStep = mainTour.steps[globalIdx + 1];
    if (!nextStep) return finishTour();
    tourStepIndex.set(globalIdx + 1);
    saveTourState(nextStep.page, globalIdx + 1);
    if (localIdx + 1 < runLength) {
      // Langkah berikutnya masih di halaman yang sama — biarkan driver melaju.
      driverInstance?.moveNext();
    } else {
      // Pindah halaman: kunci efek utama selama navigasi, lalu lanjutkan tur.
      navPending = true;
      destroyDriver();
      resumeTour(globalIdx + 1);
    }
  }

  function handlePrev(globalIdx: number, localIdx: number) {
    if (globalIdx <= 0) return;
    const prevStep = mainTour.steps[globalIdx - 1];
    tourStepIndex.set(globalIdx - 1);
    saveTourState(prevStep.page, globalIdx - 1);
    if (localIdx > 0) {
      // Langkah sebelumnya masih di halaman yang sama — biarkan driver mundur.
      driverInstance?.movePrevious();
    } else {
      // Langkah sebelumnya di halaman lain — navigasi langsung ke sana.
      navPending = true;
      destroyDriver();
      setTimeout(() => {
        navPending = false;
        void goto(stepUrl(prevStep, slug));
      }, 150);
    }
  }

  async function startTour() {
    const firstStep = mainTour.steps[0];
    tourStepIndex.set(0);
    clearTourState();
    saveTourState(firstStep.page, 0);
    resumeTour(0);
  }

  // Reaksi utama: kapan pun tur berjalan (dari tombol, halaman tutorial, atau
  // pergantian halaman saat tur berlangsung) dan belum ada driver aktif,
  // lanjutkan tur dari posisi tersimpan — atau mulai dari awal bila kosong.
  $effect(() => {
    // Ketergantungan eksplisit pada path: pergantian halaman (goto) memicu
    // evaluasi ulang sehingga tur dilanjutkan di halaman tujuan.
    const currentPath = $page.url.pathname;
    if (driverInstance || navPending) return;
    // Status tur tersimpan (localStorage) tetap valid walau halaman dimuat
    // ulang penuh (mis. redirect /auth/onboarding memakai window.location).
    const state = loadTourState();
    if (!$tourRunning && !state) return;
    if (!state) { void startTour(); return; }
    if (!$tourRunning) tourRunning.set(true);
    resumeTour(state.step, true);
  });

  // Mulai ulang tur dari langkah tertentu (klik "Mulai dari sini" di halaman
  // tutorial) — hancurkan driver lama bila tur sedang berjalan.
  $effect(() => {
    const nonce = $tourNonce;
    if (nonce === handledNonce) return;
    handledNonce = nonce;
    destroyDriver();
    const state = loadTourState();
    if (state) resumeTour(state.step, true);
  });

  onDestroy(() => { destroyDriver(); });
</script>
