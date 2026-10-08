-- Инициализация базы данных Aurora (выполняется автоматически при первом старте postgres)
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO notes (title) VALUES
  ('Первая заметка из init-скрипта'),
  ('Docker + PostgreSQL = ❤'),
  ('Тема Aurora');
