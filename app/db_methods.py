from typing import List
import sqlite3

DB_NAME = "weather.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        city TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        time TIMESTAMP NOT NULL,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        pressure REAL,
        FOREIGN KEY (city_id) REFERENCES cities (id)
    )
    """)
    conn.commit()
    conn.close()


def get_all_cities() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, city, lat, lon FROM cities")
    cities = [
        {"id": row[0], "city": row[1], "lat": row[2], "lon": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return cities


def save_weather_to_db(city_id: int, weather_data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for i, time_point in enumerate(weather_data["hourly"]["time"]):
        cursor.execute("""
        INSERT INTO weather (city_id, time, temperature, humidity, wind_speed, pressure)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            city_id,
            time_point,
            weather_data["hourly"]["temperature_2m"][i],
            weather_data["hourly"]["relative_humidity_2m"][i],
            weather_data["hourly"]["windspeed_10m"][i],
            weather_data["hourly"].get("pressure_msl", [None])[i]
        ))
    conn.commit()
    conn.close()


def register_user_in_db(username: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def add_city_to_db(user_id: int, city: str, lat: float, lon: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cities (user_id, city, lat, lon) VALUES (?, ?, ?, ?)", (user_id, city, lat, lon))
    conn.commit()
    conn.close()


def get_cities_for_user(user_id: int) -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT city, lat, lon FROM cities WHERE user_id = ?", (user_id,))
    cities = [
        {"city": row[0], "lat": row[1], "lon": row[2]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return cities
