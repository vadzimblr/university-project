<script setup lang="ts">
import type { Illustration, Scene } from '@/types/models';

defineProps<{
  scene: Scene;
  illustration?: Illustration;
  selected?: boolean;
  compact?: boolean;
}>();

const emit = defineEmits<{
  edit: [id: string];
}>();

const statusStyles = {
  pending: 'bg-slate-200 text-slate-800',
  approved: 'bg-emerald-200 text-emerald-800',
  generating: 'bg-amber-200 text-amber-800',
  ready: 'bg-blue-200 text-blue-800',
  error: 'bg-red-200 text-red-800',
};
</script>

<template>
  <article
    class="rounded-2xl border border-slate-200 bg-white p-3 transition"
    :class="selected ? 'ring-2 ring-emerald-200 shadow-md' : 'shadow-sm'"
  >
    <div class="mb-2 flex items-start justify-between gap-2">
      <h3 class="comic-title text-sm font-semibold">#{{ scene.index }} {{ scene.title }}</h3>
      <span class="rounded-full border border-slate-200 px-2 py-0.5 text-xs font-semibold" :class="statusStyles[scene.status]">{{ scene.status }}</span>
    </div>

    <div class="mb-2 flex items-center gap-2">
      <img v-if="illustration" :src="illustration.imageUrl" alt="thumb" class="h-10 w-16 rounded border border-slate-200 object-cover" />
      <div v-else class="flex h-10 w-16 items-center justify-center rounded border border-dashed border-slate-300 bg-slate-100 text-[10px] text-slate-500">panel</div>
      <p class="text-xs text-slate-700" :class="compact ? 'line-clamp-1' : 'line-clamp-2'">{{ scene.text }}</p>
    </div>

    <div class="flex flex-wrap gap-2 text-xs">
      <button class="rounded border border-slate-200 bg-white px-2 py-1 font-semibold" @click.stop="emit('edit', scene.id)">Edit</button>
    </div>
  </article>
</template>
