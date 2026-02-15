import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import type { Scene, Illustration } from '@/types/models';
import { fetchScenes, fetchSceneSentences, patchScenes, approveJob, mergeScenes } from '@/api/sceneSplitter';

export const useScenesStore = defineStore('scenes', () => {
  const jobId = ref<string | null>(null);
  const scenes = ref<Scene[]>([]);
  const illustrations = ref<Record<string, Illustration>>({});
  const sentencesMap = ref<Record<number, string[]>>({});
  const dirtyTexts = ref<Record<number, string>>({});
  const pendingMergeLinks = ref<Record<number, true>>({});
  const pendingMergeLinksAuto = ref<Record<number, true>>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  const search = ref('');
  const listPage = ref(1);
  const pageSize = ref(8);

  const filteredScenes = computed(() => {
    const q = search.value.trim().toLowerCase();
    const prepared = scenes.value.filter((s) => s.text.toLowerCase().includes(q) || (s.title ?? '').toLowerCase().includes(q));
    return prepared.sort((a, b) => a.sceneNumber - b.sceneNumber);
  });

  const totalFiltered = computed(() => filteredScenes.value.length);
  const totalPages = computed(() => Math.max(1, Math.ceil(totalFiltered.value / pageSize.value)));
  const pagedScenes = computed(() => {
    const safe = Math.min(Math.max(1, listPage.value), totalPages.value);
    const start = (safe - 1) * pageSize.value;
    return filteredScenes.value.slice(start, start + pageSize.value);
  });

  const sceneStats = computed(() => ({
    total: scenes.value.length,
    approved: 0,
    ready: 0,
    error: 0,
  }));

  const pendingMergeLinksAll = computed(() => ({ ...pendingMergeLinks.value, ...pendingMergeLinksAuto.value }));
  const pendingMergeCount = computed(() => Object.keys(pendingMergeLinksAll.value).length);
  const pendingMergeSceneNumbers = computed(() => mapScenesForLinks(pendingMergeLinks.value));
  const pendingMergeSceneNumbersAuto = computed(() => mapScenesForLinks(pendingMergeLinksAuto.value));
  const pendingManualMergeLinks = computed(() => ({ ...pendingMergeLinks.value }));

  const canGenerateImages = computed(() => false);
  const segmentationApproved = ref(false);
  const isGeneratingAll = ref(false);

  function setListPage(page: number) {
    listPage.value = Math.min(Math.max(1, page), totalPages.value);
  }

  async function loadScenes(targetJobId: string) {
    jobId.value = targetJobId;
    loading.value = true;
    error.value = null;
    try {
      const resp = await fetchScenes(targetJobId);
      scenes.value = resp.scenes.map((s) => ({
        id: `${targetJobId}-${s.scene_number}`,
        sceneNumber: s.scene_number,
        index: s.scene_number,
        title: `Сцена ${s.scene_number}`,
        text: s.scene_text,
        sentenceCount: s.sentence_count,
        status: 'pending',
      }));
      listPage.value = 1;
      sentencesMap.value = {};
      dirtyTexts.value = {};
      pendingMergeLinks.value = {};
      pendingMergeLinksAuto.value = {};
    } catch (e: any) {
      error.value = e?.message ?? 'Не удалось загрузить сцены';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function resetScenes() {
    jobId.value = null;
    scenes.value = [];
    sentencesMap.value = {};
    dirtyTexts.value = {};
    pendingMergeLinks.value = {};
    pendingMergeLinksAuto.value = {};
    listPage.value = 1;
    error.value = null;
  }

  async function loadSentences(sceneNumber: number) {
    if (!jobId.value) return [];
    if (sentencesMap.value[sceneNumber]) return sentencesMap.value[sceneNumber];
    const resp = await fetchSceneSentences(jobId.value, sceneNumber);
    sentencesMap.value[sceneNumber] = resp.sentences.map((s) => s.text);
    return sentencesMap.value[sceneNumber];
  }

  function syncSceneText(sceneNumber: number) {
    const scene = scenes.value.find((s) => s.sceneNumber === sceneNumber);
    if (!scene) return;
    const sentences = sentencesMap.value[sceneNumber] || [];
    const text = sentences.join(' ');
    scene.text = text;
    dirtyTexts.value[sceneNumber] = text;
  }

  function ensureSentenceList(sceneNumber: number) {
    if (!sentencesMap.value[sceneNumber]) {
      const scene = scenes.value.find((s) => s.sceneNumber === sceneNumber);
      if (scene) {
        sentencesMap.value[sceneNumber] = scene.text.split(/(?<=[.!?])\s+/).filter(Boolean);
      } else {
        sentencesMap.value[sceneNumber] = [];
      }
    }
    return sentencesMap.value[sceneNumber];
  }

  function getSceneSentenceCount(sceneNumber: number) {
    if (sentencesMap.value[sceneNumber]) return sentencesMap.value[sceneNumber].length;
    const scene = scenes.value.find((s) => s.sceneNumber === sceneNumber);
    if (!scene) return 0;
    if (scene.sentenceCount != null) return scene.sentenceCount;
    return estimateSentenceCount(scene.text);
  }

  function moveSentences(sceneNumber: number, mode: 'head' | 'tail', count: number, direction: 'prev' | 'next') {
    const targetSceneNumber = direction === 'prev' ? sceneNumber - 1 : sceneNumber + 1;
    const source = ensureSentenceList(sceneNumber);
    const target = ensureSentenceList(targetSceneNumber);
    if (!source.length || count <= 0) return;
    if (mode === 'head' && direction === 'next') return;
    if (mode === 'tail' && direction === 'prev') return;

    let moved: string[] = [];
    if (mode === 'head') {
      moved = source.splice(0, Math.min(count, source.length));
      if (direction === 'prev') {
        target.push(...moved);
      } else {
        target.unshift(...moved);
      }
    } else {
      moved = source.splice(Math.max(0, source.length - count), count);
      if (direction === 'prev') {
        target.push(...moved);
      } else {
        target.unshift(...moved);
      }
    }

    syncSceneText(sceneNumber);
    syncSceneText(targetSceneNumber);
  }

  function queueMerge(sceneNumber: number, direction: 'prev' | 'next') {
    const link = direction === 'prev' ? sceneNumber - 1 : sceneNumber;
    if (link < 1) return;
    if (link >= scenes.value.length) return;
    const pending = { ...pendingMergeLinks.value };
    if (pending[link]) {
      delete pending[link];
    } else {
      pending[link] = true;
    }
    pendingMergeLinks.value = pending;
  }

  function queueMergeShortScenes(threshold: number) {
    if (!Number.isFinite(threshold)) return;
    const limit = Math.max(1, Math.floor(threshold));
    const pending: Record<number, true> = {};
    const total = scenes.value.length;
    for (const scene of scenes.value) {
      const count = getSceneSentenceCount(scene.sceneNumber);
      if (count >= limit) continue;
      if (scene.sceneNumber > 1) {
        pending[scene.sceneNumber - 1] = true;
      } else if (scene.sceneNumber < total) {
        pending[scene.sceneNumber] = true;
      }
    }
    pendingMergeLinksAuto.value = pending;
  }

  function clearAutoMerges() {
    pendingMergeLinksAuto.value = {};
  }

  function updateSceneText(sceneNumber: number, text: string) {
    const scene = scenes.value.find((s) => s.sceneNumber === sceneNumber);
    if (!scene) return;
    scene.text = text;
    dirtyTexts.value[sceneNumber] = text;
  }

  async function saveAll() {
    if (!jobId.value) return;
    const patches = Object.entries(dirtyTexts.value).map(([num, text]) => ({
      scene_number: Number(num),
      scene_text: text,
    }));
    if (patches.length) {
      await patchScenes(jobId.value, patches);
    }

    const mergeGroups = buildMergeGroups(pendingMergeLinksAll.value, scenes.value.length);
    if (mergeGroups.length) {
      const sorted = mergeGroups.sort((a, b) => b[b.length - 1] - a[a.length - 1]);
      for (const group of sorted) {
        await mergeScenes(jobId.value, group);
      }
      await loadScenes(jobId.value);
      pendingMergeLinks.value = {};
      pendingMergeLinksAuto.value = {};
      return;
    }

    if (patches.length) {
      dirtyTexts.value = {};
    }
  }

  async function approveCurrentJob() {
    if (!jobId.value) throw new Error('job_id unknown');
    await saveAll();
    await approveJob(jobId.value);
    segmentationApproved.value = true;
  }

  return {
    jobId,
    scenes,
    illustrations,
    sentencesMap,
    dirtyTexts,
    loading,
    error,
    search,
    listPage,
    pageSize,
    filteredScenes,
    pagedScenes,
    totalFiltered,
    totalPages,
    sceneStats,
    segmentationApproved,
    canGenerateImages,
    isGeneratingAll,
    setListPage,
    loadScenes,
    resetScenes,
    loadSentences,
    updateSceneText,
    moveSentences,
    queueMerge,
    queueMergeShortScenes,
    clearAutoMerges,
    syncSceneText,
    saveAll,
    approveCurrentJob,
    pendingMergeCount,
    pendingMergeSceneNumbers,
    pendingMergeSceneNumbersAuto,
    pendingManualMergeLinks,
  };
});

function mapScenesForLinks(links: Record<number, true>) {
  const map: Record<number, true> = {};
  for (const key of Object.keys(links)) {
    const link = Number(key);
    if (!Number.isFinite(link)) continue;
    map[link] = true;
    map[link + 1] = true;
  }
  return map;
}

function buildMergeGroups(pendingLinks = {} as Record<number, true>, totalScenes = 0) {
  const links = Object.keys(pendingLinks)
    .map(Number)
    .filter((link) => link >= 1 && (totalScenes ? link < totalScenes : true))
    .sort((a, b) => a - b);
  if (!links.length) return [] as number[][];

  const groups: number[][] = [];
  let start = links[0];
  let last = links[0];

  for (let i = 1; i < links.length; i += 1) {
    const link = links[i];
    if (link === last + 1) {
      last = link;
      continue;
    }
    groups.push(range(start, last + 1));
    start = link;
    last = link;
  }
  groups.push(range(start, last + 1));
  return groups;
}

function range(start: number, endInclusive: number) {
  const values: number[] = [];
  for (let i = start; i <= endInclusive; i += 1) values.push(i);
  return values;
}

function estimateSentenceCount(text: string) {
  if (!text) return 0;
  return text.split(/(?<=[.!?])\s+/).filter(Boolean).length;
}
