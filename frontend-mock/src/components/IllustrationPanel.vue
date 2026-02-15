<script setup lang="ts">
import type { Illustration, Scene } from '@/types/models';

defineProps<{
  scene: Scene;
  illustration?: Illustration;
}>();

const emit = defineEmits<{
  regenerate: [id: string];
  showPrompt: [id: string];
  retry: [id: string];
}>();
</script>

<template>
  <section class="comic-card bg-white p-4">
    <h3 class="comic-title mb-3 text-sm font-semibold">Иллюстрация / Комикс-панель</h3>

    <div v-if="scene.status === 'ready' && illustration" class="space-y-3">
      <div class="panel-frame">
        <img :src="illustration.imageUrl" alt="illustration" class="h-56 w-full object-cover" />
      </div>
      <p class="rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs font-medium">Caption: Сцена готова к сборке в storybook-последовательность.</p>
      <div class="flex gap-2">
        <button class="kaboom-btn" @click="emit('regenerate', scene.id)">Регенерировать</button>
        <button class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm" @click="emit('showPrompt', scene.id)">Показать промпт</button>
      </div>
    </div>

    <div v-else-if="scene.status === 'generating'" class="space-y-3">
      <div class="panel-frame flex h-56 items-center justify-center bg-amber-50 text-amber-800">Генерируем кадр...</div>
    </div>

    <div v-else-if="scene.status === 'error'" class="space-y-3">
      <div class="panel-frame flex h-56 items-center justify-center bg-rose-50 text-rose-700">Ошибка генерации панели</div>
      <button class="rounded-lg border border-slate-200 bg-rose-50 px-3 py-1.5 text-sm font-semibold text-rose-700" @click="emit('retry', scene.id)">Retry</button>
    </div>

    <div v-else class="panel-frame flex h-56 items-center justify-center text-slate-500">Panel placeholder до готовности</div>
  </section>
</template>
