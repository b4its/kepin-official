export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '-';
  const now = new Date();
  const past = new Date(date);
  const diffMs = now.getTime() - past.getTime();
  const totalSec = Math.floor(diffMs / 1000);
  const totalMin = Math.floor(totalSec / 60);
  const totalHour = Math.floor(totalMin / 60);
  const totalDay = Math.floor(totalHour / 24);

  if (totalSec < 60) return `${totalSec} detik yang lalu`;
  if (totalMin < 60) return `${totalMin} menit yang lalu`;
  if (totalHour < 24) return `${totalHour} jam yang lalu`;
  if (totalDay < 30) return `${totalDay} hari yang lalu`;
  const totalMonth = Math.floor(totalDay / 30);
  if (totalMonth < 12) return `${totalMonth} bulan yang lalu`;
  const totalYear = Math.floor(totalMonth / 12);
  return `${totalYear} tahun yang lalu`;
}
