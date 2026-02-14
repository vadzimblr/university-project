<script setup lang="ts">
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scene: Scene;
  illustration?: Illustration;
  selected?: boolean;
}>();

const emit = defineEmits<{
  approve: [id: string, approved: boolean];
  edit: [id: string];
  regenerate: [id: string];
}>();

const statusStyles = {
  pending: 'bg-slate-100 text-slate-700',
  approved: 'bg-emerald-100 text-emerald-700',
  generating: 'bg-amber-100 text-amber-700',
  ready: 'bg-blue-100 text-blue-700',
  error: 'bg-red-100 text-red-700',
};
</script>

<template>
  <article
    class="cursor-pointer rounded-xl border p-3 transition"
    :class="selected ? 'border-brand-600 bg-brand-50' : 'border-slate-200 bg-white hover:border-brand-300'"
    @click="emit('edit', scene.id)"
  >
    <div class="mb-2 flex items-start justify-between gap-2">
      <h3 class="text-sm font-semibold">#{{ scene.index }} {{ scene.title }}</h3>
      <span class="rounded-full px-2 py-0.5 text-xs" :class="statusStyles[scene.status]">{{ scene.status }}</span>
    </div>

    <div class="mb-2 flex items-center gap-2">
      <img v-if="illustration" :src="illustration.imageUrl" alt="thumb" class="h-10 w-16 rounded object-cover" />
      <div v-else class="flex h-10 w-16 items-center justify-center rounded bg-slate-100 text-[10px] text-slate-500">no img</div>
      <p class="line-clamp-2 text-xs text-slate-600">{{ props.scene.text }}</p>
    </div>

    <div class="flex flex-wrap gap-2 text-xs">
      <button class="rounded border border-slate-200 px-2 py-1" @click.stop="emit('approve', scene.id, scene.status !== 'approved')">
        {{ scene.status === 'approved' ? 'Unapprove' : 'Approve' }}
      </button>
      <button class="rounded border border-slate-200 px-2 py-1" @click.stop="emit('edit', scene.id)">Edit</button>
      <button v-if="scene.status === 'ready' || scene.status === 'error'" class="rounded border border-slate-200 px-2 py-1" @click.stop="emit('regenerate', scene.id)">Regenerate</button>
    </div>
  </article>
</template>
