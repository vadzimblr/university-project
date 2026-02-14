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

## Концепт UI
- Интерфейс оформлен как comic/storybook: контрастные рамки панелей, "кадры", подписи и onboarding про нарративный темп.
- Цель — собрать визуальную последовательность сцен, а не просто набор отдельных иллюстраций.

## UX для больших документов (100+ страниц)
- Пагинация списка сцен (`listPage`, `pageSize`) + переключение compact cards.
- Batch approve/unapprove для текущей страницы списка.
- В редакторе сцены есть sentence window (6/8/12 предложений) и навигация окнами для комфортной работы с длинным текстом.
- Storyboard strip показывает готовые панели как итоговую последовательность результата.
