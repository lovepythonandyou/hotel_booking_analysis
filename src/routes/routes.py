from datetime import date
from typing import List, Dict

import pandas as pd
from fastapi import Depends, HTTPException, FastAPI, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.auth.auth import verify_credentials
from src.db.database import get_db, engine
from src.models.models import Booking, BookingResponse
from src.operations.load_data import load_data

app = FastAPI()


# Endpoint for uploading a csv file
@app.post("/upload-csv/")
async def upload_csv(file: UploadFile):
    try:
        # Reading data from the uploaded CSV file
        df = pd.read_csv(file.file)

        # Data entry in the “bookings” table of the database
        df.to_sql("bookings", engine, if_exists="replace", index=False)

        return JSONResponse(
            content={"message": "The CSV file has been successfully uploaded and written to the database"},
            status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Endpoint for retrieving a list of all bookings
@app.get("/bookings/")
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings


# Endpoint for extracting detailed information about a particular booking by its unique identifier.
@app.get("/bookings/{booking_id}")
def get_booking_by_id(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


# Endpoint for finding bookings based on parameters
@app.get("/bookings/search/", response_model=List[BookingResponse])
def search_bookings(
        guest_name: str = Query(None, description="The name of the guest to search for"),
        booking_date: date = Query(None, description="The booking date for the search"),
        length_of_stay: int = Query(None, description="Duration of stay for the search"),
        db: Session = Depends(get_db)
):
    # Creating an initial query to the database
    query = db.query(Booking)

    # Apply filters based on the passed parameters
    if guest_name:
        query = query.filter(Booking.guest_name == guest_name)
    if booking_date:
        query = query.filter(Booking.booking_date == booking_date)
    if length_of_stay:
        query = query.filter(Booking.length_of_stay == length_of_stay)

    # Getting search results
    bookings = query.all()

    # Convert query results to BookingResponse objects
    booking_responses = [BookingResponse(id=booking.id, guest_name=booking.guest_name,
                                         booking_date=booking.booking_date,
                                         length_of_stay=booking.length_of_stay,
                                         daily_rate=booking.daily_rate) for booking in bookings]

    return booking_responses


# Endpoint for providing statistical information
@app.get("/bookings/stats/", response_model=Dict[str, float])
def get_booking_stats(db: Session = Depends(get_db)):
    # Calculating statistical information using SQLAlchemy
    total_bookings = db.query(func.count(Booking.id)).scalar()
    avg_length_of_stay = db.query(func.avg(Booking.length_of_stay)).scalar()
    avg_daily_rate = db.query(func.avg(Booking.daily_rate)).scalar()

    # Creating a dictionary with statistics results
    stats = {
        "total_bookings": total_bookings,
        "avg_length_of_stay": avg_length_of_stay,
        "avg_daily_rate": avg_daily_rate
    }

    return stats


# Endpoint for analyzing the amount bookings by month
@app.get("/bookings/analysis/")
async def get_booking_analysis():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Checking if there is information about bookings
    if data.empty:
        raise HTTPException(status_code=404, detail="Booking information not found")

    # Extracting the month from the 'arrival_date_month' column and counting the amount bookings by a month.
    booking_analysis = data['arrival_date_month'].value_counts().reset_index()
    booking_analysis.columns = ['month', 'count']

    # Converting results to a dictionary list
    booking_analysis_list = booking_analysis.to_dict(orient='records')

    return booking_analysis_list


# Endpoint for retrieving bookings by nationality
@app.get("/bookings/nationality/")
async def get_bookings_by_nationality(
        nationality: str = Query(None, description="Nationality for which it is necessary to receive bookings"),
):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Performing data filtering by nationality
    filtered_data = data[data['country'] == nationality]

    # Checking if there are bookings with the specified nationality
    if filtered_data.empty:
        raise HTTPException(status_code=404, detail=f"No bookings for nationality'{nationality}'")

    # Selecting only the necessary columns (row number—index and country)
    selected_columns = ['country']
    bookings_by_nationality = filtered_data[
        selected_columns].copy()  # Creating a copy to avoid SettingWithCopyWarning

    # Assign values to the 'id' column using .loc[]
    bookings_by_nationality['id'] = bookings_by_nationality.index

    # Converting results to a dictionary list
    bookings_list = bookings_by_nationality.reset_index(drop=True).to_dict(orient='records')

    return bookings_list


# The endpoint for extracting the most popular power pack
@app.get("/bookings/popular_meal_package/")
async def get_most_popular_meal_package():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Performing data aggregation to find the most popular power pack
    most_popular_meal_package = data['meal'].mode()

    # Checking if there is information about a popular food package
    if most_popular_meal_package.empty:
        raise HTTPException(status_code=404, detail="Information about the most popular food package was not found")

    # Extract the value from the Series and convert it to a string.
    most_popular_meal_package = most_popular_meal_package.iloc[0]

    return {"most_popular_meal_package": most_popular_meal_package}


# Endpoint for extracting average length of stay
@app.get("/bookings/avg_length_of_stay/")
async def get_avg_length_of_stay():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Grouping data by booking year and hotel type and calculating the average length of stay.
    avg_length_of_stay = data.groupby(['arrival_date_year', 'hotel'])[[
        'stays_in_weekend_nights', 'stays_in_week_nights']].mean().reset_index()

    # Checking if there is information about the average length of stay.
    if avg_length_of_stay.empty:
        raise HTTPException(status_code=404, detail="Information about the average length of stay was not found")

    # Converting the results to a list of dictionaries (you can customize the output format according to your
    # requirements)
    avg_length_of_stay = avg_length_of_stay.to_dict(orient='records')

    return avg_length_of_stay


# Endpoint for extracting total revenue
@app.get("/bookings/total_revenue/")
async def get_total_revenue():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Filtering data to exclude cancelled bookings
    data = data[data['is_canceled'] == 0]

    # Creating a new column "total_revenue", which is the product of "adr" by the total number nights of stay.
    data['total_revenue'] = data['adr'] * (data['stays_in_weekend_nights'] + data['stays_in_week_nights'])

    # Grouping data by booking month and hotel type and calculating total revenue.
    total_revenue_by_month = data.groupby(['arrival_date_month', 'hotel'])['total_revenue'].sum().reset_index()

    # Checking if there is information about total revenue
    if total_revenue_by_month.empty:
        raise HTTPException(status_code=404, detail="Information about total revenue was not found")

    # Converting the results to a list of dictionaries (you can customize the output format according to your
    # requirements)
    total_revenue_by_month = total_revenue_by_month.to_dict(orient='records')

    return total_revenue_by_month


# The end point for displaying the top 5 countries with the most bookings.
@app.get("/bookings/top_countries/")
async def get_top_countries():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Grouping data by country and counting the amount bookings
    top_countries = data['country'].value_counts().head(5).reset_index()
    top_countries.columns = ['country', 'booking_count']

    # Check if there is information about the top 5 countries
    if top_countries.empty:
        raise HTTPException(status_code=404, detail="Information about the top 5 countries was not found")

    # Converting the results to a list of dictionaries (you can customize the output format according to your
    # requirements)
    top_countries_list = top_countries.to_dict(orient='records')

    return top_countries_list


# Endpoint to output the percentage of repeat guests
@app.get("/bookings/repeated_guests_percentage/")
async def get_repeated_guests_percentage():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Checking if there is information about bookings
    if data.empty:
        raise HTTPException(status_code=404, detail="Booking information not found")

    # Counting the percentage of repeat guests
    total_bookings = len(data)
    total_repeated_guests = len(data[data['is_repeated_guest'] == 1])
    repeated_guests_percentage = (total_repeated_guests / total_bookings) * 100.0

    return {"percentage": repeated_guests_percentage}


# Endpoint for displaying the total amount guests by booking year
@app.get("/bookings/total_guests_by_year/")
async def get_total_guests_by_year():
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Grouping data by booking year and counting the total amount guests.
    total_guests_by_year = data.groupby(['arrival_date_year'])[['adults', 'children', 'babies']].sum().reset_index()

    # Checking if there is information about the total amount guests.
    if total_guests_by_year.empty:
        raise HTTPException(status_code=404, detail="Information about the total number of guests was not found")

    # Converting the results to a list of dictionaries (you can customize the output format according to your
    # requirements)
    total_guests_by_year_list = total_guests_by_year.to_dict(orient='records')

    return total_guests_by_year_list


# The end point for the output of the average daily rate by a month for resort hotels.
@app.get("/bookings/avg_daily_rate_resort/")
async def get_avg_daily_rate_resort(username: str = Depends(verify_credentials)):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Filtering data to exclude cancelled bookings
    data = data[data['is_canceled'] == 0]

    # Filtering data for bookings in resort hotels
    resort_bookings = data[data['hotel'] == 'Resort Hotel']

    # Checking if there is information about bookings in resort hotels
    if resort_bookings.empty:
        raise HTTPException(status_code=404, detail="Information about bookings in resort hotels was not found")

    # Grouping data by booking month and calculating the average daily rate.
    avg_daily_rate_resort = resort_bookings.groupby(['arrival_date_month'])['adr'].mean().reset_index()

    # Converting the results to a list of dictionaries (you can customize the output format according to your
    # requirements)
    avg_daily_rate_resort_list = avg_daily_rate_resort.to_dict(orient='records')

    return avg_daily_rate_resort_list


# The endpoint for displaying the most common arrival date on the day of the week for city hotels.
@app.get("/bookings/most_common_arrival_day_city/")
async def get_most_common_arrival_day_city(username: str = Depends(verify_credentials)):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Filtering data for bookings in city hotels
    city_bookings = data[data['hotel'] == 'City Hotel']

    # Checking if there is information about bookings in city hotels
    if city_bookings.empty:
        raise HTTPException(status_code=404, detail="Information about bookings in city hotels was not found")

    # Converting a column with the arrival date to the day of the week format.
    city_bookings['arrival_date'] = pd.to_datetime(
        city_bookings['arrival_date_year'].astype(str) + '-' + city_bookings['arrival_date_month'].astype(str) + '-' +
        city_bookings['arrival_date_day_of_month'].astype(str))
    city_bookings['arrival_day_of_week'] = city_bookings['arrival_date'].dt.day_name()

    # Finding the most common arrival date on the day of the week.
    most_common_arrival_day = city_bookings['arrival_day_of_week'].mode().values[0]

    return {"most_common_arrival_day_city": most_common_arrival_day}


# Endpoint for displaying the amount bookings by hotel type and meal package.
@app.get("/bookings/count_by_hotel_meal/")
async def get_count_by_hotel_meal(username: str = Depends(verify_credentials)):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Grouping data by hotel type and meal package and counting the amount bookings.
    count_by_hotel_meal = data.groupby(['hotel', 'meal']).size().reset_index(name='count')

    # Checking if there is information about the amount bookings
    if count_by_hotel_meal.empty:
        raise HTTPException(status_code=404, detail="Information about the number of bookings was not found")

    # Converting the results to a list of dictionaries
    count_by_hotel_meal_list = count_by_hotel_meal.to_dict(orient='records')

    return count_by_hotel_meal_list


# The end point for the output of total revenue from booking resort hotels by country.
@app.get("/bookings/total_revenue_resort_by_country/")
async def get_total_revenue_resort_by_country(username: str = Depends(verify_credentials)):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Filtering data to exclude cancelled bookings
    data = data[data['is_canceled'] == 0]

    # Filtering data for bookings in resort hotels
    resort_bookings = data[data['hotel'] == 'Resort Hotel']

    # Checking if there is information about bookings in resort hotels
    if resort_bookings.empty:
        raise HTTPException(status_code=404, detail="Information about bookings in resort hotels was not found")

    # Grouping data by country and calculating total revenue
    total_revenue_resort_by_country = resort_bookings.groupby(['country'])['adr'].sum().reset_index(
        name='total_revenue')

    # Checking if there is information about revenue by country
    if total_revenue_resort_by_country.empty:
        raise HTTPException(status_code=404,
                            detail="Information on revenue from booking resort hotels by country was not found")

    # Converting results to a dictionary list
    total_revenue_resort_by_country_list = total_revenue_resort_by_country.to_dict(orient='records')

    return total_revenue_resort_by_country_list


# Endpoint for displaying the amount bookings by hotel type and repeat guest status.
@app.get("/bookings/count_by_hotel_repeated_guest/")
async def get_count_by_hotel_repeated_guest(username: str = Depends(verify_credentials)):
    # Loading data from a CSV file
    data = load_data("../hotel_booking_data.csv")

    # Checking if there is information about bookings
    if data.empty:
        raise HTTPException(status_code=404, detail="Booking information not found")

    # Grouping data by hotel type and repeat guest status and counting the amount bookings.
    count_by_hotel_repeated_guest = data.groupby(['hotel', 'is_repeated_guest']).size().reset_index(name='count')

    # Checking if there is information about the amount bookings
    if count_by_hotel_repeated_guest.empty:
        raise HTTPException(status_code=404, detail="Information about the number of bookings was not found")

    # Converting results to a dictionary list
    count_by_hotel_repeated_guest_list = count_by_hotel_repeated_guest.to_dict(orient='records')

    return count_by_hotel_repeated_guest_list
