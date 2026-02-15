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
  <ol class="hidden items-center gap-2 text-xs text-slate-600 md:flex">
    <li v-for="step in steps" :key="step.key" class="flex items-center gap-2">
      <span
        class="flex h-7 w-7 items-center justify-center rounded-md border border-slate-200 font-bold"
        :class="[
          step.key === stage ? 'bg-slate-900 text-white' : 'bg-white',
          isComplete(step.key) ? 'bg-emerald-500 text-white' : '',
        ]"
      >
        {{ steps.findIndex((s) => s.key === step.key) + 1 }}
      </span>
      <span class="font-semibold">{{ step.label }}</span>
      <span v-if="step.key !== 'generate'" class="h-0.5 w-6 bg-slate-300" />
    </li>
  </ol>
</template>
