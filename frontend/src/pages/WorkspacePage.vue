<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Topbar from '@/components/Topbar.vue';
import SceneList from '@/components/SceneList.vue';
import SceneEditor from '@/components/SceneEditor.vue';
import PromptModal from '@/components/PromptModal.vue';
import ShortcutsModal from '@/components/ShortcutsModal.vue';
import OnboardingBanner from '@/components/OnboardingBanner.vue';
import StorybookReader from '@/components/StorybookReader.vue';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useScenesStore } from '@/stores/scenesStore';
import { useUiStore } from '@/stores/uiStore';

const route = useRoute();
const router = useRouter();
const docs = useDocumentsStore();
const scenes = useScenesStore();
const ui = useUiStore();

const workspaceMode = ref<'editor' | 'reader'>('editor');
const saving = ref(false);

async function initData() {
  const id = String(route.params.id);
  if (!docs.documents.length) {
    await docs.loadDocuments().catch(() => {});
  }
  docs.setActiveDocument(id);
  const doc = docs.activeDocument;
  const jobId = doc?.processingJobs?.[0]?.id;
  if (jobId) {
    await scenes.loadScenes(jobId);
    ui.selectedSceneId = scenes.scenes[0]?.id ?? null;
  }
}

onMounted(() => {
  initData();
  window.addEventListener('keydown', onKeys);
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKeys);
});

const selectedScene = computed(() => scenes.scenes.find((scene) => scene.id === ui.selectedSceneId) ?? null);
const selectedSceneIndex = computed(() => scenes.scenes.findIndex((scene) => scene.id === ui.selectedSceneId));
const hasPrevScene = computed(() => selectedSceneIndex.value > 0);
const hasNextScene = computed(() => selectedSceneIndex.value >= 0 && selectedSceneIndex.value < scenes.scenes.length - 1);
const stepStage = computed(() => {
  if (scenes.isGeneratingAll) return 'generate' as const;
  return 'review' as const;
});

const promptText = computed(() => '');
const showApproveConfirm = ref(false);
const skipApproveConfirm = ref(localStorage.getItem('skipApproveConfirm') === '1');
const hasPendingChanges = computed(() => Object.keys(scenes.dirtyTexts).length > 0 || scenes.pendingMergeCount > 0);
const mergeThreshold = ref(3);
const isApproved = computed(() => {
  const raw = docs.activeDocument?.processingJobs?.[0]?.status ?? '';
  const normalized = String(raw).toLowerCase().replace('processingstatus.', '');
  return normalized === 'approved';
});

function applyMergeShort() {
  scenes.queueMergeShortScenes(mergeThreshold.value);
}

async function confirmApprove() {
  if (saving.value) return;
  if (isApproved.value) return;
  saving.value = true;
  try {
    await scenes.approveCurrentJob();
    showApproveConfirm.value = false;
    if (skipApproveConfirm.value) localStorage.setItem('skipApproveConfirm', '1');
  } catch (e) {
    console.error(e);
  } finally {
    saving.value = false;
  }
}

async function handleSave() {
  if (saving.value) return;
  saving.value = true;
  const prevSceneNumber = selectedScene.value?.sceneNumber ?? null;
  try {
    await scenes.saveAll();
    if (!scenes.scenes.length) {
      ui.selectedSceneId = null;
      return;
    }
    if (prevSceneNumber !== null) {
      const match =
        scenes.scenes.find((s) => s.sceneNumber === prevSceneNumber) ??
        [...scenes.scenes].filter((s) => s.sceneNumber < prevSceneNumber).slice(-1)[0] ??
        scenes.scenes[0];
      ui.selectedSceneId = match?.id ?? scenes.scenes[0]?.id ?? null;
    } else {
      ui.selectedSceneId = scenes.scenes[0]?.id ?? null;
    }
  } catch (e) {
    console.error(e);
  } finally {
    saving.value = false;
  }
}

function onKeys(event: KeyboardEvent) {
  if (!selectedScene.value) return;
  const currentIndex = scenes.scenes.findIndex((s) => s.id === selectedScene.value?.id);
  if (event.key === 'ArrowRight') ui.selectedSceneId = scenes.scenes[Math.min(scenes.scenes.length - 1, currentIndex + 1)]?.id ?? ui.selectedSceneId;
  if (event.key === 'ArrowLeft') ui.selectedSceneId = scenes.scenes[Math.max(0, currentIndex - 1)]?.id ?? ui.selectedSceneId;
}
</script>

