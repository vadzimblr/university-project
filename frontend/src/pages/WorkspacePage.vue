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

async function confirmApprove() {
  try {
    await scenes.saveAll();
    await scenes.approveCurrentJob();
    showApproveConfirm.value = false;
    if (skipApproveConfirm.value) localStorage.setItem('skipApproveConfirm', '1');
  } catch (e) {
    console.error(e);
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

    <main class="mx-auto grid max-w-[1780px] grid-cols-1 gap-3 p-3 lg:grid-cols-[330px_1fr]">
      <section class="comic-card bg-white p-4 lg:col-span-2">
        <div class="flex flex-wrap items-center gap-3">
          <button class="kaboom-btn" :disabled="!Object.keys(scenes.dirtyTexts).length" @click="scenes.saveAll()">Сохранить изменения</button>
          <button class="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold" @click="showApproveConfirm = true">
            Подтвердить нарезку
          </button>
          <p class="text-xs text-slate-500">После подтверждения границы сцен нельзя будет изменить.</p>
        </div>
      </section>
      <div :class="['lg:block', ui.leftDrawerOpen ? 'block' : 'hidden']">
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
          @choose="ui.selectedSceneId = $event; ui.leftDrawerOpen = false"
          @update-search="scenes.search = $event; scenes.setListPage(1)"
          @update-status-filter="() => {}"
          @update-sort-by="() => {}"
          @update-page="scenes.setListPage($event)"
          @update-page-size="scenes.pageSize = $event; scenes.setListPage(1)"
        />
      </div>

      <section class="space-y-3">
        <OnboardingBanner v-if="ui.showOnboardingBanner" @close="ui.dismissOnboarding()" />

        <div v-if="selectedScene">
          <SceneEditor
            :scene="selectedScene"
            :sentences="scenes.sentencesMap[selectedScene.sceneNumber]"
            :has-prev="hasPrevScene"
            :has-next="hasNextScene"
            @request-sentences="scenes.loadSentences(selectedScene.sceneNumber)"
            @update-text="(text) => scenes.updateSceneText(selectedScene.sceneNumber, text)"
            @move-sentences="(mode, count, dir) => scenes.moveSentences(selectedScene.sceneNumber, mode, count, dir)"
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
