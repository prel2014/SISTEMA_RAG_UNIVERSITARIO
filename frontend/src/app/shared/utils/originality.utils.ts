export function scoreColorClass(score: number | null): string {
  if (score === null) return 'text-gray-400';
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 40) return 'text-orange-500';
  return 'text-red-600';
}

export function levelBadgeClass(level: string | null): string {
  switch (level) {
    case 'low':       return 'bg-green-100 text-green-700';
    case 'moderate':  return 'bg-yellow-100 text-yellow-700';
    case 'high':      return 'bg-orange-100 text-orange-700';
    case 'very_high': return 'bg-red-100 text-red-700';
    default:          return 'bg-gray-100 text-gray-500';
  }
}

export function levelLabel(level: string | null): string {
  switch (level) {
    case 'low':       return 'Bajo';
    case 'moderate':  return 'Moderado';
    case 'high':      return 'Alto';
    case 'very_high': return 'Muy Alto';
    default:          return '-';
  }
}
