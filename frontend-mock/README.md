# Story Illustrator Mock Frontend (Vue 3 + Vite)

Демо-шаблон фронтенда для автоматической иллюстрации рассказа из PDF.

## Стек
- Vue 3 + Vite
- TypeScript
- Tailwind CSS
- Pinia
- Vue Router

## Запуск
```bash
npm i
npm run dev
npm run build
```

## Структура
```text
src/
  app/                # app shell + router
  pages/              # UploadPage, WorkspacePage
  components/         # Topbar, Stepper, SceneList, SceneCard, SceneEditor, IllustrationPanel, modals
  stores/             # documentsStore, scenesStore, uiStore
  mock/               # mockStory (предложения), mockDocuments
  styles/             # Tailwind entry
  types/              # модели сущностей
```

## Где менять моковые данные
- Документы: `src/mock/mockDocuments.ts`
- Текст рассказа по предложениям: `src/mock/mockStory.ts`
- Логика сегментации и генерации: `src/stores/scenesStore.ts`

## Как устроено состояние
- `documentsStore`: недавние документы, активный документ, добавление нового.
- `uiStore`: прогресс upload/segmenting, выбор сцены, модалки, onboarding, mobile drawer.
- `scenesStore`: сцены, фильтры/сортировка, операции Split/Merge/границы, генерация (с ограничением параллелизма 3), иллюстрации и error-state.
