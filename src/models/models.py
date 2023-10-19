from datetime import date

from pydantic import BaseModel
from sqlalchemy import Column, Integer, Date, String, Float

from src.db.database import Base


# Defining the booking data model
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_date = Column(Date)
    length_of_stay = Column(Integer)
    guest_name = Column(String)
    daily_rate = Column(Float)


# Create a Pydantic model corresponding to the SQLAlchemy (Booking) model
class BookingResponse(BaseModel):
    id: int
    booking_date: date
    length_of_stay: int
    guest_name: str
    daily_rate: float = None
    # bookings: list = None


# Pydantic model for request parameters
class NationalityRequest(BaseModel):
    nationality: str
