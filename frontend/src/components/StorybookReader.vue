<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scenes: Scene[];
  illustrations: Record<string, Illustration>;
}>();

const page = ref(1);
const scenesPerPage = ref(1);
const fontScale = ref<'md' | 'lg' | 'xl'>('lg');
const layoutMode = ref<'stacked' | 'split'>('split');
const panelHeight = ref(420);

const readerScenes = computed(() => {
  const base = [...props.scenes].sort((a, b) => a.index - b.index);
  return base;
});

const totalPages = computed(() => Math.max(1, Math.ceil(readerScenes.value.length / scenesPerPage.value)));
const canPrev = computed(() => page.value > 1);
const canNext = computed(() => page.value < totalPages.value);
const isSplit = computed(() => layoutMode.value === 'split');
const paged = computed(() => {
  const safe = Math.min(Math.max(1, page.value), totalPages.value);
  const start = (safe - 1) * scenesPerPage.value;
  return readerScenes.value.slice(start, start + scenesPerPage.value);
});

const pageItems = computed(() => {
  const total = totalPages.value;
  const current = page.value;
  if (total <= 9) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const items: Array<number | 'gap'> = [1];
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  if (start > 2) items.push('gap');
  for (let n = start; n <= end; n += 1) items.push(n);
  if (end < total - 1) items.push('gap');
  items.push(total);

  return items;
});

const textClass = computed(() => {
  if (fontScale.value === 'xl') return 'text-xl leading-10';
  if (fontScale.value === 'lg') return 'text-lg leading-9';
  return 'text-base leading-8';
});

watch([scenesPerPage], () => {
  page.value = 1;
});

watch(totalPages, (value) => {
  if (page.value > value) page.value = value;
});

watch(layoutMode, (mode) => {
  if (mode === 'split' && scenesPerPage.value !== 1) {
    scenesPerPage.value = 1;
  }
});

const container = ref<HTMLElement | null>(null);

function nextPage() {
  page.value = Math.min(totalPages.value, page.value + 1);
}

function prevPage() {
  page.value = Math.max(1, page.value - 1);
}

function getImage(scene: Scene) {
  return props.illustrations[scene.id]?.imageUrl;
}

function jumpTo(index: number) {
  page.value = index;
}

const imageBoxStyle = computed(() => (isSplit.value ? { height: `${panelHeight.value}px` } : {}));
const textBoxStyle = computed(() => (isSplit.value ? { height: `${panelHeight.value}px` } : {}));

function isTypingTarget(target: EventTarget | null) {
  const node = target as HTMLElement | null;
  if (!node) return false;
  const tag = node.tagName?.toLowerCase();
  return tag === 'input' || tag === 'textarea' || tag === 'select' || node.isContentEditable;
}

function handleKey(event: KeyboardEvent) {
  if (isTypingTarget(event.target)) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') {
    if (canNext.value) nextPage();
    event.preventDefault();
  }
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
    if (canPrev.value) prevPage();
    event.preventDefault();
  }
}

