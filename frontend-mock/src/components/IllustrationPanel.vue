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
  <section class="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
    <h3 class="mb-3 text-sm font-semibold">Иллюстрация</h3>

    <div v-if="scene.status === 'ready' && illustration" class="space-y-3">
      <img :src="illustration.imageUrl" alt="illustration" class="h-52 w-full rounded-lg object-cover" />
      <div class="flex gap-2">
        <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm" @click="emit('regenerate', scene.id)">Регенерировать</button>
        <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm" @click="emit('showPrompt', scene.id)">Показать промпт</button>
      </div>
    </div>

    <div v-else-if="scene.status === 'generating'" class="space-y-3">
      <div class="flex h-52 items-center justify-center rounded-lg bg-amber-50 text-amber-700">Генерируем…</div>
    </div>

    <div v-else-if="scene.status === 'error'" class="space-y-3">
      <div class="flex h-52 items-center justify-center rounded-lg bg-red-50 text-red-700">Ошибка генерации</div>
      <button class="rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-700" @click="emit('retry', scene.id)">Retry</button>
    </div>

    <div v-else class="flex h-52 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
      Placeholder до готовности
    </div>
  </section>
</template>
