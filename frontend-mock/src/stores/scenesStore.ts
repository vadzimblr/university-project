import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import type { Illustration, Scene, SceneStatus } from '@/types/models';
import { storySentences } from '@/mock/mockStory';

const statusOrder: Record<SceneStatus, number> = {
  pending: 1,
  approved: 2,
  generating: 3,
  ready: 4,
  error: 5,
};

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createPlaceholder(scene: Scene) {
  const safeTitle = encodeURIComponent(scene.title ?? `Scene ${scene.index}`);
  return `data:image/svg+xml;utf8,\n  <svg xmlns='http://www.w3.org/2000/svg' width='960' height='540'>\n    <defs><linearGradient id='g' x1='0' x2='1' y1='0' y2='1'><stop offset='0%' stop-color='%233b82f6'/><stop offset='100%' stop-color='%237c3aed'/></linearGradient></defs>\n    <rect width='100%' height='100%' fill='url(%23g)'/>\n    <text x='50%' y='48%' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='42' font-family='Arial'>${safeTitle}</text>\n    <text x='50%' y='58%' dominant-baseline='middle' text-anchor='middle' fill='white' opacity='0.9' font-size='24' font-family='Arial'>Generated Mock Illustration</text>\n  </svg>`;
}

export const useScenesStore = defineStore('scenes', () => {
  const scenes = ref<Scene[]>([]);
  const illustrations = ref<Record<string, Illustration>>({});
  const search = ref('');
  const statusFilter = ref<'all' | SceneStatus>('all');
  const sortBy = ref<'index' | 'status'>('index');
  const isGeneratingAll = ref(false);
  const listPage = ref(1);
  const pageSize = ref(8);
  const compactCards = ref(false);

  const filteredScenes = computed(() => {
    const lowered = search.value.trim().toLowerCase();
    const prepared = scenes.value.filter((scene) => {
      const textHit = scene.text.toLowerCase().includes(lowered) || (scene.title ?? '').toLowerCase().includes(lowered);
      const filterHit = statusFilter.value === 'all' || scene.status === statusFilter.value;
      return textHit && filterHit;
    });

    return prepared.sort((a, b) => {
      if (sortBy.value === 'status') {
        return statusOrder[a.status] - statusOrder[b.status] || a.index - b.index;
      }
      return a.index - b.index;
    });
  });

  const totalFiltered = computed(() => filteredScenes.value.length);
  const totalPages = computed(() => Math.max(1, Math.ceil(totalFiltered.value / pageSize.value)));

  const pagedScenes = computed(() => {
    const safePage = Math.min(Math.max(1, listPage.value), totalPages.value);
    const start = (safePage - 1) * pageSize.value;
    return filteredScenes.value.slice(start, start + pageSize.value);
  });


  const canGenerateImages = computed(() => scenes.value.length > 0 && scenes.value.every((s) => s.status !== 'pending'));

  const sceneStats = computed(() => ({
    total: scenes.value.length,
    approved: scenes.value.filter((s) => s.status === 'approved').length,
    ready: scenes.value.filter((s) => s.status === 'ready').length,
    error: scenes.value.filter((s) => s.status === 'error').length,
  }));

  function rebuildIndexes() {
    scenes.value.forEach((scene, idx) => {
      scene.index = idx + 1;
      scene.title = `Сцена ${idx + 1}`;
      scene.text = storySentences.slice(scene.startIdx, scene.endIdx + 1).join(' ');
    });
  }

  function segmentStory(targetScenes = 12) {
    scenes.value = [];
    illustrations.value = {};
    let cursor = 0;

    for (let i = 0; i < targetScenes; i += 1) {
      const remaining = storySentences.length - cursor;
      const remainingScenes = targetScenes - i;
      const chunkSize = Math.max(3, Math.round(remaining / remainingScenes));
      const startIdx = cursor;
      const endIdx = Math.min(storySentences.length - 1, cursor + chunkSize - 1);
      cursor = endIdx + 1;

      scenes.value.push({
        id: `scene-${i + 1}`,
        index: i + 1,
        title: `Сцена ${i + 1}`,
        text: storySentences.slice(startIdx, endIdx + 1).join(' '),
        startIdx,
        endIdx,
        status: 'pending',
      });
    }

    listPage.value = 1;
  }

  function setListPage(page: number) {
    listPage.value = Math.min(Math.max(1, page), totalPages.value);
  }

  function approve(sceneId: string, approved: boolean) {
    const scene = scenes.value.find((item) => item.id === sceneId);
    if (!scene) return;
    scene.status = approved ? 'approved' : 'pending';
  }

  function approvePaged(approved: boolean) {
    pagedScenes.value.forEach((scene) => {
      if (scene.status === 'pending' || scene.status === 'approved') {
        scene.status = approved ? 'approved' : 'pending';
      }
    });
  }


  function setSceneRange(sceneId: string, newStart: number, newEnd: number) {
    const idx = scenes.value.findIndex((s) => s.id === sceneId);
    if (idx === -1) return;

    const scene = scenes.value[idx];
    const prev = scenes.value[idx - 1];
    const next = scenes.value[idx + 1];

    const minStart = prev ? prev.startIdx + 1 : 0;
    const maxEnd = next ? next.endIdx - 1 : storySentences.length - 1;

    const safeStart = Math.max(minStart, Math.min(newStart, maxEnd - 1));
    const safeEnd = Math.max(safeStart + 1, Math.min(newEnd, maxEnd));

    scene.startIdx = safeStart;
    scene.endIdx = safeEnd;

    if (prev) prev.endIdx = safeStart - 1;
    if (next) next.startIdx = safeEnd + 1;

    rebuildIndexes();
  }

  function updateBoundaries(sceneId: string, direction: 'start-' | 'start+' | 'end-' | 'end+') {
    const idx = scenes.value.findIndex((s) => s.id === sceneId);
    if (idx === -1) return;
    const scene = scenes.value[idx];
    const prev = scenes.value[idx - 1];
    const next = scenes.value[idx + 1];

    if (direction === 'start-' && prev && scene.startIdx > prev.startIdx + 1) {
      scene.startIdx -= 1;
      prev.endIdx -= 1;
    }
    if (direction === 'start+' && scene.startIdx < scene.endIdx - 1) {
      scene.startIdx += 1;
      if (prev) prev.endIdx += 1;
    }
    if (direction === 'end-' && scene.endIdx > scene.startIdx + 1) {
      scene.endIdx -= 1;
      if (next) next.startIdx -= 1;
    }
    if (direction === 'end+' && next && scene.endIdx < next.endIdx - 1) {
      scene.endIdx += 1;
      next.startIdx += 1;
    }

    rebuildIndexes();
  }

  function splitScene(sceneId: string, splitAtGlobalSentenceIdx: number) {
    const idx = scenes.value.findIndex((scene) => scene.id === sceneId);
    if (idx === -1) return;
    const scene = scenes.value[idx];
    if (splitAtGlobalSentenceIdx <= scene.startIdx || splitAtGlobalSentenceIdx > scene.endIdx) return;

    const left: Scene = { ...scene, endIdx: splitAtGlobalSentenceIdx - 1 };
    const right: Scene = {
      ...scene,
      id: `scene-${Math.random().toString(36).slice(2, 9)}`,
      startIdx: splitAtGlobalSentenceIdx,
      status: 'pending',
    };

    scenes.value.splice(idx, 1, left, right);
    rebuildIndexes();
  }

  function mergeWithNeighbor(sceneId: string, direction: 'prev' | 'next') {
    const idx = scenes.value.findIndex((scene) => scene.id === sceneId);
    if (idx === -1) return;
    const source = scenes.value[idx];
    const otherIdx = direction === 'prev' ? idx - 1 : idx + 1;
    if (otherIdx < 0 || otherIdx >= scenes.value.length) return;
    const other = scenes.value[otherIdx];

    const merged: Scene = {
      ...source,
      id: `scene-${Math.random().toString(36).slice(2, 9)}`,
      startIdx: Math.min(source.startIdx, other.startIdx),
      endIdx: Math.max(source.endIdx, other.endIdx),
      status: 'pending',
    };

    const min = Math.min(idx, otherIdx);
    scenes.value.splice(min, 2, merged);
    rebuildIndexes();
  }

  async function generateSingle(sceneId: string) {
    const scene = scenes.value.find((item) => item.id === sceneId);
    if (!scene) return;
    scene.status = 'generating';

    await delay(1200 + Math.random() * 2400);

    if (scene.index % 7 === 0) {
      scene.status = 'error';
      return;
    }

    scene.status = 'ready';
    illustrations.value[scene.id] = {
      id: `illustration-${scene.id}`,
      sceneId: scene.id,
      imageUrl: createPlaceholder(scene),
      createdAt: new Date().toISOString(),
      promptPreview: `cinematic digital painting, scene ${scene.index}, dramatic lighting, high detail`,
    };
  }

  async function generateApprovedWithConcurrency(maxParallel = 3) {
    if (!canGenerateImages.value) return;
    const queue = scenes.value.filter((s) => s.status === 'approved' || s.status === 'error');
    if (!queue.length) return;
    isGeneratingAll.value = true;

    const workers = Array.from({ length: Math.min(maxParallel, queue.length) }, async (_, workerIndex) => {
      for (let i = workerIndex; i < queue.length; i += maxParallel) {
        await generateSingle(queue[i].id);
      }
    });

    await Promise.all(workers);
    isGeneratingAll.value = false;
  }

  return {
    scenes,
    illustrations,
    search,
    statusFilter,
    sortBy,
    isGeneratingAll,
    listPage,
    pageSize,
    compactCards,
    filteredScenes,
    pagedScenes,
    totalFiltered,
    totalPages,
    sceneStats,
    canGenerateImages,
    segmentStory,
    setListPage,
    approve,
    approvePaged,
    setSceneRange,
    updateBoundaries,
    splitScene,
    mergeWithNeighbor,
    generateSingle,
    generateApprovedWithConcurrency,
  };
});
