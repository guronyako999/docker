#!/usr/bin/env python3
"""
Мини-backend на стандартной библиотеке Python.
Отвечает GET /db-status — JSON со статусом подключения к PostgreSQL.
Зависимость: psycopg[binary] (ставится в Dockerfile backend).
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "aurora_db")
DB_USER = os.getenv("DB_USER", "aurora_user")
DB_PASS = os.getenv("DB_PASSWORD", "aurora_pass")


def get_status() -> dict:
    dsn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    try:
        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("select version()")
                version = cur.fetchone()[0].split(",")[0]
                cur.execute(
                    """
                    select table_name from information_schema.tables
                    where table_schema = 'public' order by table_name
                    """
                )
                tables = [r[0] for r in cur.fetchall()]
        return {"database_connected": True, "version": version, "tables": tables}
    except Exception as e:  # noqa: BLE001
        return {"database_connected": False, "error": str(e)}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path in ("/db-status", "/health"):
            body = json.dumps(get_status(), ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        elif path == "/":
            # корень бэкенда — подсказка, чтобы любой запрос давал осмысленный ответ
            body = json.dumps({
                "service": "aurora-backend",
                "endpoints": ["/db-status", "/health"],
            }, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        else:
            body = json.dumps({"error": "not found"}, ensure_ascii=False).encode("utf-8")
            self._send(404, body, "application/json; charset=utf-8")

    def log_message(self, *args):  # тихий лог
        pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"aurora-backend listening on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
