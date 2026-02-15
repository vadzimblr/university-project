import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', () => {
  const uploadProgress = ref(0);
  const segmentationProgress = ref(0);
  const processingStage = ref<'idle' | 'upload' | 'segmenting' | 'done'>('idle');
  const selectedSceneId = ref<string | null>(null);
  const showPromptModal = ref(false);
  const promptSceneId = ref<string | null>(null);
  const showHelpModal = ref(false);
  const showOnboardingBanner = ref(localStorage.getItem('story-onboarding-dismissed') !== '1');
  const leftDrawerOpen = ref(false);

  function dismissOnboarding() {
    showOnboardingBanner.value = false;
    localStorage.setItem('story-onboarding-dismissed', '1');
  }

  return {
    uploadProgress,
    segmentationProgress,
    processingStage,
    selectedSceneId,
    showPromptModal,
    promptSceneId,
    showHelpModal,
    showOnboardingBanner,
    leftDrawerOpen,
    dismissOnboarding,
  };
});
