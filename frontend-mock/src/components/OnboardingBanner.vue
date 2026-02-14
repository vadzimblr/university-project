<script setup lang="ts">
const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <div class="rounded-xl border border-brand-200 bg-brand-50 p-4">
    <h3 class="text-sm font-semibold text-brand-700">Как править сцены эффективно</h3>
    <ul class="mt-2 list-disc pl-5 text-sm text-brand-700">
      <li>Сдвигайте Start/End по одному предложению для точного snap.</li>
      <li>Используйте Split по кликнутому предложению внутри сцены.</li>
      <li>Approve только хорошие сцены и запускайте Generate.</li>
    </ul>
    <button class="mt-3 rounded-lg bg-brand-600 px-3 py-1.5 text-sm text-white" @click="emit('close')">Понятно</button>
  </div>
</template>
