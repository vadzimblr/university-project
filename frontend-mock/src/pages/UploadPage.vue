<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useScenesStore } from '@/stores/scenesStore';
import { useUiStore } from '@/stores/uiStore';

const router = useRouter();
const documentsStore = useDocumentsStore();
const scenesStore = useScenesStore();
const uiStore = useUiStore();

const dragOver = ref(false);
let timer: number | null = null;

const isProcessing = computed(() => uiStore.processingStage !== 'idle' && uiStore.processingStage !== 'done');

function selectDocument(name: string) {
  documentsStore.addDocument(name);
  startMockFlow();
}

function openRecent(docId: string) {
  documentsStore.setActiveDocument(docId);
  startMockFlow();
}

function startMockFlow() {
  uiStore.processingStage = 'upload';
  uiStore.uploadProgress = 0;
  uiStore.segmentationProgress = 0;

  timer = window.setInterval(() => {
    if (uiStore.processingStage === 'upload') {
      uiStore.uploadProgress = Math.min(100, uiStore.uploadProgress + 8);
      if (uiStore.uploadProgress >= 100) uiStore.processingStage = 'segmenting';
      return;
    }

    if (uiStore.processingStage === 'segmenting') {
      uiStore.segmentationProgress = Math.min(100, uiStore.segmentationProgress + 10);
      if (uiStore.segmentationProgress >= 100) {
        uiStore.processingStage = 'done';
        scenesStore.segmentStory();
        uiStore.selectedSceneId = scenesStore.scenes[0]?.id ?? null;
        if (documentsStore.activeDocumentId) router.push(`/doc/${documentsStore.activeDocumentId}`);
      }
    }
  }, 260);
}

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<template>
  <main class="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-10 lg:px-6">
    <section class="comic-card halftone p-6">
      <p class="text-xs font-bold uppercase tracking-[0.3em] text-slate-500">Storybook AI Studio</p>
      <h1 class="comic-title mt-2 text-3xl font-black md:text-4xl">Преврати рассказ из PDF в комикс-кадры</h1>
      <p class="mt-3 max-w-3xl text-slate-700">Не просто “сгенерировать картинки”: собери визуальную историю с правильными границами сцен, ритмом и атмосферой.</p>
    </section>

    <section
      class="comic-card bg-white p-10 text-center"
      :class="dragOver ? 'ring-4 ring-blue-300' : ''"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="dragOver = false; selectDocument('Новый рассказ.pdf')"
    >
      <p class="text-2xl font-black comic-title">DROP PDF!</p>
      <p class="mt-2 text-sm text-slate-600">Перетащите файл в панель или выберите его вручную.</p>
      <button class="kaboom-btn mt-4" @click="selectDocument('Новый рассказ.pdf')">Выбрать PDF</button>
    </section>

    <section class="comic-card bg-white p-4">
      <h2 class="comic-title mb-3 text-lg font-black">Недавние документы</h2>
      <ul class="space-y-2">
        <li v-for="doc in documentsStore.recentDocuments" :key="doc.id" class="rounded-xl border-2 border-slate-200 bg-slate-50 p-3">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="font-semibold">{{ doc.name }}</p>
              <p class="text-xs text-slate-500">{{ doc.pagesCount }} pages · {{ new Date(doc.uploadedAt).toLocaleString() }}</p>
            </div>
            <button class="kaboom-btn" @click="openRecent(doc.id)">Открыть</button>
          </div>
        </li>
      </ul>
    </section>

    <section v-if="isProcessing" class="comic-card bg-white p-4">
      <h3 class="comic-title text-base font-black">Подготовка комикса</h3>
      <div class="mt-3 space-y-3">
        <div>
          <p class="mb-1 text-sm font-medium">Upload: {{ uiStore.uploadProgress }}%</p>
          <div class="h-3 rounded-full border-2 border-slate-900 bg-slate-100"><div class="h-full rounded-full bg-blue-500" :style="{ width: `${uiStore.uploadProgress}%` }" /></div>
        </div>
        <div>
          <p class="mb-1 text-sm font-medium">Segmenting: {{ uiStore.segmentationProgress }}%</p>
          <div class="h-3 rounded-full border-2 border-slate-900 bg-slate-100"><div class="h-full rounded-full bg-emerald-500" :style="{ width: `${uiStore.segmentationProgress}%` }" /></div>
        </div>
      </div>
    </section>
  </main>
</template>
