from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric
from database import Base


class Weather_data(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, unique=True)
    neighborhood = Column(String)
    humidity = Column(Numeric(3,2))
    temperature = Column(Numeric(3,2))
    heatIndex = Column(Numeric(3,2))
    windSpeed = Column(Numeric(3,2))

class Station(Base):
    __tablename__ = "station"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    url = Column(String)
    neighborhood = Column(String)