watch(page, () => {
  if (!container.value) return;
  requestAnimationFrame(() => {
    container.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

onMounted(() => {
  window.addEventListener('keydown', handleKey);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKey);
});
</script>

<template>
  <section ref="container" class="comic-card relative overflow-hidden bg-white p-5">
    <div class="pointer-events-none absolute inset-0 opacity-30 halftone"></div>

    <div class="relative z-10 mb-4 rounded-2xl border border-slate-200 bg-white/90 p-4">
      <h2 class="comic-title text-3xl font-semibold">Режим чтения</h2>
      <p class="mt-1 text-sm text-slate-600">Иллюстрация встроена в текст, показываем историю целиком.</p>
      <p class="mt-1 text-xs text-slate-500">Навигация: кнопки сверху или стрелки ← → на клавиатуре.</p>
      <p v-if="isSplit" class="mt-1 text-xs text-slate-500">Разделенный макет показывает одну сцену на разворот.</p>

      <div class="mt-4 grid gap-2 md:grid-cols-4">
        <label class="reader-chip">
          Сцен на разворот:
          <select v-model.number="scenesPerPage" class="reader-select" :disabled="isSplit">
            <option :value="1">1</option>
            <option :value="2" :disabled="isSplit">2</option>
          </select>
        </label>

        <label class="reader-chip">
          Размер текста:
          <select v-model="fontScale" class="reader-select">
            <option value="md">M</option>
            <option value="lg">L</option>
            <option value="xl">XL</option>
          </select>
        </label>

        <label class="reader-chip">
          Макет:
          <select v-model="layoutMode" class="reader-select">
            <option value="split">Разделенный</option>
            <option value="stacked">Вертикальный</option>
          </select>
        </label>

        <label v-if="isSplit" class="reader-chip">
          Высота панели:
          <input v-model.number="panelHeight" type="range" min="320" max="560" step="20" class="reader-select" />
          <span class="text-xs text-slate-500">{{ panelHeight }}px</span>
        </label>
      </div>
    </div>

    <div class="relative z-10 mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
      <div class="flex items-center gap-2">
        <button class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-sm font-semibold disabled:opacity-50" :disabled="!canPrev" @click="prevPage">← Назад</button>
        <button class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-sm font-semibold disabled:opacity-50" :disabled="!canNext" @click="nextPage">Далее →</button>
      </div>
      <span>Разворот {{ page }} / {{ totalPages }}</span>
      <span class="rounded-full bg-slate-900 px-2 py-0.5 text-xs text-white">{{ readerScenes.length }} сцен</span>
    </div>

    <div class="relative z-10 space-y-8">
      <article
        v-for="scene in paged"
        :key="scene.id"
        class="storybook-spread"
        :class="isSplit ? 'grid gap-6 lg:grid-cols-2' : 'space-y-4'"
      >
        <header class="mb-3 flex items-center justify-between gap-2 lg:col-span-2">
          <h3 class="text-3xl font-semibold">Глава {{ scene.index }} · {{ scene.title ?? `Сцена ${scene.sceneNumber}` }}</h3>
        </header>

        <div
          class="panel-frame"
          :class="isSplit ? 'w-full' : 'mx-auto w-full max-w-5xl aspect-[3/2]'"
          :style="imageBoxStyle"
        >
          <img v-if="getImage(scene)" :src="getImage(scene)" alt="panel" class="h-full w-full object-cover" />
          <div v-else class="flex h-full w-full items-center justify-center bg-slate-200 text-slate-500">Иллюстрация пока не готова</div>
        </div>

        <div
          class="rounded-2xl border border-slate-200 bg-white/95 p-6 shadow-sm"
          :class="[textClass, isSplit ? 'w-full overflow-y-auto' : 'mx-auto mt-4 max-w-4xl']"
          :style="textBoxStyle"
        >
          {{ scene.text }}
        </div>
      </article>
    </div>

    <div class="relative z-10 mt-5 flex flex-wrap items-center justify-between gap-3">
      <button class="kaboom-btn disabled:opacity-50" :disabled="page <= 1" @click="prevPage">Назад</button>

      <div class="flex max-w-full items-center gap-1 overflow-x-auto rounded-lg border border-slate-300 bg-white px-2 py-1">
        <template v-for="item in pageItems" :key="`page-${item}`">
          <span v-if="item === 'gap'" class="px-2 text-xs text-slate-400">…</span>
          <button
            v-else
            class="h-7 min-w-7 rounded text-xs font-semibold"
            :class="item === page ? 'bg-slate-900 text-white' : 'bg-slate-100 hover:bg-slate-200'"
            @click="jumpTo(item)"
          >
            {{ item }}
          </button>
        </template>
      </div>

      <button class="kaboom-btn disabled:opacity-50" :disabled="page >= totalPages" @click="nextPage">Далее</button>
    </div>
  </section>
</template>
