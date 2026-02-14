<script setup lang="ts">
const emit = defineEmits<{ close: [] }>();
</script>

<template>
  <div class="comic-card halftone bg-yellow-100 p-4">
    <h3 class="comic-title text-sm font-black">First issue: как собрать storybook, а не набор картинок</h3>
    <ul class="mt-2 list-disc pl-5 text-sm text-slate-800">
      <li>Подправь Start/End, чтобы сцены читались как последовательные кадры.</li>
      <li>Split/Merge используй для темпа: короткие моменты vs длинные развороты.</li>
      <li>Approve только сцены, которые уже работают как визуальный нарратив.</li>
    </ul>
    <button class="kaboom-btn mt-3" @click="emit('close')">Понятно</button>
  </div>
</template>
