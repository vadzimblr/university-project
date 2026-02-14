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
  compactCards: boolean;
}>();

const emit = defineEmits<{
  choose: [id: string];
  approve: [id: string, approved: boolean];
  regenerate: [id: string];
  updateSearch: [value: string];
  updateStatusFilter: [value: 'all' | SceneStatus];
  updateSortBy: [value: 'index' | 'status'];
  updatePage: [value: number];
  updatePageSize: [value: number];
  toggleCompact: [value: boolean];
  approvePage: [approved: boolean];
}>();
</script>

<template>
  <aside class="comic-card h-full bg-orange-50 p-3">
    <div class="mb-3 space-y-2">
      <p class="comic-title text-sm font-black">Storyboard Scenes</p>
      <input
        :value="search"
        type="text"
        placeholder="Поиск сцен..."
        class="w-full rounded-lg border-2 border-slate-900 px-3 py-2 text-sm"
        @input="emit('updateSearch', ($event.target as HTMLInputElement).value)"
      />

      <div class="grid grid-cols-2 gap-2">
        <select
          :value="statusFilter"
          class="rounded-lg border-2 border-slate-900 px-2 py-2 text-sm"
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
          class="rounded-lg border-2 border-slate-900 px-2 py-2 text-sm"
          @change="emit('updateSortBy', ($event.target as HTMLSelectElement).value as any)"
        >
          <option value="index">Сорт: номер</option>
          <option value="status">Сорт: статус</option>
        </select>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <select
          :value="String(pageSize)"
          class="rounded-lg border-2 border-slate-900 px-2 py-2 text-sm"
          @change="emit('updatePageSize', Number(($event.target as HTMLSelectElement).value))"
        >
          <option value="6">6 / page</option>
          <option value="8">8 / page</option>
          <option value="12">12 / page</option>
        </select>
        <label class="flex items-center justify-center gap-2 rounded-lg border-2 border-slate-900 bg-white px-2 text-xs font-semibold">
          <input type="checkbox" :checked="compactCards" @change="emit('toggleCompact', ($event.target as HTMLInputElement).checked)" /> compact
        </label>
      </div>

      <div class="flex flex-wrap gap-2">
        <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-xs font-semibold" @click="emit('approvePage', true)">Approve page</button>
        <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-xs font-semibold" @click="emit('approvePage', false)">Unapprove page</button>
      </div>
    </div>

    <div class="mb-2 flex items-center justify-between text-xs font-semibold text-slate-700">
      <span>{{ totalFiltered }} scenes</span>
      <span>page {{ listPage }} / {{ totalPages }}</span>
    </div>

    <div class="space-y-2 overflow-y-auto pb-4" style="max-height: calc(100vh - 340px)">
      <SceneCard
        v-for="scene in scenes"
        :key="scene.id"
        :scene="scene"
        :illustration="illustrations[scene.id]"
        :selected="selectedSceneId === scene.id"
        :compact="compactCards"
        @edit="emit('choose', $event)"
        @approve="(id, approved) => emit('approve', id, approved)"
        @regenerate="emit('regenerate', $event)"
      />
    </div>

    <div class="mt-3 grid grid-cols-2 gap-2">
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-xs font-semibold" :disabled="listPage <= 1" @click="emit('updatePage', listPage - 1)">Prev</button>
      <button class="rounded border-2 border-slate-900 bg-white px-2 py-1 text-xs font-semibold" :disabled="listPage >= totalPages" @click="emit('updatePage', listPage + 1)">Next</button>
    </div>
  </aside>
</template>
