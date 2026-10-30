"""Fetch current weather from Open-Meteo and store it in SQLite."""
import sqlite3
from datetime import datetime, timezone

import requests

# A few cities: (name, latitude, longitude)
CITIES = [
    ("Delhi", 28.61, 77.21),
    ("London", 51.51, -0.13),
    ("New York", 40.71, -74.01),
]

DB_PATH = "weather.db"


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            windspeed_kmh REAL NOT NULL,
            observed_at TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def fetch_city(city: str, lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()["current_weather"]
    return {
        "city": city,
        "temperature_c": data["temperature"],
        "windspeed_kmh": data["windspeed"],
        "observed_at": data["time"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    for city, lat, lon in CITIES:
        try:
            row = fetch_city(city, lat, lon)
            conn.execute(
                """
                INSERT INTO weather_readings
                    (city, temperature_c, windspeed_kmh, observed_at, fetched_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row["city"],
                    row["temperature_c"],
                    row["windspeed_kmh"],
                    row["observed_at"],
                    row["fetched_at"],
                ),
            )
            conn.commit()
            print(f"[OK] {city}: {row['temperature_c']} C")
        except Exception as e:
            print(f"[FAIL] {city}: {e}")

    conn.close()


if __name__ == "__main__":
    main()