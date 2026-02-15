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

const workspaceMode = ref<'editor' | 'reader'>('reader');

onMounted(() => {
  const id = String(route.params.id);
  docs.setActiveDocument(id);
  if (!scenes.scenes.length) scenes.segmentStory(14);
  if (!ui.selectedSceneId && scenes.scenes.length) ui.selectedSceneId = scenes.scenes[0].id;
  window.addEventListener('keydown', onKeys);
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKeys);
});

const selectedScene = computed(() => scenes.scenes.find((scene) => scene.id === ui.selectedSceneId) ?? null);
const selectedSceneIndex = computed(() => scenes.scenes.findIndex((scene) => scene.id === ui.selectedSceneId));
const boundaryLimits = computed(() => {
  const idx = selectedSceneIndex.value;
  const prev = idx > 0 ? scenes.scenes[idx - 1] : null;
  const next = idx >= 0 && idx < scenes.scenes.length - 1 ? scenes.scenes[idx + 1] : null;
  return {
    minStart: prev ? prev.startIdx + 1 : 0,
    maxEnd: next ? next.endIdx - 1 : (scenes.scenes.length ? scenes.scenes[scenes.scenes.length - 1].endIdx : 0),
  };
});
const hasPrevScene = computed(() => selectedSceneIndex.value > 0);
const hasNextScene = computed(() => selectedSceneIndex.value >= 0 && selectedSceneIndex.value < scenes.scenes.length - 1);
const stepStage = computed(() => {
  if (scenes.isGeneratingAll) return 'generate' as const;
  return 'review' as const;
});

const promptText = computed(() => {
  if (!ui.promptSceneId) return '';
  return scenes.illustrations[ui.promptSceneId]?.promptPreview ?? 'Prompt will appear after generation.';
});

const storyboardReady = computed(() =>
  scenes.scenes
    .filter((scene) => scene.status === 'ready')
    .slice(0, 10)
    .map((scene) => ({ scene, illustration: scenes.illustrations[scene.id] }))
    .filter((item) => item.illustration),
);

const showApproveConfirm = ref(false);
const skipApproveConfirm = ref(localStorage.getItem('skipApproveConfirm') === '1');

function requestApprove() {
  if (skipApproveConfirm.value) {
    scenes.approveSegmentation();
    return;
  }
  showApproveConfirm.value = true;
}

function confirmApprove() {
  scenes.approveSegmentation();
  showApproveConfirm.value = false;
  if (skipApproveConfirm.value) localStorage.setItem('skipApproveConfirm', '1');
}

function cancelApprove() {
  showApproveConfirm.value = false;
}

async function generateAll() {
  await scenes.generateApprovedWithConcurrency(3);
}

