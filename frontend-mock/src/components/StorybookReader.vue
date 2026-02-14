<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scenes: Scene[];
  illustrations: Record<string, Illustration>;
}>();

const page = ref(1);
const scenesPerPage = ref(1);
const showOnlyReady = ref(false);
const fontScale = ref<'md' | 'lg' | 'xl'>('lg');

const readerScenes = computed(() => {
  const base = [...props.scenes].sort((a, b) => a.index - b.index);
  return showOnlyReady.value ? base.filter((s) => s.status === 'ready') : base;
});

const totalPages = computed(() => Math.max(1, Math.ceil(readerScenes.value.length / scenesPerPage.value)));
const paged = computed(() => {
  const safe = Math.min(Math.max(1, page.value), totalPages.value);
  const start = (safe - 1) * scenesPerPage.value;
  return readerScenes.value.slice(start, start + scenesPerPage.value);
});

const textClass = computed(() => {
  if (fontScale.value === 'xl') return 'text-xl leading-10';
  if (fontScale.value === 'lg') return 'text-lg leading-9';
  return 'text-base leading-8';
});

watch([scenesPerPage, showOnlyReady], () => {
  page.value = 1;
});

watch(totalPages, (value) => {
  if (page.value > value) page.value = value;
});

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
</script>

<template>
  <section class="comic-card relative overflow-hidden bg-white p-5">
    <div class="pointer-events-none absolute inset-0 opacity-30 halftone"></div>

    <div class="relative z-10 mb-4 rounded-2xl border-2 border-slate-900 bg-amber-50 p-4">
      <h2 class="comic-title text-3xl font-black">📖 Storybook Reader</h2>
      <p class="mt-1 text-sm text-slate-700">Плавный режим чтения: иллюстрация встроена в историю, текст идёт как единый разворот.</p>

      <div class="mt-4 grid gap-2 md:grid-cols-3">
        <label class="reader-chip">
          <input v-model="showOnlyReady" type="checkbox" class="mr-1" /> только готовые сцены
        </label>

        <label class="reader-chip">
          Сцен на разворот:
          <select v-model.number="scenesPerPage" class="reader-select">
            <option :value="1">1</option>
            <option :value="2">2</option>
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
      </div>
    </div>

    <div class="relative z-10 mb-4 flex items-center justify-between rounded-xl border-2 border-slate-900 bg-white px-3 py-2 text-sm font-semibold">
      <span>Разворот {{ page }} / {{ totalPages }}</span>
      <span class="rounded-full bg-slate-900 px-2 py-0.5 text-xs text-white">{{ readerScenes.length }} сцен</span>
    </div>

    <div class="relative z-10 space-y-8">
      <article v-for="scene in paged" :key="scene.id" class="storybook-spread">
        <header class="mb-3 flex items-center justify-between gap-2">
          <h3 class="text-3xl font-black">Глава {{ scene.index }} · {{ scene.title }}</h3>
          <span class="rounded-full border border-slate-900 bg-white px-2 py-0.5 text-xs">{{ scene.status }}</span>
        </header>

        <div class="panel-frame mx-auto max-w-5xl">
          <img v-if="getImage(scene)" :src="getImage(scene)" alt="panel" class="h-[420px] w-full object-cover" />
          <div v-else class="flex h-[420px] items-center justify-center bg-slate-200 text-slate-500">Иллюстрация пока не готова</div>
        </div>

        <div class="mx-auto mt-4 max-w-4xl rounded-2xl border-2 border-slate-900 bg-white/95 p-6 shadow-[5px_5px_0_#111827]" :class="textClass">
          {{ scene.text }}
        </div>
      </article>
    </div>

    <div class="relative z-10 mt-5 flex flex-wrap items-center justify-between gap-3">
      <button class="kaboom-btn disabled:opacity-50" :disabled="page <= 1" @click="prevPage">← Назад</button>

      <div class="flex max-w-full gap-1 overflow-x-auto rounded-lg border border-slate-300 bg-white px-2 py-1">
        <button
          v-for="n in totalPages"
          :key="`page-${n}`"
          class="h-7 min-w-7 rounded text-xs font-semibold"
          :class="n === page ? 'bg-slate-900 text-white' : 'bg-slate-100 hover:bg-slate-200'"
          @click="jumpTo(n)"
        >
          {{ n }}
        </button>
      </div>

      <button class="kaboom-btn disabled:opacity-50" :disabled="page >= totalPages" @click="nextPage">Далее →</button>
    </div>
  </section>
</template>
