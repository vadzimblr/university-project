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
}>();

const emit = defineEmits<{
  choose: [id: string];
  approve: [id: string, approved: boolean];
  regenerate: [id: string];
  updateSearch: [value: string];
  updateStatusFilter: [value: 'all' | SceneStatus];
  updateSortBy: [value: 'index' | 'status'];
}>();
</script>

<template>
  <aside class="h-full border-r border-slate-200 bg-slate-50 p-3">
    <div class="mb-3 space-y-2">
      <input
        :value="search"
        type="text"
        placeholder="Поиск сцен..."
        class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
        @input="emit('updateSearch', ($event.target as HTMLInputElement).value)"
      />
      <div class="flex gap-2">
        <select
          :value="statusFilter"
          class="w-1/2 rounded-lg border border-slate-200 px-2 py-2 text-sm"
          @change="emit('updateStatusFilter', ($event.target as HTMLSelectElement).value as any)"
        >
          <option value="all">Все статусы</option>
          <option value="pending">pending</option>
          <option value="approved">approved</option>
          <option value="generating">generating</option>
          <option value="ready">ready</option>
          <option value="error">error</option>
        </select>
        <select
          :value="sortBy"
          class="w-1/2 rounded-lg border border-slate-200 px-2 py-2 text-sm"
          @change="emit('updateSortBy', ($event.target as HTMLSelectElement).value as any)"
        >
          <option value="index">Сорт: по номеру</option>
          <option value="status">Сорт: по статусу</option>
        </select>
      </div>
    </div>

    <div class="space-y-2 overflow-y-auto pb-10" style="max-height: calc(100vh - 190px)">
      <SceneCard
        v-for="scene in scenes"
        :key="scene.id"
        :scene="scene"
        :illustration="illustrations[scene.id]"
        :selected="selectedSceneId === scene.id"
        @edit="emit('choose', $event)"
        @approve="(id, approved) => emit('approve', id, approved)"
        @regenerate="emit('regenerate', $event)"
      />
    </div>
  </aside>
</template>
