import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import type { DocumentSummary } from '@/types/models';
import { fetchDocuments, uploadDocument } from '@/api/sceneSplitter';

export const useDocumentsStore = defineStore('documents', () => {
  const documents = ref<DocumentSummary[]>([]);
  const activeDocumentId = ref<string | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const activeDocument = computed(() =>
    documents.value.find((doc) => doc.id === activeDocumentId.value) ?? null,
  );

  function setActiveDocument(id: string) {
    activeDocumentId.value = id;
  }

  async function loadDocuments() {
    loading.value = true;
    error.value = null;
    try {
      documents.value = await fetchDocuments();
    } catch (e: any) {
      error.value = e?.message ?? 'Не удалось загрузить документы';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function upload(file: File, startPage: number, endPage: number) {
    error.value = null;
    const response = await uploadDocument(file, startPage, endPage);
    const existing = documents.value.find((d) => d.id === response.document_id);
    if (!existing) {
      documents.value.unshift({
        id: response.document_id,
        filename: file.name,
        name: file.name,
        processingJobs: [{ id: response.job_id, status: response.status }],
        uploadedAt: new Date().toISOString(),
      });
    } else {
      existing.processingJobs.unshift({ id: response.job_id, status: response.status });
    }
    activeDocumentId.value = response.document_id;
    return response;
  }

  return {
    documents,
    activeDocumentId,
    activeDocument,
    loading,
    error,
    loadDocuments,
    upload,
    setActiveDocument,
  };
});
