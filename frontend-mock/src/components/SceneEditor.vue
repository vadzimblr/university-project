<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { storySentences } from '@/mock/mockStory';
import type { Scene } from '@/types/models';

const props = defineProps<{
  scene: Scene;
  minStart: number;
  maxEnd: number;
  hasPrev: boolean;
  hasNext: boolean;
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
const defaultHint = 'Перетаскивайте только крайние предложения текущей сцены в соседние зоны.';
const dragHint = ref(defaultHint);

watch(
  () => props.scene,
  (next) => {
    startValue.value = next.startIdx;
    endValue.value = next.endIdx;
    splitIdx.value = null;
    dragHint.value = defaultHint;
  },
  { deep: true },
);

const before = computed(() => storySentences.slice(Math.max(0, startValue.value - 2), startValue.value));
const inside = computed(() => storySentences.slice(startValue.value, endValue.value + 1));
const after = computed(() => storySentences.slice(endValue.value + 1, endValue.value + 3));

const maxMovable = computed(() => Math.max(0, inside.value.length - 2));
const canMoveHead = computed(() => props.hasPrev && maxMovable.value > 0);
const canMoveTail = computed(() => props.hasNext && maxMovable.value > 0);

function commitRange(newStart: number, newEnd: number) {
  if (newStart >= newEnd) return;
  emit('setRange', props.scene.id, newStart, newEnd);
}

function onSentenceDragStart(event: DragEvent, localIdx: number) {
  const isHead = localIdx === 0;
  const isTail = localIdx === inside.value.length - 1;

  if (isHead && canMoveHead.value) {
    event.dataTransfer?.setData('text/plain', 'head');
    dragHint.value = 'Отпустите в зоне «Контекст до», чтобы отдать первое предложение в previous scene.';
    return;
  }

  if (isTail && canMoveTail.value) {
    event.dataTransfer?.setData('text/plain', 'tail');
    dragHint.value = 'Отпустите в зоне «Контекст после», чтобы отдать последнее предложение в next scene.';
    return;
  }

  event.preventDefault();
}

function allowDrop(event: DragEvent) {
  event.preventDefault();
}

function onDropToPrev(event: DragEvent) {
  event.preventDefault();
  const payload = event.dataTransfer?.getData('text/plain');
  if (payload !== 'head' || !canMoveHead.value) {
    dragHint.value = 'В previous scene можно переносить только первое предложение текущей сцены.';
    return;
  }
  commitRange(startValue.value + 1, endValue.value);
  dragHint.value = 'Готово: первое предложение передано в previous scene.';
}

function onDropToNext(event: DragEvent) {
  event.preventDefault();
  const payload = event.dataTransfer?.getData('text/plain');
  if (payload !== 'tail' || !canMoveTail.value) {
    dragHint.value = 'В next scene можно переносить только последнее предложение текущей сцены.';
    return;
  }
  commitRange(startValue.value, endValue.value - 1);
  dragHint.value = 'Готово: последнее предложение передано в next scene.';
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
        <li>Зажмите и перетащите <b>первое</b> или <b>последнее</b> предложение текущей сцены.</li>
        <li>Бросьте в «Контекст до» или «Контекст после», чтобы передвинуть границу.</li>
        <li>Средние предложения переносить нельзя — только края сцены.</li>
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
      <p class="text-sm font-semibold">Ручное распределение drag &amp; drop</p>
      <p class="mt-1 text-xs text-slate-600">{{ dragHint }}</p>
      <p class="mt-2 text-xs text-slate-500">Ограничение: в сцене всегда остаётся минимум 2 предложения.</p>
    </div>

    <div class="speech-bubble">
      <button class="mb-2 text-sm font-semibold text-blue-700" @click="expanded = !expanded">{{ expanded ? 'Свернуть текст' : 'Развернуть текст' }}</button>
      <p class="text-sm leading-6 text-slate-700" :class="expanded ? '' : 'line-clamp-3'">{{ scene.text }}</p>
    </div>

    <div class="grid gap-2 md:grid-cols-3">
      <div class="story-strip" :class="hasPrev ? 'border-emerald-700 bg-emerald-50' : ''" @dragover="allowDrop" @drop="onDropToPrev">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст до</p>
        <p v-if="hasPrev" class="mb-1 text-[11px] font-semibold text-emerald-700">Drop первого предложения сюда → previous scene</p>
        <p class="text-xs text-slate-600">{{ before.join(' ') || '—' }}</p>
      </div>
      <div class="story-strip border-slate-900 bg-blue-50">
        <p class="mb-1 text-xs font-bold uppercase text-slate-700">Текущая сцена (drag края / клик для split)</p>
        <ul class="max-h-72 space-y-1 overflow-y-auto">
          <li
            v-for="(sentence, localIdx) in inside"
            :key="`${scene.id}-${localIdx}`"
            class="rounded border border-slate-200 px-2 py-1 text-xs"
            :class="[
              splitIdx === startValue + localIdx ? 'bg-yellow-200 border-slate-900' : 'bg-white',
              localIdx === 0 && canMoveHead ? 'cursor-grab border-emerald-700' : 'cursor-pointer',
              localIdx === inside.length - 1 && canMoveTail ? 'cursor-grab border-violet-700' : '',
            ]"
            :draggable="(localIdx === 0 && canMoveHead) || (localIdx === inside.length - 1 && canMoveTail)"
            @dragstart="onSentenceDragStart($event, localIdx)"
            @dragend="dragHint = defaultHint"
            @click="pickSplit(localIdx)"
          >
            <span class="mr-1 text-[10px] text-slate-400">{{ startValue + localIdx }}.</span>
            {{ sentence }}
          </li>
        </ul>
      </div>
      <div class="story-strip" :class="hasNext ? 'border-violet-700 bg-violet-50' : ''" @dragover="allowDrop" @drop="onDropToNext">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст после</p>
        <p v-if="hasNext" class="mb-1 text-[11px] font-semibold text-violet-700">Drop последнего предложения сюда → next scene</p>
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
