<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Topbar from '@/components/Topbar.vue';
import SceneList from '@/components/SceneList.vue';
import SceneEditor from '@/components/SceneEditor.vue';
import IllustrationPanel from '@/components/IllustrationPanel.vue';
import PromptModal from '@/components/PromptModal.vue';
import ShortcutsModal from '@/components/ShortcutsModal.vue';
import OnboardingBanner from '@/components/OnboardingBanner.vue';
import { useDocumentsStore } from '@/stores/documentsStore';
import { useScenesStore } from '@/stores/scenesStore';
import { useUiStore } from '@/stores/uiStore';

const route = useRoute();
const router = useRouter();
const docs = useDocumentsStore();
const scenes = useScenesStore();
const ui = useUiStore();

onMounted(() => {
  const id = String(route.params.id);
  docs.setActiveDocument(id);
  if (!scenes.scenes.length) scenes.segmentStory();
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

function resetSegmentation() {
  scenes.segmentStory();
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

    <main class="mx-auto grid max-w-[1600px] grid-cols-1 gap-3 p-3 lg:grid-cols-[360px_1fr]">
      <div :class="['lg:block', ui.leftDrawerOpen ? 'block' : 'hidden']">
        <SceneList
          :scenes="scenes.filteredScenes"
          :illustrations="scenes.illustrations"
          :selected-scene-id="ui.selectedSceneId"
          :search="scenes.search"
          :status-filter="scenes.statusFilter"
          :sort-by="scenes.sortBy"
          @choose="ui.selectedSceneId = $event; ui.leftDrawerOpen = false"
          @approve="(id, approved) => scenes.approve(id, approved)"
          @regenerate="scenes.generateSingle($event)"
          @update-search="scenes.search = $event"
          @update-status-filter="scenes.statusFilter = $event"
          @update-sort-by="scenes.sortBy = $event"
        />
      </div>

      <section class="space-y-3">
        <OnboardingBanner v-if="ui.showOnboardingBanner" @close="ui.dismissOnboarding()" />

        <div class="comic-card bg-white p-4">
          <div class="flex flex-wrap items-center gap-3">
            <button class="kaboom-btn disabled:opacity-60" :disabled="scenes.isGeneratingAll" @click="generateAll">
              {{ scenes.isGeneratingAll ? 'Генерация…' : 'Сгенерировать иллюстрации' }}
            </button>
            <p class="text-xs text-slate-600">Режим storybook: генерируем только approved/error и поддерживаем темп повествования.</p>
          </div>
          <p class="mt-2 text-xs text-slate-500">Каждая 7-я сцена падает в error для демонстрации retry.</p>
        </div>

        <div v-if="selectedScene" class="grid gap-3 xl:grid-cols-[1.2fr_0.8fr]">
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
