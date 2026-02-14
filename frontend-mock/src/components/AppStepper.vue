<script setup lang="ts">
const props = defineProps<{ stage: 'upload' | 'segmenting' | 'review' | 'generate' }>();

const steps = [
  { key: 'upload', label: 'Upload' },
  { key: 'segmenting', label: 'Segment' },
  { key: 'review', label: 'Review' },
  { key: 'generate', label: 'Generate' },
] as const;

function isComplete(stepKey: string) {
  return steps.findIndex((s) => s.key === stepKey) < steps.findIndex((s) => s.key === props.stage);
}
</script>

<template>
  <ol class="flex items-center gap-3 text-xs text-slate-500 md:text-sm">
    <li v-for="step in steps" :key="step.key" class="flex items-center gap-3">
      <span
        class="flex h-7 w-7 items-center justify-center rounded-full border"
        :class="[
          step.key === stage ? 'border-brand-600 bg-brand-600 text-white' : '',
          isComplete(step.key) ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300 bg-white',
        ]"
      >
        {{ steps.findIndex((s) => s.key === step.key) + 1 }}
      </span>
      <span class="hidden md:inline">{{ step.label }}</span>
      <span v-if="step.key !== 'generate'" class="hidden h-px w-8 bg-slate-300 md:inline" />
    </li>
  </ol>
</template>
