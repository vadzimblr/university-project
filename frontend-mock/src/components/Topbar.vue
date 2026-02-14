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
  <header class="sticky top-0 z-20 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur lg:px-6">
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="rounded-lg border border-slate-200 px-3 py-1 text-sm lg:hidden" @click="emit('toggleDrawer')">☰</button>
        <div>
          <p class="text-xs uppercase tracking-wide text-slate-500">Document</p>
          <h1 class="text-base font-semibold md:text-lg">{{ documentName }}</h1>
        </div>
      </div>

      <AppStepper :stage="stage" />

      <div class="hidden items-center gap-2 md:flex">
        <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm" @click="emit('regenerateSegmentation')">Пересегментировать</button>
        <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm" @click="emit('openHelp')">Shortcuts</button>
        <button class="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white" @click="emit('openSettings')">Настройки</button>
      </div>
    </div>
  </header>
</template>
