<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useRouter } from 'vue-router';
import { statusLabel } from '@/utils/statusLabel';

const documentsStore = useDocumentsStore();
const router = useRouter();

const dragOver = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const startPage = ref(1);
const endPage = ref(999);
const isUploading = ref(false);
const errorMsg = ref<string | null>(null);

const statusFilter = ref<'all' | 'pending' | 'in-progress' | 'ready' | 'approved' | 'failed'>('all');
const sortBy = ref<'date-desc' | 'date-asc' | 'name-asc' | 'name-desc'>('date-desc');
const hasDocs = computed(() => documentsStore.documents.length > 0);
const documentsView = computed(() => {
  const normalized = documentsStore.documents.map((d) => {
    const latest = d.processingJobs[0];
    const statusRaw = latest?.status?.toLowerCase() ?? '';
    const statusBucket =
      statusRaw === 'approved'
        ? 'approved'
        : statusRaw === 'failed'
          ? 'failed'
          : ['pending'].includes(statusRaw)
            ? 'pending'
            : statusRaw.includes('ready')
              ? 'ready'
              : statusRaw
                ? 'in-progress'
                : 'pending';
    return {
      ...d,
      statusRaw,
      statusBucket,
      statusLabel: latest ? statusLabel(latest.status) : 'Нет задач',
      uploadedDate: d.uploadedAt ? new Date(d.uploadedAt) : null,
      uploaded: d.uploadedAt ? new Date(d.uploadedAt).toLocaleString() : '—',
    };
  });

  const filtered =
    statusFilter.value === 'all'
      ? normalized
      : normalized.filter((d) => d.statusBucket === statusFilter.value);

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy.value === 'name-asc') return a.filename.localeCompare(b.filename);
    if (sortBy.value === 'name-desc') return b.filename.localeCompare(a.filename);
    const ta = a.uploadedDate?.getTime() ?? 0;
    const tb = b.uploadedDate?.getTime() ?? 0;
    return sortBy.value === 'date-asc' ? ta - tb : tb - ta;
  });

  return sorted;
});

onMounted(() => {
  documentsStore.loadDocuments().catch((e) => {
    errorMsg.value = e?.message ?? 'Не удалось загрузить документы';
  });
});

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  selectedFile.value = file ?? null;
}

async function submitUpload() {
  if (!selectedFile.value) {
    errorMsg.value = 'Выберите PDF файл';
    return;
  }
  errorMsg.value = null;
  isUploading.value = true;
  try {
    const resp = await documentsStore.upload(selectedFile.value, startPage.value, endPage.value);
    router.push(`/doc/${resp.document_id}`);
  } catch (e: any) {
    errorMsg.value = e?.message ?? 'Ошибка загрузки';
  } finally {
    isUploading.value = false;
  }
}

function openDocument(docId: string) {
  documentsStore.setActiveDocument(docId);
  router.push(`/doc/${docId}`);
}
</script>

<template>
  <main class="page-fade mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-10 lg:px-6">
    <section class="comic-card halftone p-8">
      <p class="text-[11px] font-semibold uppercase tracking-[0.32em] text-slate-500">Storybook AI Studio</p>
      <h1 class="comic-title mt-3 text-3xl font-semibold md:text-4xl">Преврати рассказ из PDF в визуальную историю</h1>
      <p class="mt-3 max-w-3xl text-slate-600">Собери сцены с правильными границами, ритмом и атмосферой, чтобы история читалась как цельный storybook.</p>
    </section>

    <section
      class="comic-card bg-white/90 p-10 text-center"
      :class="dragOver ? 'ring-2 ring-emerald-200' : ''"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="dragOver = false"
    >
      <p class="comic-title text-2xl font-semibold">Загрузить PDF</p>
      <p class="mt-2 text-sm text-slate-600">Укажите диапазон страниц для извлечения и загрузите файл.</p>

      <div class="mt-4 flex flex-col items-center gap-3">
        <input ref="fileInput" type="file" accept="application/pdf" class="hidden" @change="onFileChange" />
        <button class="kaboom-btn" @click="fileInput?.click()">Выбрать файл</button>
        <p class="text-sm text-slate-500">{{ selectedFile?.name ?? 'Файл не выбран' }}</p>

        <div class="flex flex-wrap items-center justify-center gap-3 text-sm">
          <label class="flex items-center gap-2">
            <span>Старт:</span>
            <input v-model.number="startPage" type="number" min="1" class="w-20 rounded border border-slate-200 px-2 py-1" />
          </label>
          <label class="flex items-center gap-2">
            <span>Конец:</span>
            <input v-model.number="endPage" type="number" min="1" class="w-20 rounded border border-slate-200 px-2 py-1" />
          </label>
        </div>

        <button class="kaboom-btn mt-2" :disabled="isUploading" @click="submitUpload">
          {{ isUploading ? 'Загружаем...' : 'Загрузить' }}
        </button>
        <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>
      </div>
    </section>

    <section class="comic-card bg-white p-5">
      <div class="flex items-center justify-between">
        <h2 class="comic-title mb-3 text-lg font-semibold">Документы</h2>
        <button class="rounded-full border border-slate-200 px-3 py-1 text-sm" @click="documentsStore.loadDocuments()">Обновить</button>
      </div>

      <div class="mb-3 flex flex-wrap items-center gap-3 text-sm">
        <label class="flex items-center gap-2">
          <span>Статус:</span>
          <select v-model="statusFilter" class="rounded border border-slate-200 px-2 py-1">
            <option value="all">Все</option>
            <option value="pending">В очереди</option>
            <option value="in-progress">В процессе</option>
            <option value="ready">Готово к ревью</option>
            <option value="approved">Одобрено</option>
            <option value="failed">Ошибка</option>
          </select>
        </label>
        <label class="flex items-center gap-2">
          <span>Сортировка:</span>
          <select v-model="sortBy" class="rounded border border-slate-200 px-2 py-1">
            <option value="date-desc">Новые сверху</option>
            <option value="date-asc">Старые сверху</option>
            <option value="name-asc">Имя A→Z</option>
            <option value="name-desc">Имя Z→A</option>
          </select>
        </label>
      </div>

      <div v-if="documentsStore.loading" class="text-sm text-slate-500">Загружаем...</div>
      <div v-else-if="documentsStore.error" class="text-sm text-red-600">{{ documentsStore.error }}</div>
      <div v-else-if="!hasDocs" class="text-sm text-slate-500">Документов пока нет</div>

      <ul v-else class="space-y-2">
        <li v-for="doc in documentsView" :key="doc.id" class="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <p class="font-semibold">{{ doc.filename }}</p>
              <p class="text-xs text-slate-500">Загружен: {{ doc.uploaded }}</p>
              <p class="text-xs text-slate-500">Статус: {{ doc.statusLabel }}</p>
            </div>
            <button class="kaboom-btn" @click="openDocument(doc.id)">Открыть</button>
          </div>
        </li>
      </ul>
    </section>
  </main>
</template>
