# Maton → Google Search Console для InService

Эта папка нужна, чтобы получать данные Search Console через Maton Gateway и сохранять CSV-выгрузки для анализа.

## Важно про безопасность

Не вставляй реальный ключ в GitHub, Google Sheets или публичные документы. Если ключ уже был отправлен в чат, лучше удалить его в Maton и создать новый.

Скрипт читает ключ из переменной окружения `MATON_API_KEY` или из локального файла `.env`, который игнорируется git.

## Быстрый старт

1. Создать локальный `.env` рядом с `README.md` проекта:

```powershell
Copy-Item .env.example .env
notepad .env
```

2. Вставить новый ключ Maton в `.env`:

```text
MATON_API_KEY=...
```

3. Проверить доступные сайты Search Console:

```powershell
python tools\gsc\maton_gsc_export.py sites
```

4. Выгрузить стандартные отчеты по электротранспорту за последние 28 дней:

```powershell
python tools\gsc\maton_gsc_export.py fetch-all --default-filters
```

Файлы появятся в `data/gsc/`.

## Одна ручная выгрузка

```powershell
python tools\gsc\maton_gsc_export.py fetch `
  --start-date 2026-05-01 `
  --end-date 2026-05-20 `
  --dimensions page,query,date `
  --page-filter elektrosamokat `
  --output data\gsc\gsc_elektrosamokat.csv
```

## Что анализируем

- `clicks` — клики из Google;
- `impressions` — показы;
- `ctr` — CTR;
- `position` — средняя позиция;
- `page` — страница;
- `query` — запрос;
- `date` — дата.

## Ограничение Search Console

Данные обычно запаздывают на 2-3 дня. Новые страницы, опубликованные 22.05.2026, могут не иметь статистики сразу.
