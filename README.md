# InService SEO 2026

Рабочий GitHub Pages-проект с HTML-прототипами SEO-страниц InService по направлению ремонта электротранспорта.

## Как смотреть прототип

После публикации через GitHub Pages открыть корневую страницу репозитория. Локально можно открыть:

- `index.html` — стартовая навигация по проекту;
- `site/transport/remont-elektrosamokativ-kharkiv.html` — основная страница ремонта электросамокатов;
- `project-map.html` — карта структуры проекта.

## Основные разделы

- `site/transport/` — HTML-прототипы страниц;
- `docs/strategy/` — семантика, планы, SEO-структура;
- `docs/handoff/` — SEO-тексты и handoff для верстальщика;
- `project-tracker/` — таблица проекта XLSX/CSV;
- `assets/` — материалы и ассеты;
- `archive/` — старые демо и промежуточные версии.

## Ключевые страницы

### P0

- `site/transport/remont-elektrosamokativ-kharkiv.html` — ремонт электросамокатов в Харькове.

### Поломки и узлы

- `site/transport/elektrosamokat-ne-zaryadzhayetsya-kharkiv.html`;
- `site/transport/elektrosamokat-ne-vmykayetsya-kharkiv.html`;
- `site/transport/elektrosamokat-pislya-vody-kharkiv.html`;
- `site/transport/remont-akumulyatora-elektrosamokata-kharkiv.html`;
- `site/transport/remont-kontrolera-elektrosamokata-kharkiv.html`;
- `site/transport/remont-motor-kolesa-elektrosamokata-kharkiv.html`.

### Бренды

- `site/transport/remont-elektrosamokativ-xiaomi-kharkiv.html`;
- `site/transport/remont-elektrosamokativ-ninebot-kharkiv.html`;
- `site/transport/remont-elektrosamokativ-kugoo-kharkiv.html`;
- `site/transport/remont-elektrosamokativ-crosser-kharkiv.html`;
- `site/transport/remont-elektrotransportu-giant-kharkiv.html`.

## Как опубликовать на GitHub Pages

1. Создать пустой репозиторий на GitHub, например `inservic-seo-2026`.
2. Выполнить локально:

```bash
git remote add origin https://github.com/USERNAME/inservic-seo-2026.git
git branch -M main
git push -u origin main
```

3. На GitHub открыть `Settings` -> `Pages`.
4. В `Build and deployment` выбрать:
   - Source: `Deploy from a branch`;
   - Branch: `main`;
   - Folder: `/root`.
5. Сохранить и подождать 1-3 минуты.

После публикации GitHub даст ссылку вида:

```text
https://USERNAME.github.io/inservic-seo-2026/
```
