<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scenes: Scene[];
  illustrations: Record<string, Illustration>;
}>();

const page = ref(1);
const scenesPerPage = ref(4);
const showOnlyReady = ref(false);
const fontScale = ref<'md' | 'lg'>('lg');

const readerScenes = computed(() => {
  const base = [...props.scenes].sort((a, b) => a.index - b.index);
  if (!showOnlyReady.value) return base;
  return base.filter((s) => s.status === 'ready');
});

const totalPages = computed(() => Math.max(1, Math.ceil(readerScenes.value.length / scenesPerPage.value)));
const paged = computed(() => {
  const safe = Math.min(Math.max(1, page.value), totalPages.value);
  const start = (safe - 1) * scenesPerPage.value;
  return readerScenes.value.slice(start, start + scenesPerPage.value);
});

const textClass = computed(() => (fontScale.value === 'lg' ? 'text-base leading-8' : 'text-sm leading-7'));

function nextPage() {
  page.value = Math.min(totalPages.value, page.value + 1);
}

function prevPage() {
  page.value = Math.max(1, page.value - 1);
}

function getImage(scene: Scene) {
  return props.illustrations[scene.id]?.imageUrl;
}
</script>

<template>
  <section class="comic-card bg-white p-4">
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="comic-title text-xl font-black">Storybook Reader</h2>
        <p class="text-xs text-slate-600">Цельный просмотр истории как книги/комикса.</p>
      </div>

      <div class="flex flex-wrap items-center gap-2 text-xs">
        <label class="rounded border-2 border-slate-900 bg-white px-2 py-1 font-semibold">
          <input v-model="showOnlyReady" type="checkbox" class="mr-1" /> only ready
        </label>
        <select v-model.number="scenesPerPage" class="rounded border-2 border-slate-900 px-2 py-1">
          <option :value="2">2 scenes/page</option>
          <option :value="4">4 scenes/page</option>
          <option :value="6">6 scenes/page</option>
        </select>
        <select v-model="fontScale" class="rounded border-2 border-slate-900 px-2 py-1">
          <option value="md">Text M</option>
          <option value="lg">Text L</option>
        </select>
      </div>
    </div>

    <div class="mb-3 flex items-center justify-between rounded-lg border-2 border-slate-900 bg-amber-50 px-3 py-2 text-xs font-semibold">
      <span>Страница {{ page }} / {{ totalPages }}</span>
      <span>{{ readerScenes.length }} сцен в текущем режиме</span>
    </div>

    <div class="grid gap-3 md:grid-cols-2">
      <article v-for="scene in paged" :key="scene.id" class="rounded-xl border-2 border-slate-900 bg-slate-50 p-3">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="font-black">Глава {{ scene.index }} · {{ scene.title }}</h3>
          <span class="rounded border border-slate-900 bg-white px-2 py-0.5 text-[11px]">{{ scene.status }}</span>
        </div>

        <div class="panel-frame mb-3">
          <img v-if="getImage(scene)" :src="getImage(scene)" alt="panel" class="h-52 w-full object-cover" />
          <div v-else class="flex h-52 items-center justify-center bg-slate-200 text-slate-500">Иллюстрация ещё не готова</div>
        </div>

        <p class="rounded-lg border border-slate-300 bg-white p-3 text-slate-700" :class="textClass">{{ scene.text }}</p>
      </article>
    </div>

    <div class="mt-4 flex justify-between">
      <button class="rounded border-2 border-slate-900 bg-white px-3 py-1.5 text-sm font-semibold" :disabled="page <= 1" @click="prevPage">← Предыдущая</button>
      <button class="rounded border-2 border-slate-900 bg-white px-3 py-1.5 text-sm font-semibold" :disabled="page >= totalPages" @click="nextPage">Следующая →</button>
    </div>
  </section>
</template>
