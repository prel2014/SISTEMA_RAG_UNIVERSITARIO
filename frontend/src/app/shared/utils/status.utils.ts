export const STATUS_LABELS: Record<string, string> = {
  completed: 'Completado',
  processing: 'Procesando',
  pending: 'Pendiente',
  failed: 'Fallido',
};

export function getStatusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status;
}

export function getStatusBadgeClass(status: string): string {
  switch (status) {
    case 'completed':  return 'bg-green-100 text-green-700';
    case 'processing': return 'bg-yellow-100 text-yellow-700';
    case 'pending':    return 'bg-gray-100 text-gray-600';
    case 'failed':     return 'bg-red-100 text-red-700';
    default:           return 'bg-gray-100 text-gray-600';
  }
}
