<script setup lang="ts">
import type { Illustration, Scene } from '@/types/models';

defineProps<{
  scene: Scene;
  illustration?: Illustration;
  selected?: boolean;
}>();

const emit = defineEmits<{
  edit: [id: string];
}>();
</script>

<template>
  <article
    class="rounded-2xl border border-slate-200 bg-white p-3 transition"
    :class="selected ? 'ring-2 ring-emerald-200 shadow-md' : 'shadow-sm'"
  >
    <div class="mb-2 flex items-start justify-between gap-2">
      <h3 class="comic-title text-sm font-semibold">#{{ scene.index }} {{ scene.title }}</h3>
    </div>

    <p class="text-xs text-slate-700 line-clamp-3">{{ scene.text }}</p>

    <div class="flex flex-wrap gap-2 text-xs">
      <button class="rounded border border-slate-200 bg-white px-2 py-1 font-semibold" @click.stop="emit('edit', scene.id)">Редактировать</button>
    </div>
  </article>
</template>
