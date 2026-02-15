<script setup lang="ts">
import type { Illustration, Scene } from '@/types/models';

defineProps<{
  scene: Scene;
  illustration?: Illustration;
  selected?: boolean;
  mergeQueued?: boolean;
  mergeQueuedAuto?: boolean;
}>();

const emit = defineEmits<{
  edit: [id: string];
}>();
</script>

<template>
  <article
    class="rounded-2xl border p-3 transition"
    :class="[
      selected ? 'ring-2 ring-emerald-200 shadow-md' : 'shadow-sm',
      mergeQueued ? 'border-amber-300 bg-amber-50/70' : mergeQueuedAuto ? 'border-sky-300 bg-sky-50/70' : 'border-slate-200 bg-white',
    ]"
    @click="emit('edit', scene.id)"
  >
    <div class="mb-2 flex items-start justify-between gap-2">
      <h3 class="comic-title text-sm font-semibold">#{{ scene.index }} {{ scene.title }}</h3>
      <span v-if="mergeQueued" class="rounded-full border border-amber-300 bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
        Слияние
      </span>
      <span v-else-if="mergeQueuedAuto" class="rounded-full border border-sky-300 bg-sky-100 px-2 py-0.5 text-[10px] font-semibold text-sky-800">
        Автослияние
      </span>
    </div>

    <p class="text-xs text-slate-700 line-clamp-3">{{ scene.text }}</p>
  </article>
</template>
