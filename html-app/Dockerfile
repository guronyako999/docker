# ============================================================
# Упаковка HTML-файлов + Nginx в Docker-образ
# Сборка:  docker build -t aurora-web ./html-app
# ============================================================
FROM nginx:1.27-alpine

# Удаляем дефолтный конфиг nginx
RUN rm /etc/nginx/conf.d/default.conf

# Кладём свой конфиг сервера
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Кладём HTML/CSS/JS в корень веб-сервера
COPY public/ /usr/share/nginx/html/

EXPOSE 80

# healthcheck: nginx жив?
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/ > /dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
