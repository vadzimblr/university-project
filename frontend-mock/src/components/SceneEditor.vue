<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { storySentences } from '@/mock/mockStory';
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scene: Scene;
  illustration?: Illustration;
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
const activeDropZone = ref<'prev' | 'next' | null>(null);
const selectedForMove = ref<number[]>([]);
const defaultHint = 'Ctrl + ЛКМ: выбери несколько предложений по краю. Потом перетащи выделение в PREV/NEXT.';
const dragHint = ref(defaultHint);

watch(
  () => props.scene,
  (next) => {
    startValue.value = next.startIdx;
    endValue.value = next.endIdx;
    splitIdx.value = null;
    activeDropZone.value = null;
    selectedForMove.value = [];
    dragHint.value = defaultHint;
  },
  { deep: true },
);

const before = computed(() => storySentences.slice(Math.max(0, startValue.value - 2), startValue.value));
const inside = computed(() => storySentences.slice(startValue.value, endValue.value + 1));
const after = computed(() => storySentences.slice(endValue.value + 1, endValue.value + 3));
const maxMovable = computed(() => Math.max(0, inside.value.length - 2));

const selectionSorted = computed(() => [...selectedForMove.value].sort((a, b) => a - b));

const moveSelection = computed(() => {
  const selected = selectionSorted.value;
  if (!selected.length) return { mode: null as 'head' | 'tail' | null, count: 0 };

  const head = selected.every((value, index) => value === index);
  if (head && selected.length <= maxMovable.value) return { mode: 'head' as const, count: selected.length };

  const tailStart = inside.value.length - selected.length;
  const tail = selected.every((value, index) => value === tailStart + index);
  if (tail && selected.length <= maxMovable.value) return { mode: 'tail' as const, count: selected.length };

  return { mode: null as 'head' | 'tail' | null, count: 0 };
});

function commitRange(newStart: number, newEnd: number) {
  if (newStart >= newEnd) return;
  emit('setRange', props.scene.id, newStart, newEnd);
  selectedForMove.value = [];
}

function toggleSelection(idx: number) {
  if (!selectedForMove.value.includes(idx)) {
    selectedForMove.value = [...selectedForMove.value, idx];
  } else {
    selectedForMove.value = selectedForMove.value.filter((item) => item !== idx);
  }

  if (!selectionSorted.value.length) {
    dragHint.value = defaultHint;
    return;
  }

  const state = moveSelection.value;
  if (!state.mode) {
    selectedForMove.value = [idx].filter((item) => item === 0 || item === inside.value.length - 1);
  }

  if (!selectedForMove.value.length) {
    dragHint.value = 'Можно выделять только крайние непрерывные предложения.';
    return;
  }

  const nextState = moveSelection.value;
  if (nextState.mode === 'head') dragHint.value = `Выделено ${nextState.count} с начала. Перетащи в PREV.`;
  if (nextState.mode === 'tail') dragHint.value = `Выделено ${nextState.count} с конца. Перетащи в NEXT.`;
}

function onSentenceClick(event: MouseEvent, localIdx: number) {
  if (event.ctrlKey) {
    toggleSelection(localIdx);
    return;
  }

  splitIdx.value = startValue.value + localIdx;
}

function onSentenceDragStart(event: DragEvent, localIdx: number) {
  const state = moveSelection.value;
  const fallbackHead = localIdx === 0 ? 1 : 0;
  const fallbackTail = localIdx === inside.value.length - 1 ? 1 : 0;
  const count = state.count || fallbackHead || fallbackTail;

  if (state.mode === 'head' || fallbackHead) {
    if (!props.hasPrev || count > maxMovable.value) {
      event.preventDefault();
      return;
    }
    event.dataTransfer?.setData('text/plain', JSON.stringify({ mode: 'head', count }));
    dragHint.value = `Отпусти в PREV: уйдут ${count} предлож.`;
    return;
  }

  if (state.mode === 'tail' || fallbackTail) {
    if (!props.hasNext || count > maxMovable.value) {
      event.preventDefault();
      return;
    }
    event.dataTransfer?.setData('text/plain', JSON.stringify({ mode: 'tail', count }));
    dragHint.value = `Отпусти в NEXT: уйдут ${count} предлож.`;
    return;
  }

  event.preventDefault();
}

function onSentenceDragEnd() {
  activeDropZone.value = null;
  if (!selectedForMove.value.length) dragHint.value = defaultHint;
}

function allowDrop(event: DragEvent, zone: 'prev' | 'next') {
  event.preventDefault();
  activeDropZone.value = zone;
}

function onLeaveDropZone() {
  activeDropZone.value = null;
}

function parsePayload(raw: string | undefined) {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as { mode: 'head' | 'tail'; count: number };
  } catch {
    return null;
  }
}

function onDropToPrev(event: DragEvent) {
  event.preventDefault();
  activeDropZone.value = null;
  const payload = parsePayload(event.dataTransfer?.getData('text/plain'));
  if (!payload || payload.mode !== 'head' || !props.hasPrev) {
    dragHint.value = 'В PREV можно переносить только выделение с начала сцены.';
    return;
  }

  commitRange(startValue.value + payload.count, endValue.value);
  dragHint.value = `Готово: ${payload.count} предлож. ушли в предыдущую сцену.`;
}

