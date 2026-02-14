<script setup lang="ts">
import AppStepper from './AppStepper.vue';

defineProps<{
  documentName: string;
  stage: 'upload' | 'segmenting' | 'review' | 'generate';
}>();

const emit = defineEmits<{
  regenerateSegmentation: [];
  openSettings: [];
  openHelp: [];
  toggleDrawer: [];
}>();
</script>

<template>
  <header class="sticky top-0 z-20 border-b-4 border-slate-900 bg-amber-100 px-4 py-3 lg:px-6">
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="rounded-lg border-2 border-slate-900 bg-white px-3 py-1 text-sm lg:hidden" @click="emit('toggleDrawer')">☰</button>
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-slate-600">Storybook Document</p>
          <h1 class="comic-title text-base font-black md:text-lg">{{ documentName }}</h1>
        </div>
      </div>

      <AppStepper :stage="stage" />

      <div class="hidden items-center gap-2 md:flex">
        <button class="kaboom-btn" @click="emit('regenerateSegmentation')">Пересегментировать</button>
        <button class="rounded-lg border-2 border-slate-900 bg-white px-3 py-1.5 text-sm" @click="emit('openHelp')">Shortcuts</button>
        <button class="rounded-lg border-2 border-slate-900 bg-slate-900 px-3 py-1.5 text-sm text-white" @click="emit('openSettings')">Настройки</button>
      </div>
    </div>
  </header>
</template>
