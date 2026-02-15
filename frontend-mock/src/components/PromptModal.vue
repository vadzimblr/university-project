<script setup lang="ts">
defineProps<{ open: boolean; prompt: string }>();
const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="emit('close')">
    <div class="w-full max-w-xl rounded-2xl bg-white p-5 shadow-2xl">
      <h3 class="mb-3 text-lg font-semibold">Prompt preview</h3>
      <p class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">{{ prompt }}</p>
      <div class="mt-4 text-right">
        <button class="rounded-lg border border-slate-200 px-3 py-1.5" @click="emit('close')">Закрыть</button>
      </div>
    </div>
  </div>
</template>
