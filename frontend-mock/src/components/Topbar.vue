<script setup lang="ts">
defineProps<{
  documentName: string;
  stage: 'upload' | 'segmenting' | 'review' | 'generate';
}>();

const emit = defineEmits<{
  openSettings: [];
  openHelp: [];
  toggleDrawer: [];
}>();

const stageTitle: Record<'upload' | 'segmenting' | 'review' | 'generate', string> = {
  upload: 'Upload',
  segmenting: 'Segmenting',
  review: 'Review',
  generate: 'Generate',
};
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-slate-200 bg-white/85 px-4 py-3 backdrop-blur lg:px-6">
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-sm text-slate-700 lg:hidden" @click="emit('toggleDrawer')">Menu</button>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Storybook Document</p>
          <h1 class="comic-title text-base font-semibold md:text-lg">{{ documentName }}</h1>
        </div>
      </div>

      <div class="hidden rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 md:block">
        Stage: {{ stageTitle[stage] }}
      </div>

      <div class="hidden items-center gap-2 md:flex">
        <button class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm" @click="emit('openHelp')">Shortcuts</button>
        <button class="rounded-full bg-slate-900 px-3 py-1.5 text-sm text-white" @click="emit('openSettings')">Настройки</button>
      </div>
    </div>
  </header>
</template>
