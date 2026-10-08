# ✦ Aurora — HTML + Nginx + PostgreSQL в Docker

Готовый проект: красивые HTML-страницы (тёмная тема **«Aurora»**) упакованы в Docker-образ
вместе с **Nginx**, поднимаются через **docker-compose** бок о бок с **PostgreSQL**,
с настроенным **пробросом портов** и мини-backend'ом, который проверяет подключение к базе.

## Структура проекта

```
.
├── docker-compose.yml          # оркестрация: web + backend + postgres
├── .env.example                # переменные окружения (БД)
├── html-app/                   # ← наше HTML-приложение, «упакованное» с nginx
│   ├── Dockerfile              # образ на базе nginx:1.27-alpine
│   ├── nginx/default.conf      # конфиг сайта: статика + gzip + прокси /api/
│   └── public/                 # HTML / CSS / JS (тема Aurora)
│       ├── index.html
│       ├── about.html
│       ├── css/style.css
│       └── js/app.js
├── backend/                    # Python-сервис проверки статуса PostgreSQL
│   ├── Dockerfile
│   └── app.py
└── db/init/01-init.sql         # init-скрипт БД (таблица notes + данные)
```

## Быстрый старт

```bash
cp .env.example .env            # при необходимости поменяйте пароли
docker compose up -d --build    # собрать образы и запустить весь стек
docker compose ps               # убедиться, что все сервисы healthy/up
```

| Что                       | Адрес                                                     |
|---------------------------|-----------------------------------------------------------|
| 🌐 Сайт (nginx)           | http://localhost:8080                                     |
| 🔌 API статуса БД         | http://localhost:8080/api/db-status                       |
| 🐘 PostgreSQL с хоста     | `localhost:5433` (user `aurora_user`, pass `aurora_pass`) |

Остановить стек: `docker compose down` (добавьте `-v`, чтобы удалить том с данными БД).

## Как устроен проброс портов в Docker

Проброс (port mapping) задаётся параметром **`-p хост:контейнер`** при запуске
или секцией **`ports:`** в `docker-compose.yml`. Формат:

```
ports:
  - "8080:80"   # порт 8080 на ХОСТЕ  ->  порт 80 ВНУТРИ контейнера
```

После этого обращение к `http://localhost:8080` docker автоматически доставляет
трафик на `nginx:80` внутри контейнера. Взаимодействие контейнеров **между собой**
идёт напрямую по внутренней сети (`aurora-net`) и проброса не требует:
nginx обращается к `http://backend:8000`, а backend — к `db:5432`.

### Варианты проброса

```bash
# 1. Классический: хост:контейнер
docker run -d -p 8080:80 aurora-web

# 2. Случайный порт хоста: docker сам выберет, покажет его через `docker ps`
docker run -d -p 80 aurora-web

# 3. Привязка только к конкретному интерфейсу
docker run -d -p 127.0.0.1:8080:80 aurora-web

# 4. То же самое в docker-compose.yml
services:
  web:
    ports:
      - "8080:80"        # веб (nginx)
  db:
    ports:
      - "5433:5432"      # postgres: наружу 5433, чтобы не спорить с локальным 5432
```

В этом проекте проброшены:
* **web**: `8080:80` — сайт доступен с хоста;
* **db**: `5433:5432` — можно подключиться из DBeaver/psql:
  `psql -h localhost -p 5433 -U aurora_user -d aurora_db`;
* **backend** наружу **не** проброшен намеренно — доступ только через nginx (`/api/`).

## Альтернатива: Caddy вместо Nginx

Хотите Caddy? Замените `html-app/Dockerfile` на:

```dockerfile
FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY public/ /srv
EXPOSE 80 443 2019
```

и создайте `html-app/Caddyfile`:

```caddyfile
:80 {
    root * /srv
    encode gzip zstd
    handle_path /api/* {
        reverse_proxy backend:8000
    }
    handle {
        file_server
        try_files {path} {path}/ /index.html
    }
}
```

Caddy умеет и автоматический HTTPS: замените `:80` на `your-domain.com` — сертификаты
Let's Encrypt будут получены и продлены автоматически. В остальном достаточно пересобрать:
`docker compose up -d --build web`.

## Проверка

```bash
curl http://localhost:8080/               # HTML главной страницы
curl http://localhost:8080/api/db-status  # JSON: {"database_connected": true, ...}
docker exec -it aurora-db psql -U aurora_user -d aurora_db -c "select * from notes;"
```

---
© 2026 Aurora Project · Nginx 1.27-alpine · Postgres 16-alpine · Python 3.12-alpine
