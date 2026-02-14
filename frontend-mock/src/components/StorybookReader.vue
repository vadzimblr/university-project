<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Illustration, Scene } from '@/types/models';

const props = defineProps<{
  scenes: Scene[];
  illustrations: Record<string, Illustration>;
}>();

const page = ref(1);
const scenesPerPage = ref(2);
const showOnlyReady = ref(false);
const fontScale = ref<'md' | 'lg'>('lg');

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

const textClass = computed(() => (fontScale.value === 'lg' ? 'text-lg leading-9' : 'text-base leading-8'));

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
  <section class="comic-card bg-white p-5">
    <div class="mb-4 rounded-xl border-2 border-slate-900 bg-slate-50 p-4">
      <h2 class="comic-title text-2xl font-black">📖 Storybook Reader</h2>
      <p class="mt-1 text-sm text-slate-700">Читательский режим: развороты, крупный текст и цельный нарратив без редакторского шума.</p>

      <div class="mt-3 flex flex-wrap items-center gap-2 text-sm">
        <label class="rounded border-2 border-slate-900 bg-white px-2 py-1 font-semibold">
          <input v-model="showOnlyReady" type="checkbox" class="mr-1" /> только готовые сцены
        </label>
        <select v-model.number="scenesPerPage" class="rounded border-2 border-slate-900 bg-white px-2 py-1">
          <option :value="1">1 сцена / разворот</option>
          <option :value="2">2 сцены / разворот</option>
          <option :value="3">3 сцены / разворот</option>
        </select>
        <select v-model="fontScale" class="rounded border-2 border-slate-900 bg-white px-2 py-1">
          <option value="md">Текст M</option>
          <option value="lg">Текст L</option>
        </select>
      </div>
    </div>

    <div class="mb-4 flex items-center justify-between rounded-lg border-2 border-slate-900 bg-amber-50 px-3 py-2 text-sm font-semibold">
      <span>Разворот {{ page }} / {{ totalPages }}</span>
      <span>{{ readerScenes.length }} сцен</span>
    </div>

    <div class="space-y-4">
      <article v-for="scene in paged" :key="scene.id" class="rounded-xl border-2 border-slate-900 bg-white p-4 shadow-[4px_4px_0_#111827]">
        <div class="mb-2 flex items-center justify-between gap-2">
          <h3 class="text-xl font-black">Глава {{ scene.index }}: {{ scene.title }}</h3>
          <span class="rounded border border-slate-900 bg-slate-50 px-2 py-0.5 text-xs">{{ scene.status }}</span>
        </div>

        <div class="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <div class="panel-frame">
            <img v-if="getImage(scene)" :src="getImage(scene)" alt="panel" class="h-64 w-full object-cover" />
            <div v-else class="flex h-64 items-center justify-center bg-slate-200 text-slate-500">Иллюстрация ещё не готова</div>
          </div>

          <div class="rounded-xl border border-slate-300 bg-slate-50 p-4" :class="textClass">
            {{ scene.text }}
          </div>
        </div>
      </article>
    </div>

    <div class="mt-5 flex justify-between">
      <button class="rounded border-2 border-slate-900 bg-white px-3 py-1.5 text-sm font-semibold" :disabled="page <= 1" @click="prevPage">← Назад</button>
      <button class="rounded border-2 border-slate-900 bg-white px-3 py-1.5 text-sm font-semibold" :disabled="page >= totalPages" @click="nextPage">Далее →</button>
    </div>
  </section>
</template>