<template>
  <div class="min-h-screen bg-transparent page-fade">
    <Topbar
      :document-name="docs.activeDocument?.name ?? docs.activeDocument?.filename ?? 'Документ'"
      :stage="stepStage"
      @open-settings="router.push('/upload')"
      @open-help="ui.showHelpModal = true"
      @toggle-drawer="ui.leftDrawerOpen = !ui.leftDrawerOpen"
    />

    <div class="mx-auto mt-3 flex w-full max-w-[1680px] flex-wrap items-center justify-between gap-2 px-3">
      <div class="rounded-full border border-slate-200 bg-white/90 p-1 text-sm font-semibold shadow-sm">
        <button class="rounded-full px-4 py-1.5" :class="workspaceMode === 'editor' ? 'bg-slate-900 text-white' : 'text-slate-600'" @click="workspaceMode = 'editor'">Режим редактора</button>
        <button class="rounded-full px-4 py-1.5" :class="workspaceMode === 'reader' ? 'bg-slate-900 text-white' : 'text-slate-600'" @click="workspaceMode = 'reader'">Режим чтения</button>
      </div>
      <p class="text-xs text-slate-600">Режим чтения — целостный просмотр, редактор — для правки.</p>
    </div>

    <main class="mx-auto grid max-w-[1780px] grid-cols-1 gap-3 p-3 lg:grid-cols-[330px_1fr]">
      <section v-if="workspaceMode === 'editor'" class="comic-card bg-white p-4 lg:col-span-2">
        <div class="flex flex-wrap items-center gap-3">
          <button class="kaboom-btn inline-flex h-10 items-center justify-center px-5 text-sm leading-none" :disabled="!hasPendingChanges || saving || isApproved" @click="handleSave">
            Сохранить изменения
          </button>
          <button
            class="inline-flex h-10 items-center justify-center rounded-xl border border-amber-200 bg-amber-50 px-5 text-sm font-semibold leading-none text-amber-900 transition hover:bg-amber-100"
            :disabled="saving || isApproved"
            @click="showApproveConfirm = true"
          >
            Подтвердить нарезку
          </button>
          <p class="text-xs text-slate-500">После подтверждения границы сцен нельзя будет изменить.</p>
        </div>

        <div class="mt-3 flex flex-wrap items-center gap-3 text-sm">
          <div class="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
            <span class="text-xs font-semibold text-slate-700">Автослияние</span>
            <span class="text-xs text-slate-500">Слить сцены с предложений меньше</span>
            <input
              v-model.number="mergeThreshold"
              type="number"
              min="1"
              class="h-8 w-20 rounded-lg border border-slate-200 bg-white px-2 text-sm"
            />
            <button
              class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-semibold hover:bg-slate-100"
              :disabled="isApproved"
              @click="applyMergeShort"
            >
              Применить
            </button>
            <button
              class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-100"
              :disabled="isApproved || !scenes.pendingMergeSceneNumbersAuto || !Object.keys(scenes.pendingMergeSceneNumbersAuto).length"
              @click="scenes.clearAutoMerges()"
            >
              Сбросить
            </button>
          </div>
          <p class="text-xs text-slate-500">Слияние ставится в очередь и выполнится после сохранения.</p>
        </div>
      </section>
      <div v-if="workspaceMode === 'editor'" :class="['lg:block', ui.leftDrawerOpen ? 'block' : 'hidden']">
        <SceneList
          :scenes="scenes.pagedScenes"
          :illustrations="scenes.illustrations"
          :selected-scene-id="ui.selectedSceneId"
          :search="scenes.search"
          :status-filter="'all'"
          :sort-by="'index'"
          :list-page="scenes.listPage"
          :total-pages="scenes.totalPages"
          :total-filtered="scenes.totalFiltered"
          :page-size="scenes.pageSize"
          :pending-merge-scenes="scenes.pendingMergeSceneNumbers"
          :pending-merge-scenes-auto="scenes.pendingMergeSceneNumbersAuto"
          @choose="ui.selectedSceneId = $event; ui.leftDrawerOpen = false"
          @update-search="scenes.search = $event; scenes.setListPage(1)"
          @update-status-filter="() => {}"
          @update-sort-by="() => {}"
          @update-page="scenes.setListPage($event)"
          @update-page-size="scenes.pageSize = $event; scenes.setListPage(1)"
        />
      </div>

      <section class="space-y-3" :class="workspaceMode === 'reader' ? 'lg:col-span-2' : ''">
        <OnboardingBanner v-if="ui.showOnboardingBanner" @close="ui.dismissOnboarding()" />

        <StorybookReader v-if="workspaceMode === 'reader'" :scenes="scenes.scenes" :illustrations="scenes.illustrations" />

        <div v-if="workspaceMode === 'editor' && selectedScene">
          <SceneEditor
            :scene="selectedScene"
            :sentences="scenes.sentencesMap[selectedScene.sceneNumber]"
            :has-prev="hasPrevScene"
            :has-next="hasNextScene"
            :merge-prev-queued="!!scenes.pendingManualMergeLinks[selectedScene.sceneNumber - 1]"
            :merge-next-queued="!!scenes.pendingManualMergeLinks[selectedScene.sceneNumber]"
            :read-only="isApproved"
            @request-sentences="scenes.loadSentences(selectedScene.sceneNumber)"
            @update-text="(text) => scenes.updateSceneText(selectedScene.sceneNumber, text)"
            @move-sentences="(mode, count, dir) => scenes.moveSentences(selectedScene.sceneNumber, mode, count, dir)"
            @merge-scene="(dir) => scenes.queueMerge(selectedScene.sceneNumber, dir)"
          />
        </div>
      </section>
    </main>

    <PromptModal :open="ui.showPromptModal" :prompt="promptText" @close="ui.showPromptModal = false" />
    <ShortcutsModal :open="ui.showHelpModal" @close="ui.showHelpModal = false" />

    <div
      v-if="showApproveConfirm"
      class="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/50 px-4"
      role="dialog"
      aria-modal="true"
    >
      <div class="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
        <h3 class="comic-title text-lg font-semibold">Подтвердить нарезку?</h3>
        <p class="mt-2 text-sm text-slate-700">
          После подтверждения границы сцен нельзя будет изменить, а генерация иллюстраций может стартовать автоматически. Убедитесь, что всё верно.
        </p>
        <label class="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <input v-model="skipApproveConfirm" type="checkbox" class="rounded border-slate-300" />
          Не показывать снова
        </label>
        <div class="mt-4 flex justify-end gap-2">
          <button class="rounded border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold" @click="showApproveConfirm = false">Отмена</button>
          <button class="kaboom-btn px-4 py-2 text-sm" @click="confirmApprove">Подтвердить</button>
        </div>
      </div>
    </div>
  </div>
</template>
