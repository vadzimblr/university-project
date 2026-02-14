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
        if (documentsStore.activeDocumentId) {
          router.push(`/doc/${documentsStore.activeDocumentId}`);
        }
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
    <section>
      <h1 class="text-2xl font-bold">PDF Story Illustration — Mock Upload</h1>
      <p class="text-slate-600">Загрузите PDF, дождитесь сегментации, затем отредактируйте сцены и запустите генерацию.</p>
    </section>

    <section
      class="rounded-2xl border-2 border-dashed bg-white p-10 text-center"
      :class="dragOver ? 'border-brand-500 bg-brand-50' : 'border-slate-300'"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="dragOver = false; selectDocument('Новый рассказ.pdf')"
    >
      <p class="text-lg font-semibold">Перетащите PDF сюда</p>
      <p class="mt-1 text-sm text-slate-500">или используйте кнопку ниже</p>
      <button class="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white" @click="selectDocument('Новый рассказ.pdf')">
        Выбрать PDF
      </button>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-4">
      <h2 class="mb-3 text-lg font-semibold">Недавние документы</h2>
      <ul class="space-y-2">
        <li v-for="doc in documentsStore.recentDocuments" :key="doc.id" class="flex items-center justify-between rounded-lg border border-slate-100 p-3">
          <div>
            <p class="font-medium">{{ doc.name }}</p>
            <p class="text-xs text-slate-500">{{ doc.pagesCount }} pages · {{ new Date(doc.uploadedAt).toLocaleString() }}</p>
          </div>
          <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm" @click="openRecent(doc.id)">Открыть</button>
        </li>
      </ul>
    </section>

    <section v-if="isProcessing" class="rounded-xl border border-slate-200 bg-white p-4">
      <h3 class="text-base font-semibold">Processing</h3>
      <div class="mt-3 space-y-3">
        <div>
          <p class="mb-1 text-sm">Upload: {{ uiStore.uploadProgress }}%</p>
          <div class="h-2 rounded bg-slate-100"><div class="h-2 rounded bg-brand-600" :style="{ width: `${uiStore.uploadProgress}%` }" /></div>
        </div>
        <div>
          <p class="mb-1 text-sm">Segmenting: {{ uiStore.segmentationProgress }}%</p>
          <div class="h-2 rounded bg-slate-100"><div class="h-2 rounded bg-emerald-600" :style="{ width: `${uiStore.segmentationProgress}%` }" /></div>
        </div>
      </div>
    </section>
  </main>
</template>
