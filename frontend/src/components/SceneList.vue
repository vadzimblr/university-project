<script setup lang="ts">
import type { Illustration, Scene, SceneStatus } from '@/types/models';
import SceneCard from './SceneCard.vue';

defineProps<{
  scenes: Scene[];
  illustrations: Record<string, Illustration>;
  selectedSceneId: string | null;
  search: string;
  statusFilter: 'all' | SceneStatus;
  sortBy: 'index' | 'status';
  listPage: number;
  totalPages: number;
  totalFiltered: number;
  pageSize: number;
}>();

const emit = defineEmits<{
  choose: [id: string];
  updateSearch: [value: string];
  updateStatusFilter: [value: 'all' | SceneStatus];
  updateSortBy: [value: 'index' | 'status'];
  updatePage: [value: number];
  updatePageSize: [value: number];
}>();
</script>

<template>
  <aside class="comic-card h-full bg-white/90 p-3">
    <div class="mb-3 space-y-2">
      <p class="comic-title text-sm font-semibold">Сцены</p>
      <input
        :value="search"
        type="text"
        placeholder="Поиск сцен..."
        class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
        @input="emit('updateSearch', ($event.target as HTMLInputElement).value)"
      />

      <select
        :value="String(pageSize)"
        class="w-full rounded-lg border border-slate-200 px-2 py-2 text-sm"
        @change="emit('updatePageSize', Number(($event.target as HTMLSelectElement).value))"
      >
        <option value="6">6 / страница</option>
        <option value="8">8 / страница</option>
        <option value="12">12 / страница</option>
      </select>
    </div>

    <div class="mb-2 flex items-center justify-between text-xs font-semibold text-slate-700">
      <span>{{ totalFiltered }} сцен</span>
      <span>страница {{ listPage }} / {{ totalPages }}</span>
    </div>

    <div class="space-y-2 overflow-y-auto pb-4" style="max-height: calc(100vh - 320px)">
      <SceneCard
        v-for="scene in scenes"
        :key="scene.id"
        :scene="scene"
        :illustration="illustrations[scene.id]"
        :selected="selectedSceneId === scene.id"
        @edit="emit('choose', $event)"
      />
    </div>

    <div class="mt-3 grid grid-cols-2 gap-2">
      <button class="rounded border border-slate-200 bg-white px-2 py-1 text-xs font-semibold" :disabled="listPage <= 1" @click="emit('updatePage', listPage - 1)">Назад</button>
      <button class="rounded border border-slate-200 bg-white px-2 py-1 text-xs font-semibold" :disabled="listPage >= totalPages" @click="emit('updatePage', listPage + 1)">Вперёд</button>
    </div>
  </aside>
</template>
