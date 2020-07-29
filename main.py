import models
from typing import Optional
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import urllib.request
import json
from models import Weather_data
import sqlite3 as lite
import time
import argparse
import asyncio

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

def get_stations():
    db = SessionLocal()
    station_list = {}
    stations =  db.query(models.Station).all()
    for station in stations:
        station_list[station.name] = [station.url, station.neighborhood]
    return station_list


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

    print(weather.timestamp)

    db.add(weather)
    db.commit()
    data = db.query(models.Weather_data).order_by(models.Weather_data.id.desc()).filter_by(neighborhood = "University of Cyprus").limit(2)
    # print(data)
      

def read_station_weather(db):
    stations = get_stations()
    for station in stations:
        print(stations[station][0])
        weather = Weather_data()
        fetch_weather_data(db, stations[station][0], weather)
   

def controller(args, db):
    if args.get:
        read_station_weather(db)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-g','--get', action='store_true')
    args=parser.parse_args()
    db = SessionLocal()
    controller(args, db)

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    data = db.query(models.Weather_data).order_by(models.Weather_data.id.desc()).limit(10)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data
    })

@app.get("/station/{station_name}")
def get_data_for_station(station_name, request: Request, db: Session = Depends(get_db)):
    stations = get_stations()

    data = db.query(models.Weather_data).order_by(models.Weather_data.id.desc()).filter_by(neighborhood = stations[station_name][1]).limit(10)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data
    })



if __name__ == "__main__":
    main()