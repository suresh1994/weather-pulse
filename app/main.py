"""FastAPI service exposing weather readings stored in SQLite."""
import sqlite3

from fastapi import FastAPI, HTTPException

DB_PATH = "weather.db"

app = FastAPI(title="Weather Pulse", version="0.1.0")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us return dicts
    return conn


@app.get("/health")
def health() -> dict:
    """Simple liveness probe — used later by Render & Docker."""
    return {"status": "ok"}


@app.get("/weather")
def all_cities() -> list[dict]:
    """Latest reading for every city we track."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT w.city, w.temperature_c, w.windspeed_kmh, w.observed_at
            FROM weather_readings w
            JOIN (
                SELECT city, MAX(id) AS max_id
                FROM weather_readings
                GROUP BY city
            ) latest ON latest.max_id = w.id
            ORDER BY w.city
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/weather/{city}")
def city_latest(city: str) -> dict:
    """Latest reading for a single city (case-insensitive)."""
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT city, temperature_c, windspeed_kmh, observed_at
            FROM weather_readings
            WHERE LOWER(city) = LOWER(?)
            ORDER BY id DESC
            LIMIT 1
            """,
            (city,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No data for {city}")
        return dict(row)
    finally:
        conn.close()


@app.get("/weather/{city}/history")
def city_history(city: str, limit: int = 20) -> list[dict]:
    """Recent readings for a city, newest first."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT city, temperature_c, windspeed_kmh, observed_at
            FROM weather_readings
            WHERE LOWER(city) = LOWER(?)
            ORDER BY id DESC
            LIMIT ?
            """,
            (city, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()