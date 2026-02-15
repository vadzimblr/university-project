const map: Record<string, string> = {
  pending: 'Ожидает',
  extracting: 'Извлечение текста',
  splitting: 'Разделение сцен',
  'ready-for-review': 'Готово к проверке',
  approved: 'Одобрено',
  completed: 'Завершено',
  failed: 'Ошибка',
  cancelled: 'Отменено',
};

export function statusLabel(status?: string): string {
  if (!status) return 'Неизвестно';
  const key = status.toLowerCase();
  return map[key] ?? status;
}
