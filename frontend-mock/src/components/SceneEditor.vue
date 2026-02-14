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
  <section class="comic-card space-y-4 bg-white p-4">
    <div class="flex items-center justify-between gap-2">
      <div>
        <h2 class="comic-title text-xl font-black">{{ scene.title }}</h2>
        <p class="text-sm text-slate-600">Комикс-статус: {{ scene.status }}</p>
      </div>
      <button
        class="rounded-lg border-2 border-slate-900 px-3 py-1.5 text-sm font-semibold"
        :class="scene.status === 'approved' ? 'bg-emerald-400 text-white' : 'bg-white'"
        @click="emit('approve', scene.id, scene.status !== 'approved')"
      >
        {{ scene.status === 'approved' ? 'Approved' : 'Approve' }}
      </button>
    </div>

    <div class="speech-bubble">
      <button class="mb-2 text-sm font-semibold text-blue-700" @click="expanded = !expanded">{{ expanded ? 'Свернуть текст' : 'Развернуть текст' }}</button>
      <p class="text-sm leading-6 text-slate-700" :class="expanded ? '' : 'line-clamp-3'">{{ scene.text }}</p>
    </div>

    <div class="space-y-2">
      <p class="text-sm font-black">Границы сцены (snap по предложениям)</p>
      <div class="grid gap-2 md:grid-cols-3">
        <div class="story-strip">
          <p class="mb-1 text-xs font-bold uppercase text-slate-500">До сцены</p>
          <p class="text-xs text-slate-600">{{ before.join(' ') }}</p>
        </div>
        <div class="story-strip border-slate-900 bg-blue-50">
          <p class="mb-1 text-xs font-bold uppercase text-slate-700">Сцена (кликни для Split)</p>
          <ul class="space-y-1">
            <li
              v-for="(sentence, localIdx) in inside"
              :key="`${scene.id}-${localIdx}`"
              class="cursor-pointer rounded border border-slate-200 px-2 py-1 text-xs"
              :class="splitIdx === scene.startIdx + localIdx ? 'bg-yellow-200 border-slate-900' : 'bg-white'"
              @click="pickSplit(localIdx)"
            >
              {{ sentence }}
            </li>
          </ul>
        </div>
        <div class="story-strip">
          <p class="mb-1 text-xs font-bold uppercase text-slate-500">После сцены</p>
          <p class="text-xs text-slate-600">{{ after.join(' ') }}</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2 md:grid-cols-4">
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('boundaryShift', scene.id, 'start-')">Start −</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('boundaryShift', scene.id, 'start+')">Start +</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('boundaryShift', scene.id, 'end-')">End −</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('boundaryShift', scene.id, 'end+')">End +</button>
    </div>

    <div class="flex flex-wrap gap-2">
      <button class="kaboom-btn" :disabled="splitIdx === null" @click="splitIdx !== null && emit('split', scene.id, splitIdx)">Split</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('merge', scene.id, 'prev')">Merge prev</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('merge', scene.id, 'next')">Merge next</button>
    </div>
  </section>
</template>
