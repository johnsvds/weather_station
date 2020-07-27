import models
from typing import Optional
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import urllib.request
import json
from models import Weather_data
#import schedule
import sqlite3 as lite
import time

KAIMAKLI = "https://api.weather.com/v2/pws/observations/current?apiKey=6532d6454b8aa370768e63d6ba5a832e&stationId=INICOSIA31&numericPrecision=decimal&format=json&units=e"
UCY = "https://api.weather.com/v2/pws/observations/current?apiKey=6532d6454b8aa370768e63d6ba5a832e&stationId=IAGLANDJ2&numericPrecision=decimal&format=json&units=e"

def fahrenheit_to_celsius(tempF):
    return (tempF - 32) * 5/9

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def fetch_weather_data(db, link, weather):
    contents = json.loads(urllib.request.urlopen(link).read())
    data = contents["observations"][0]

    tempF = float(data["imperial"]["temp"])
    tempC = fahrenheit_to_celsius(tempF)

    heat_indexF = float(data["imperial"]["heatIndex"])
    heat_indexC = fahrenheit_to_celsius(heat_indexF)

    data["imperial"]["temp"] = round(tempC, 1)
    data["imperial"]["heatIndex"] = round(heat_indexC, 1)

    weather.timestamp = data["obsTimeLocal"]
    weather.neighborhood = data["neighborhood"]
    weather.humidity = data["humidity"]
    weather.windSpeed = data["imperial"]["windSpeed"]
    weather.temperature = data["imperial"]["temp"]
    weather.heatIndex = data["imperial"]["heatIndex"]

    db.add(weather)
    db.commit()


@app.get("/station/{station_name}")
async def read_station_weather(station_name: str,  background_tasks: BackgroundTasks ,  db: Session = Depends(get_db)):

    weather = Weather_data()
    link = UCY
    if station_name == "kaimakli":
        link = KAIMAKLI 
    elif station_name == "ucy":
        link =  UCY
   
    background_tasks.add_task(fetch_weather_data, db, link, weather)

    



@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    data = db.query(models.Weather_data).all()
    
    print(type(data), data)
    # data=json.dumps(data)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data
    })

# while True:
#     db = SessionLocal()
#     read_station_weather("ucy", db)
#     time.sleep(60)
