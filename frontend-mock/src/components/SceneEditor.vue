<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { storySentences } from '@/mock/mockStory';
import type { Scene } from '@/types/models';

const props = defineProps<{
  scene: Scene;
  minStart: number;
  maxEnd: number;
}>();

const emit = defineEmits<{
  setRange: [sceneId: string, startIdx: number, endIdx: number];
  split: [sceneId: string, splitAtGlobalSentenceIdx: number];
  merge: [sceneId: string, direction: 'prev' | 'next'];
  approve: [sceneId: string, approved: boolean];
}>();

const expanded = ref(false);
const splitIdx = ref<number | null>(null);
const startValue = ref(props.scene.startIdx);
const endValue = ref(props.scene.endIdx);

watch(
  () => props.scene,
  (next) => {
    startValue.value = next.startIdx;
    endValue.value = next.endIdx;
    splitIdx.value = null;
  },
  { deep: true },
);

const before = computed(() => storySentences.slice(Math.max(0, startValue.value - 2), startValue.value));
const inside = computed(() => storySentences.slice(startValue.value, endValue.value + 1));
const after = computed(() => storySentences.slice(endValue.value + 1, endValue.value + 3));

function commitRange() {
  if (startValue.value >= endValue.value) {
    endValue.value = startValue.value + 1;
  }
  emit('setRange', props.scene.id, startValue.value, endValue.value);
}

function onStartInput(value: number) {
  startValue.value = Math.min(value, endValue.value - 1);
  commitRange();
}

function onEndInput(value: number) {
  endValue.value = Math.max(value, startValue.value + 1);
  commitRange();
}

function pickSplit(localIdx: number) {
  splitIdx.value = startValue.value + localIdx;
}
</script>

<template>
  <section class="comic-card space-y-4 bg-white p-4">
    <div class="rounded-lg border-2 border-slate-900 bg-amber-50 p-3 text-sm">
      <p class="font-black">Как пользоваться</p>
      <ol class="mt-1 list-decimal pl-5 text-xs text-slate-700">
        <li>Двигайте ползунок <b>Start</b> и <b>End</b> — предложение либо входит в сцену, либо нет.</li>
        <li>Сцена обновляется сразу, соседние сцены подстраиваются автоматически.</li>
        <li>Нажмите на предложение и используйте Split для деления сцены.</li>
      </ol>
    </div>

    <div class="flex items-center justify-between gap-2">
      <div>
        <h2 class="comic-title text-xl font-black">{{ scene.title }}</h2>
        <p class="text-sm text-slate-600">Границы сцены: {{ startValue }}-{{ endValue }}</p>
      </div>
      <button class="rounded-lg border-2 border-slate-900 px-3 py-1.5 text-sm font-semibold" :class="scene.status === 'approved' ? 'bg-emerald-400 text-white' : 'bg-white'" @click="emit('approve', scene.id, scene.status !== 'approved')">
        {{ scene.status === 'approved' ? 'Approved' : 'Approve' }}
      </button>
    </div>

    <div class="rounded-xl border-2 border-slate-900 bg-white p-3">
      <div class="mb-3">
        <label class="mb-1 block text-sm font-semibold">Start: {{ startValue }}</label>
        <input type="range" class="w-full accent-blue-600" :min="minStart" :max="Math.max(minStart, endValue - 1)" :value="startValue" @input="onStartInput(Number(($event.target as HTMLInputElement).value))" />
      </div>
      <div>
        <label class="mb-1 block text-sm font-semibold">End: {{ endValue }}</label>
        <input type="range" class="w-full accent-blue-600" :min="Math.min(maxEnd, startValue + 1)" :max="maxEnd" :value="endValue" @input="onEndInput(Number(($event.target as HTMLInputElement).value))" />
      </div>
    </div>

    <div class="speech-bubble">
      <button class="mb-2 text-sm font-semibold text-blue-700" @click="expanded = !expanded">{{ expanded ? 'Свернуть текст' : 'Развернуть текст' }}</button>
      <p class="text-sm leading-6 text-slate-700" :class="expanded ? '' : 'line-clamp-3'">{{ scene.text }}</p>
    </div>

    <div class="grid gap-2 md:grid-cols-3">
      <div class="story-strip">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст до</p>
        <p class="text-xs text-slate-600">{{ before.join(' ') || '—' }}</p>
      </div>
      <div class="story-strip border-slate-900 bg-blue-50">
        <p class="mb-1 text-xs font-bold uppercase text-slate-700">Текущая сцена (клик для split)</p>
        <ul class="max-h-72 space-y-1 overflow-y-auto">
          <li
            v-for="(sentence, localIdx) in inside"
            :key="`${scene.id}-${localIdx}`"
            class="cursor-pointer rounded border border-slate-200 px-2 py-1 text-xs"
            :class="splitIdx === startValue + localIdx ? 'bg-yellow-200 border-slate-900' : 'bg-white'"
            @click="pickSplit(localIdx)"
          >
            <span class="mr-1 text-[10px] text-slate-400">{{ startValue + localIdx }}.</span>
            {{ sentence }}
          </li>
        </ul>
      </div>
      <div class="story-strip">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст после</p>
        <p class="text-xs text-slate-600">{{ after.join(' ') || '—' }}</p>
      </div>
    </div>

    <div class="flex flex-wrap gap-2">
      <button class="kaboom-btn" :disabled="splitIdx === null" @click="splitIdx !== null && emit('split', scene.id, splitIdx)">Split по выделенному</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('merge', scene.id, 'prev')">Merge prev</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-sm font-semibold" @click="emit('merge', scene.id, 'next')">Merge next</button>
    </div>
  </section>
</template>
