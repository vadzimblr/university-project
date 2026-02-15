import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import type { Document } from '@/types/models';
import { mockDocuments } from '@/mock/mockDocuments';

export const useDocumentsStore = defineStore('documents', () => {
  const recentDocuments = ref<Document[]>(mockDocuments);
  const activeDocumentId = ref<string | null>(null);

  const activeDocument = computed(() =>
    recentDocuments.value.find((doc) => doc.id === activeDocumentId.value) ?? null,
  );

  function setActiveDocument(id: string) {
    activeDocumentId.value = id;
  }

  function addDocument(name: string) {
    const newDoc: Document = {
      id: `doc-${Math.random().toString(36).slice(2, 10)}`,
      name,
      pagesCount: Math.floor(14 + Math.random() * 22),
      uploadedAt: new Date().toISOString(),
    };

    recentDocuments.value.unshift(newDoc);
    activeDocumentId.value = newDoc.id;
    return newDoc;
  }

  return {
    recentDocuments,
    activeDocumentId,
    activeDocument,
    addDocument,
    setActiveDocument,
  };
});