function onDropToNext(event: DragEvent) {
  event.preventDefault();
  activeDropZone.value = null;
  const payload = parsePayload(event.dataTransfer?.getData('text/plain'));
  if (!payload || payload.mode !== 'tail' || !props.hasNext) {
    dragHint.value = 'В NEXT можно переносить только выделение с конца сцены.';
    return;
  }

  commitRange(startValue.value, endValue.value - payload.count);
  dragHint.value = `Готово: ${payload.count} предлож. ушли в следующую сцену.`;
}

function isSelected(idx: number) {
  return selectedForMove.value.includes(idx);
}
</script>

<template>
  <section class="comic-card space-y-4 bg-white p-5 xl:p-6">
    <div class="rounded-lg border-2 border-slate-900 bg-amber-50 p-3 text-sm">
      <p class="font-black">Редактирование границ</p>
      <ol class="mt-1 list-decimal pl-5 text-xs text-slate-700">
        <li><b>Ctrl + ЛКМ</b> выделяет несколько крайних предложений.</li>
        <li>Выделение с начала дропай в <b>PREV</b>, с конца — в <b>NEXT</b>.</li>
        <li>Остаётся минимум 2 предложения, середина не переносится.</li>
      </ol>
    </div>

    <div class="flex items-center justify-between gap-2">
      <div>
        <h2 class="comic-title text-2xl font-black">{{ scene.title }}</h2>
        <p class="text-sm text-slate-600">Границы сцены: {{ startValue }}-{{ endValue }}</p>
      </div>
      <button class="kaboom-btn" :class="scene.status === 'approved' ? 'bg-emerald-300' : ''" @click="emit('approve', scene.id, scene.status !== 'approved')">
        {{ scene.status === 'approved' ? 'Unapprove' : 'Approve' }}
      </button>
    </div>

    <div class="panel-frame">
      <img v-if="illustration" :src="illustration.imageUrl" alt="scene illustration" class="h-80 w-full object-cover" />
      <div v-else class="flex h-80 items-center justify-center bg-slate-200 text-slate-500">Иллюстрация пока не готова</div>
    </div>

    <div class="rounded-xl border-2 border-slate-900 bg-white p-3">
      <p class="text-sm font-semibold">Подсказка</p>
      <p class="mt-1 text-xs text-slate-600">{{ dragHint }}</p>
    </div>

    <div class="speech-bubble">
      <button class="mb-2 text-sm font-semibold text-blue-700" @click="expanded = !expanded">{{ expanded ? 'Свернуть текст' : 'Развернуть текст' }}</button>
      <p class="text-sm leading-7 text-slate-700" :class="expanded ? '' : 'line-clamp-3'">{{ scene.text }}</p>
    </div>

    <div class="grid gap-3 xl:grid-cols-3">
      <div
        class="story-strip border-2 border-dashed"
        :class="[hasPrev ? 'border-emerald-700 bg-emerald-50' : 'border-slate-300 bg-slate-50', activeDropZone === 'prev' ? 'ring-2 ring-emerald-500' : '']"
        @dragover="allowDrop($event, 'prev')"
        @dragleave="onLeaveDropZone"
        @drop="onDropToPrev"
      >
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст до · PREV</p>
        <p v-if="hasPrev" class="mb-1 text-[11px] font-semibold text-emerald-700">Drop выделения начала сцены</p>
        <p class="text-xs text-slate-600">{{ before.join(' ') || '—' }}</p>
      </div>

      <div class="story-strip border-slate-900 bg-blue-50 xl:col-span-1">
        <p class="mb-1 text-xs font-bold uppercase text-slate-700">Текущая сцена (Ctrl+ЛКМ / drag / клик для split)</p>
        <ul class="max-h-80 space-y-1 overflow-y-auto">
          <li
            v-for="(sentence, localIdx) in inside"
            :key="`${scene.id}-${localIdx}`"
            class="cursor-pointer rounded border border-slate-200 px-2 py-1 text-sm"
            :class="[
              splitIdx === startValue + localIdx ? 'bg-yellow-200 border-slate-900' : 'bg-white',
              isSelected(localIdx) ? 'border-indigo-700 bg-indigo-100' : '',
              localIdx === 0 ? 'border-l-4 border-l-emerald-700' : '',
              localIdx === inside.length - 1 ? 'border-r-4 border-r-violet-700' : '',
            ]"
            :draggable="localIdx === 0 || localIdx === inside.length - 1 || isSelected(localIdx)"
            @dragstart="onSentenceDragStart($event, localIdx)"
            @dragend="onSentenceDragEnd"
            @click="onSentenceClick($event, localIdx)"
          >
            <span class="mr-1 text-[10px] text-slate-400">{{ startValue + localIdx }}.</span>
            {{ sentence }}
          </li>
        </ul>
      </div>

      <div
        class="story-strip border-2 border-dashed"
        :class="[hasNext ? 'border-violet-700 bg-violet-50' : 'border-slate-300 bg-slate-50', activeDropZone === 'next' ? 'ring-2 ring-violet-500' : '']"
        @dragover="allowDrop($event, 'next')"
        @dragleave="onLeaveDropZone"
        @drop="onDropToNext"
      >
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Контекст после · NEXT</p>
        <p v-if="hasNext" class="mb-1 text-[11px] font-semibold text-violet-700">Drop выделения конца сцены</p>
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