function onKeys(event: KeyboardEvent) {
  if (!selectedScene.value) return;
  const currentIndex = scenes.scenes.findIndex((s) => s.id === selectedScene.value?.id);
  if (event.key.toLowerCase() === 'g') void generateAll();
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
      <div v-if="workspaceMode === 'editor'" :class="['lg:block', ui.leftDrawerOpen ? 'block' : 'hidden']">
        <SceneList
          :scenes="scenes.pagedScenes"
          :illustrations="scenes.illustrations"
          :selected-scene-id="ui.selectedSceneId"
          :search="scenes.search"
          :status-filter="scenes.statusFilter"
          :sort-by="scenes.sortBy"
          :list-page="scenes.listPage"
          :total-pages="scenes.totalPages"
          :total-filtered="scenes.totalFiltered"
          :page-size="scenes.pageSize"
          :compact-cards="scenes.compactCards"
          @choose="ui.selectedSceneId = $event; ui.leftDrawerOpen = false"
          @update-search="scenes.search = $event; scenes.setListPage(1)"
          @update-status-filter="scenes.statusFilter = $event; scenes.setListPage(1)"
          @update-sort-by="scenes.sortBy = $event"
          @update-page="scenes.setListPage($event)"
          @update-page-size="scenes.pageSize = $event; scenes.setListPage(1)"
          @toggle-compact="scenes.compactCards = $event"
        />
      </div>

      <section class="space-y-3" :class="workspaceMode === 'reader' ? 'lg:col-span-2' : ''">
        <OnboardingBanner v-if="ui.showOnboardingBanner" @close="ui.dismissOnboarding()" />

        <StorybookReader v-if="workspaceMode === 'reader'" :scenes="scenes.scenes" :illustrations="scenes.illustrations" />

        <div v-if="workspaceMode === 'editor'" class="comic-card bg-white p-5">
          <div class="grid gap-2 md:grid-cols-4">
            <div class="rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs"><b>{{ scenes.sceneStats.total }}</b><br />Всего сцен</div>
            <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-2 text-xs"><b>{{ scenes.sceneStats.approved }}</b><br />Одобрено</div>
            <div class="rounded-lg border border-blue-200 bg-blue-50 p-2 text-xs"><b>{{ scenes.sceneStats.ready }}</b><br />Готово</div>
            <div class="rounded-lg border border-rose-200 bg-rose-50 p-2 text-xs"><b>{{ scenes.sceneStats.error }}</b><br />Ошибки</div>
          </div>
          <div class="mt-3 flex flex-wrap items-center gap-3">
            <button class="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold" :class="scenes.segmentationApproved ? 'bg-emerald-100 text-emerald-800' : ''" @click="requestApprove">
              {{ scenes.segmentationApproved ? 'Нарезка подтверждена' : 'Подтвердить текущую нарезку сцен' }}
            </button>
            <button class="kaboom-btn disabled:opacity-60" :disabled="scenes.isGeneratingAll || !scenes.canGenerateImages" @click="generateAll">
              {{ scenes.isGeneratingAll ? 'Генерация…' : 'Сгенерировать иллюстрации' }}
            </button>
          </div>
          <p v-if="!scenes.canGenerateImages" class="mt-2 text-xs font-semibold text-rose-700">Сначала одобрите границы всех сцен (не должно остаться pending), затем генерация станет доступна.</p>
        </div>

        <div v-if="workspaceMode === 'editor' && storyboardReady.length" class="comic-card bg-white p-3">
          <p class="comic-title mb-2 text-sm font-semibold">Storyboard strip (preview результата)</p>
          <div class="flex gap-2 overflow-x-auto pb-1">
            <button
              v-for="item in storyboardReady"
              :key="item.scene.id"
              class="min-w-40 rounded-lg border border-slate-200 bg-white p-1 text-left"
              @click="ui.selectedSceneId = item.scene.id"
            >
              <img :src="item.illustration?.imageUrl" alt="panel" class="h-20 w-full rounded border border-slate-200 object-cover" />
              <p class="mt-1 text-[11px] font-semibold">#{{ item.scene.index }} {{ item.scene.title }}</p>
            </button>
          </div>
        </div>

        <div v-if="workspaceMode === 'editor' && selectedScene">
          <SceneEditor
            :scene="selectedScene"
            :illustration="scenes.illustrations[selectedScene.id]"
            :min-start="boundaryLimits.minStart"
            :max-end="boundaryLimits.maxEnd"
            :has-prev="hasPrevScene"
            :has-next="hasNextScene"
            @set-range="(id, startIdx, endIdx) => scenes.setSceneRange(id, startIdx, endIdx)"
            @split="(id, splitAt) => scenes.splitScene(id, splitAt)"
            @merge="(id, direction) => scenes.mergeWithNeighbor(id, direction)"
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
          После подтверждения границы сцен нельзя будет изменить, а генерация иллюстраций запустится автоматически. Убедитесь, что сцены расставлены верно.
        </p>
        <label class="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <input v-model="skipApproveConfirm" type="checkbox" class="rounded border-slate-300" />
          Не показывать снова
        </label>
        <div class="mt-4 flex justify-end gap-2">
          <button class="rounded border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold" @click="cancelApprove">Отмена</button>
          <button class="kaboom-btn px-4 py-2 text-sm" @click="confirmApprove">Подтвердить</button>
        </div>
      </div>
    </div>
  </div>
</template>
