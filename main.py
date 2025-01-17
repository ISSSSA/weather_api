from fastapi import FastAPI, HTTPException, Query
from app.models import AddCityRequest, RegisterUserRequest
from app.db_methods import init_db, get_all_cities, save_weather_to_db, add_city_to_db, get_cities_for_user, \
    register_user_in_db
import asyncio
import httpx
from datetime import datetime
import sqlite3

API_URL = "https://api.open-meteo.com/v1/forecast"
UPDATE_INTERVAL = 15 * 60

DB_NAME = "weather.db"

init_db()

app = FastAPI(
    title="Weather Forecast API",
    description="Данное API позволяет получать пользователям погоду в своем городе и по заданным координатам",
    version="1.0.0",
    contact={
        "name": "Воронов Игорь Сергеевич",
        "url": "https://t.me/ISSSSSSSSSSA",
        "email": "igorsvoronov@gmail.com"
    }
)


async def update_weather():
    while True:
        cities = get_all_cities()
        for city in cities:
            weather_data = await fetch_weather(city["lat"], city["lon"])
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weather WHERE city_id = ?", (city["id"],))
            conn.commit()
            conn.close()
            save_weather_to_db(city["id"], weather_data)
        await asyncio.sleep(UPDATE_INTERVAL)


async def fetch_weather(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "temperature_2m,relative_humidity_2m,windspeed_10m,pressure_msl"
        }
        response = await client.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()


@app.on_event("startup")
def startup_event():
    asyncio.create_task(update_weather())


@app.get("/weather", summary="Получить текущую погоду",
         description="Получить текущую погоду, по предоставленным координатам")
async def get_current_weather(lat: float = Query(..., description="Широта локации пример 70.3333"),
                              lon: float = Query(..., description="Долгота локации пример 6.4444")):
    weather_data = await fetch_weather(lat, lon)
    current_weather = weather_data.get("current_weather", {})
    print(current_weather)
    return {
        "temperature": current_weather.get("temperature"),
        "wind_speed": current_weather.get("windspeed"),
    }


@app.post("/city", summary="Добавить свой город для его трекинга",
          description="Добавь по id пользователя город в список его городов")
async def add_city(request: AddCityRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (request.user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found.")

    add_city_to_db(request.user_id, request.city, request.lat, request.lon)

    cursor.execute("SELECT id FROM cities WHERE user_id = ? AND city = ?", (request.user_id, request.city))
    city_id = cursor.fetchone()[0]
    conn.close()

    weather_data = await fetch_weather(request.lat, request.lon)
    save_weather_to_db(city_id, weather_data)

    return {"message": f"City {request.city} added for user {request.user_id} and weather data saved."}


@app.get("/cities", summary="Список отслеживаемых городов",
         description="Получи все города для конкретного пользователя")
async def list_cities(user_id: int = Query(..., description="ПОлучи города по id")):
    cities = get_cities_for_user(user_id)
    return {"cities": cities}


@app.post("/register", summary="Зарегестрируй пользователя и получи его id",
          description="Сверху написано, так что пояснять не буду")
async def register_user(request: RegisterUserRequest):
    try:
        user_id = register_user_in_db(request.username)
        return {"user_id": user_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists.")


@app.get("/weather_at_time", summary="Время в iso формате!!!!!",
         description="Получи для конкретного пользователя погоду в его городе по времени")
async def get_weather_at_time(
        user_id: int = Query(..., description="User ID"),
        city: str = Query(..., description="City name"),
        time: str = Query(..., description="Время в таком формате указывать 2025-01-16T14:00:00"),
        temperature: bool = Query(True, description="Температура"),
        humidity: bool = Query(True, description="Осадки"),
        wind_speed: bool = Query(True, description="Ветер ветер ты могуч, ты гоняешь стаи туч"),
        pressure: bool = Query(True, description="Атмосферное давление")
):
    requested_time = datetime.fromisoformat(time)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

    cursor.execute("""
    SELECT id, lat, lon FROM cities
    WHERE user_id = ? AND city = ?
    """, (user_id, city))
    city_data = cursor.fetchone()
    conn.close()

    if not city_data:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found for user ID {user_id}.")

    city_id, lat, lon = city_data

    weather_data = await fetch_weather(lat, lon)
    hourly_data = weather_data.get("hourly", {})

    for i, time_point in enumerate(hourly_data["time"]):
        time_point_dt = datetime.fromisoformat(time_point)
        if time_point_dt == requested_time:
            weather_at_time = {
                "time": time_point,
            }
            if temperature:
                weather_at_time["temperature"] = hourly_data["temperature_2m"][i]
            if humidity:
                weather_at_time["humidity"] = hourly_data["relative_humidity_2m"][i]
            if wind_speed:
                weather_at_time["wind_speed"] = hourly_data["windspeed_10m"][i]
            if pressure:
                weather_at_time["pressure"] = hourly_data.get("pressure_msl", [None])[i]

            return weather_at_time

    raise HTTPException(status_code=404, detail="Weather data for the specified time not found.")


@app.get("/city_weather", summary="ПОлучи просто погоду по городу, это вне задания сделал просто так",
         description="Получите время из базы данных для конкретного города без привязки к пользователю.")
async def get_city_weather(city: str = Query(..., description="City name")):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT w.time, w.temperature, w.humidity, w.wind_speed, w.pressure
    FROM weather w
    JOIN cities c ON w.city_id = c.id
    WHERE c.city = ?
    """, (city,))
    weather = [
        {
            "time": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "wind_speed": row[3],
            "pressure": row[4]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return {"city": city, "weather": weather}
