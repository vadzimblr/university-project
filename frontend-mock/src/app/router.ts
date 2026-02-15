import { createRouter, createWebHistory } from 'vue-router';
import UploadPage from '@/pages/UploadPage.vue';
import WorkspacePage from '@/pages/WorkspacePage.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/upload' },
    { path: '/upload', name: 'upload', component: UploadPage },
    { path: '/doc/:id', name: 'workspace', component: WorkspacePage },
  ],
});
