<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import type { Scene } from '@/types/models';

const props = defineProps<{
  scene: Scene;
  sentences?: string[];
  hasPrev: boolean;
  hasNext: boolean;
}>();

const emit = defineEmits<{
  requestSentences: [];
  moveSentences: [mode: 'head' | 'tail', count: number, direction: 'prev' | 'next'];
}>();

const selected = ref<number[]>([]);
const hoverIndex = ref<number | null>(null);

function splitFallback(text: string) {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

const sentencesList = computed(() => (props.sentences && props.sentences.length ? props.sentences : splitFallback(props.scene.text)));

onMounted(() => emit('requestSentences'));

watch(
  () => props.scene.id,
  () => {
    selected.value.splice(0, selected.value.length);
    emit('requestSentences');
  },
);

function toggleSelect(idx: number, evt: MouseEvent) {
  if (!evt.ctrlKey) return;
  const pos = selected.value.indexOf(idx);
  if (pos === -1) selected.value.push(idx);
  else selected.value.splice(pos, 1);
}

const selectionInfo = computed(() => {
  const list = [...selected.value].sort((a, b) => a - b);
  if (!list.length) return { mode: null as 'head' | 'tail' | null, count: 0 };
  const len = sentencesList.value.length;
  const isHead = list[0] === 0 && list.every((v, i) => v === i);
  const isTail = list[list.length - 1] === len - 1 && list.every((v, i) => v === len - list.length + i);
  if (isHead) return { mode: 'head', count: list.length };
  if (isTail) return { mode: 'tail', count: list.length };
  return { mode: null, count: 0 };
});

function onDrop(direction: 'prev' | 'next') {
  const { mode, count } = selectionInfo.value;
  if (!mode || count === 0) return;
  if (mode === 'head' && direction === 'next') return;
  if (mode === 'tail' && direction === 'prev') return;
  if ((direction === 'prev' && !props.hasPrev) || (direction === 'next' && !props.hasNext)) return;
  emit('moveSentences', mode, count, direction);
  selected.value.splice(0, selected.value.length);
}
</script>

<template>
  <section class="comic-card space-y-4 bg-white p-5 xl:p-6">
    <div class="flex items-start justify-between gap-2">
      <div>
        <h2 class="comic-title text-2xl font-semibold">Сцена {{ scene.sceneNumber }}</h2>
        <p class="text-sm text-slate-600">Всего предложений: {{ sentencesList.length || '—' }}</p>
      </div>
    </div>

    <div class="panel-frame">
      <div class="flex h-64 items-center justify-center bg-slate-100 text-slate-500">Иллюстрация пока не готова</div>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white p-4">
      <div class="flex items-center justify-between">
        <p class="text-sm font-semibold">Текст сцены</p>
        <button class="rounded border border-slate-200 bg-white px-2 py-1 text-xs font-semibold" @click="emit('requestSentences')">Обновить</button>
      </div>

      <div class="mt-3 text-[15px] leading-7 text-slate-700">
        <span
          v-for="(sentence, idx) in sentencesList"
          :key="idx"
          class="cursor-pointer rounded-md px-1 py-0.5 transition"
          :class="[
            selected.includes(idx) ? 'bg-emerald-100 ring-1 ring-emerald-300' : '',
            hoverIndex === idx ? 'bg-slate-100' : '',
          ]"
          @mouseenter="hoverIndex = idx"
          @mouseleave="hoverIndex = null"
          @click="toggleSelect(idx, $event as MouseEvent)"
        >
          {{ sentence }}
        </span>
        <span v-if="!sentencesList.length" class="text-xs text-slate-500">Нет данных, попробуйте обновить.</span>
      </div>

      <div
        v-if="selectionInfo.mode"
        class="mt-4 flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs"
      >
        <p class="font-semibold">
          Выбрано {{ selectionInfo.count }} ({{ selectionInfo.mode === 'head' ? 'начало' : 'конец' }} сцены)
        </p>
        <button class="rounded border border-slate-200 bg-white px-3 py-1 text-sm font-semibold" :disabled="selectionInfo.mode !== 'head' || !hasPrev" @click="onDrop('prev')">
          В предыдущую сцену
        </button>
        <button class="rounded border border-slate-200 bg-white px-3 py-1 text-sm font-semibold" :disabled="selectionInfo.mode !== 'tail' || !hasNext" @click="onDrop('next')">
          В следующую сцену
        </button>
      </div>
    </div>
  </section>
</template>
