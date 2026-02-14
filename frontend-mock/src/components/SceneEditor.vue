<script setup lang="ts">
import { computed, ref } from 'vue';
import { storySentences } from '@/mock/mockStory';
import type { Scene } from '@/types/models';

const props = defineProps<{ scene: Scene }>();

const emit = defineEmits<{
  boundaryShift: [sceneId: string, direction: 'start-' | 'start+' | 'end-' | 'end+'];
  split: [sceneId: string, splitAtGlobalSentenceIdx: number];
  merge: [sceneId: string, direction: 'prev' | 'next'];
  approve: [sceneId: string, approved: boolean];
}>();

const expanded = ref(false);
const splitIdx = ref<number | null>(null);

const before = computed(() => storySentences.slice(Math.max(0, props.scene.startIdx - 2), props.scene.startIdx));
const inside = computed(() => storySentences.slice(props.scene.startIdx, props.scene.endIdx + 1));
const after = computed(() => storySentences.slice(props.scene.endIdx + 1, props.scene.endIdx + 3));

function pickSplit(localIdx: number) {
  splitIdx.value = props.scene.startIdx + localIdx;
}
</script>

<template>
  <section class="space-y-4 rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold">{{ scene.title }}</h2>
        <p class="text-sm text-slate-500">status: {{ scene.status }}</p>
      </div>
      <button
        class="rounded-lg px-3 py-1.5 text-sm"
        :class="scene.status === 'approved' ? 'bg-emerald-600 text-white' : 'border border-slate-300'"
        @click="emit('approve', scene.id, scene.status !== 'approved')"
      >
        {{ scene.status === 'approved' ? 'Approved' : 'Approve' }}
      </button>
    </div>

    <div>
      <button class="mb-2 text-sm text-brand-600" @click="expanded = !expanded">{{ expanded ? 'Свернуть текст' : 'Развернуть текст' }}</button>
      <p class="text-sm leading-6 text-slate-700" :class="expanded ? '' : 'line-clamp-3'">{{ scene.text }}</p>
    </div>

    <div class="space-y-2">
      <p class="text-sm font-medium">Границы сцены (snap по предложениям)</p>
      <div class="rounded-lg bg-slate-50 p-3 text-sm">
        <p class="mb-1 text-xs uppercase text-slate-400">До сцены</p>
        <p class="text-slate-500">{{ before.join(' ') }}</p>
        <p class="mb-1 mt-3 text-xs uppercase text-slate-400">Сцена</p>
        <ul class="space-y-1">
          <li
            v-for="(sentence, localIdx) in inside"
            :key="`${scene.id}-${localIdx}`"
            class="cursor-pointer rounded px-2 py-1"
            :class="splitIdx === scene.startIdx + localIdx ? 'bg-amber-100' : 'bg-brand-50'"
            @click="pickSplit(localIdx)"
          >
            {{ sentence }}
          </li>
        </ul>
        <p class="mb-1 mt-3 text-xs uppercase text-slate-400">После сцены</p>
        <p class="text-slate-500">{{ after.join(' ') }}</p>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2 md:grid-cols-4">
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('boundaryShift', scene.id, 'start-')">Start −</button>
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('boundaryShift', scene.id, 'start+')">Start +</button>
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('boundaryShift', scene.id, 'end-')">End −</button>
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('boundaryShift', scene.id, 'end+')">End +</button>
    </div>

    <div class="flex flex-wrap gap-2">
      <button
        class="rounded border border-slate-200 px-2 py-1 text-sm"
        :disabled="splitIdx === null"
        @click="splitIdx !== null && emit('split', scene.id, splitIdx)"
      >
        Split at selected sentence
      </button>
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('merge', scene.id, 'prev')">Merge prev</button>
      <button class="rounded border border-slate-200 px-2 py-1 text-sm" @click="emit('merge', scene.id, 'next')">Merge next</button>
    </div>
  </section>
</template>
