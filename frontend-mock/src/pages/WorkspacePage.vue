<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Topbar from '@/components/Topbar.vue';
import SceneList from '@/components/SceneList.vue';
import SceneEditor from '@/components/SceneEditor.vue';
import IllustrationPanel from '@/components/IllustrationPanel.vue';
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

function resetSegmentation() {
  scenes.segmentStory(14);
  ui.selectedSceneId = scenes.scenes[0]?.id ?? null;
}

async function generateAll() {
  await scenes.generateApprovedWithConcurrency(3);
}

function onKeys(event: KeyboardEvent) {
  if (!selectedScene.value) return;
  const currentIndex = scenes.scenes.findIndex((s) => s.id === selectedScene.value?.id);
  if (event.key.toLowerCase() === 'a') scenes.approve(selectedScene.value.id, selectedScene.value.status !== 'approved');
  if (event.key.toLowerCase() === 'g') void generateAll();
  if (event.key === 'ArrowRight') ui.selectedSceneId = scenes.scenes[Math.min(scenes.scenes.length - 1, currentIndex + 1)]?.id ?? ui.selectedSceneId;
  if (event.key === 'ArrowLeft') ui.selectedSceneId = scenes.scenes[Math.max(0, currentIndex - 1)]?.id ?? ui.selectedSceneId;
}
</script>

<template>
  <div class="min-h-screen bg-transparent">
    <Topbar
      :document-name="docs.activeDocument?.name ?? 'Unknown document'"
      :stage="stepStage"
      @regenerate-segmentation="resetSegmentation"
      @open-settings="router.push('/upload')"
      @open-help="ui.showHelpModal = true"
      @toggle-drawer="ui.leftDrawerOpen = !ui.leftDrawerOpen"
    />

    <div class="mx-auto mt-3 flex w-full max-w-[1680px] items-center justify-between px-3">
      <div class="rounded-xl border-2 border-slate-900 bg-white p-1 text-sm font-semibold">
        <button class="rounded-lg px-3 py-1" :class="workspaceMode === 'editor' ? 'bg-slate-900 text-white' : ''" @click="workspaceMode = 'editor'">Editor mode</button>
        <button class="rounded-lg px-3 py-1" :class="workspaceMode === 'reader' ? 'bg-slate-900 text-white' : ''" @click="workspaceMode = 'reader'">Storybook mode</button>
      </div>
      <p class="text-xs text-slate-600">Reader mode — цельный просмотр как книга, Editor mode — точная правка.</p>
    </div>

    <main class="mx-auto grid max-w-[1680px] grid-cols-1 gap-3 p-3 lg:grid-cols-[360px_1fr]">
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
          @approve="(id, approved) => scenes.approve(id, approved)"
          @regenerate="scenes.generateSingle($event)"
          @update-search="scenes.search = $event; scenes.setListPage(1)"
          @update-status-filter="scenes.statusFilter = $event; scenes.setListPage(1)"
          @update-sort-by="scenes.sortBy = $event"
          @update-page="scenes.setListPage($event)"
          @update-page-size="scenes.pageSize = $event; scenes.setListPage(1)"
          @toggle-compact="scenes.compactCards = $event"
          @approve-page="scenes.approvePaged($event)"
        />
      </div>

      <section class="space-y-3" :class="workspaceMode === 'reader' ? 'lg:col-span-2' : ''">
        <OnboardingBanner v-if="ui.showOnboardingBanner" @close="ui.dismissOnboarding()" />

        <StorybookReader
          v-if="workspaceMode === 'reader'"
          :scenes="scenes.scenes"
          :illustrations="scenes.illustrations"
        />

        <div v-if="workspaceMode === 'editor'" class="comic-card bg-white p-4">
          <div class="grid gap-2 md:grid-cols-4">
            <div class="rounded-lg border-2 border-slate-900 bg-slate-50 p-2 text-xs"><b>{{ scenes.sceneStats.total }}</b><br />Total scenes</div>
            <div class="rounded-lg border-2 border-slate-900 bg-emerald-50 p-2 text-xs"><b>{{ scenes.sceneStats.approved }}</b><br />Approved</div>
            <div class="rounded-lg border-2 border-slate-900 bg-blue-50 p-2 text-xs"><b>{{ scenes.sceneStats.ready }}</b><br />Ready panels</div>
            <div class="rounded-lg border-2 border-slate-900 bg-red-50 p-2 text-xs"><b>{{ scenes.sceneStats.error }}</b><br />Errors</div>
          </div>
          <div class="mt-3 flex flex-wrap items-center gap-3">
            <button class="kaboom-btn disabled:opacity-60" :disabled="scenes.isGeneratingAll" @click="generateAll">
              {{ scenes.isGeneratingAll ? 'Генерация…' : 'Сгенерировать иллюстрации' }}
            </button>
            <p class="text-xs text-slate-600">Для 100+ страниц: используйте page-size, compact list и batch approve текущей страницы.</p>
          </div>
          <p class="mt-2 text-xs text-slate-500">Каждая 7-я сцена падает в error для демонстрации retry.</p>
        </div>

        <div v-if="workspaceMode === 'editor' && storyboardReady.length" class="comic-card bg-white p-3">
          <p class="comic-title mb-2 text-sm font-black">Storyboard strip (preview результата)</p>
          <div class="flex gap-2 overflow-x-auto pb-1">
            <button
              v-for="item in storyboardReady"
              :key="item.scene.id"
              class="min-w-40 rounded-lg border-2 border-slate-900 bg-white p-1 text-left"
              @click="ui.selectedSceneId = item.scene.id"
            >
              <img :src="item.illustration?.imageUrl" alt="panel" class="h-20 w-full rounded border border-slate-900 object-cover" />
              <p class="mt-1 text-[11px] font-semibold">#{{ item.scene.index }} {{ item.scene.title }}</p>
            </button>
          </div>
        </div>

        <div v-if="workspaceMode === 'editor' && selectedScene" class="grid gap-3 xl:grid-cols-[1.2fr_0.8fr]">
          <SceneEditor
            :scene="selectedScene"
            @approve="(id, approved) => scenes.approve(id, approved)"
            @boundary-shift="(id, direction) => scenes.updateBoundaries(id, direction)"
            @split="(id, splitAt) => scenes.splitScene(id, splitAt)"
            @merge="(id, direction) => scenes.mergeWithNeighbor(id, direction)"
          />
          <IllustrationPanel
            :scene="selectedScene"
            :illustration="scenes.illustrations[selectedScene.id]"
            @regenerate="scenes.generateSingle($event)"
            @retry="scenes.generateSingle($event)"
            @show-prompt="ui.promptSceneId = $event; ui.showPromptModal = true"
          />
        </div>
      </section>
    </main>

    <PromptModal :open="ui.showPromptModal" :prompt="promptText" @close="ui.showPromptModal = false" />
    <ShortcutsModal :open="ui.showHelpModal" @close="ui.showHelpModal = false" />
  </div>
</template>
