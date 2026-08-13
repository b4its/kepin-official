<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { mainTour } from '$lib/config/tour';
  import { tourRunning, tourStepIndex, saveTourState, clearTourState, loadTourState } from '$lib/stores/tour';
  import { showToast } from '$lib/stores/toast';

  let driverInstance: any = null;
  let resumeHandled = $state(false);
  const slug = $derived($page.params.tenantSlug || '');

  function getPage(): string {
    return $page.url.pathname.replace(`/app/${slug}/`, '').replace(`/app/${slug}`, '');
  }

  function destroyDriver() {
    try { driverInstance?.destroy(); } catch { /* noop */ }
    driverInstance = null;
  }

  function finishTour() {
    tourRunning.set(false);
    clearTourState();
    destroyDriver();
    resumeHandled = false;
    showToast('Tur selesai! Anda sekarang siap menggunakan KePin 🎉', 'success');
  }

  function closeTour() {
    tourRunning.set(false);
    clearTourState();
    destroyDriver();
    resumeHandled = false;
  }

  function handleNext(globalIdx: number) {
    const nextStep = mainTour.steps[globalIdx + 1];
    if (!nextStep) return finishTour();
    tourStepIndex.set(globalIdx + 1);
    saveTourState(nextStep.page, globalIdx + 1);
    destroyDriver();
    const currentPage = $page.url.pathname.replace(`/app/${slug}/`, '').replace(`/app/${slug}`, '');
    if (nextStep.page !== currentPage) {
      setTimeout(() => { void goto(`/app/${slug}/${nextStep.navigateTo || nextStep.page}`); }, 150);
    } else {
      resumeTour(globalIdx + 1);
    }
  }

  function handlePrev(globalIdx: number) {
    if (globalIdx <= 0) return;
    const prevStep = mainTour.steps[globalIdx - 1];
    tourStepIndex.set(globalIdx - 1);
    saveTourState(prevStep.page, globalIdx - 1);
    destroyDriver();
    const currentPage = $page.url.pathname.replace(`/app/${slug}/`, '').replace(`/app/${slug}`, '');
    if (prevStep.page !== currentPage) {
      setTimeout(() => { void goto(`/app/${slug}/${prevStep.navigateTo || prevStep.page}`); }, 150);
    } else {
      resumeTour(globalIdx - 1);
    }
  }

  async function resumeTour(fromGlobal: number) {
    const currentPage = $page.url.pathname.replace(`/app/${slug}/`, '').replace(`/app/${slug}`, '');
    const pageSteps = mainTour.steps.slice(fromGlobal).filter(
      (s) => s.page === currentPage || (currentPage === '' && s.page === '')
    );
    if (pageSteps.length === 0) {
      const nextStep = mainTour.steps.slice(fromGlobal).find((s) => s.page !== currentPage);
      if (nextStep) { void goto(`/app/${slug}/${nextStep.navigateTo || nextStep.page}`); }
      return;
    }
    try {
      const { driver } = await import('driver.js');
      await import('driver.js/dist/driver.css');
      destroyDriver();
      const steps = pageSteps.map((s, i) => {
        const g = fromGlobal + i;
        return {
          element: s.element || undefined,
          popover: {
            title: `Langkah ${g + 1} dari ${mainTour.steps.length}`,
            description: `<div class="space-y-2"><p class="font-semibold text-base">${s.title}</p><p class="text-sm opacity-80">${s.description}</p></div>`,
            side: s.side || 'bottom',
            align: s.align || 'center',
            progress: `${g + 1}/${mainTour.steps.length}`,
            onNextClick: () => handleNext(g),
            onPrevClick: () => handlePrev(g),
            doneBtnText: 'Selesai',
            nextBtnText: 'Lanjut',
            prevBtnText: 'Kembali',
          },
        };
      });
      const d = driver({ showProgress: true, animate: true, showButtons: ['next', 'previous', 'close'], steps, onCloseClick: closeTour });
      driverInstance = d;
      d.drive();
    } catch (err) {
      console.error('Tour error:', err);
      closeTour();
    }
  }

  async function startNewTour() {
    tourStepIndex.set(0);
    clearTourState();
    const currentPage = $page.url.pathname.replace(`/app/${slug}/`, '').replace(`/app/${slug}`, '');
    const firstStep = mainTour.steps[0];
    const target = firstStep.navigateTo || firstStep.page;
    if (firstStep.page !== currentPage) {
      await goto(`/app/${slug}/${target}`);
    } else {
      resumeTour(0);
    }
  }

  // Inisialisasi: cek saved state dari localStorage
  onMount(() => {
    const state = loadTourState();
    if (state) {
      const page = getPage();
      if (state.page === page || (page === '' && state.page === '')) {
        resumeHandled = true;
        tourRunning.set(true);
        resumeTour(state.step);
      }
    }
  });

  // Respons terhadap klik tombol "Mulai Tur" — hanya jika belum di-handle onMount
  $effect(() => {
    if ($tourRunning && !driverInstance && !resumeHandled) {
      startNewTour();
    }
  });

  // Pantau perubahan halaman — resume tur jika ada state tersimpan
  $effect(() => {
    const url = $page.url.pathname; // dependensi reaktif
    const state = loadTourState();
    if (state && !driverInstance && !resumeHandled) {
      const page = getPage();
      if (state.page === page || (page === '' && state.page === '')) {
        resumeHandled = true;
        tourRunning.set(true);
        resumeTour(state.step);
      }
    }
  });

  onDestroy(() => { destroyDriver(); });
</script>