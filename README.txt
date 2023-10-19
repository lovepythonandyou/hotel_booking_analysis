Project name:
API for Hotel booking analysis

Project Description:
The Hotel Booking Analysis API is designed to provide a complete set of endpoints for analyzing and extracting
information from a dataset containing information about booking a city hotel and a resort hotel. The dataset includes
various attributes such as booking dates, length of stay, amount guests, parking availability, pricing information,
arrival dates, guest nationality, repeat guest status, meal package, and more.

Installation:
All dependencies are placed in a file requirements.txt
pip3 install -r requirements.txt (for windows)

To work with the program, you need to run the main file, go to http://127.0.0.1:8000 (it may differ for you) and on the
page in the browser in the address bar, enter http://127.0.0.1:8000/docs
Then you can use the service.

API Endpoints:
1 URL: /bookings: Retrieves a list of all bookings in the dataset.
2 URL: /bookings/{booking_id}: Retrieves detailed information about a particular booking by its unique identifier.
3 URL: /bookings/search: Allows you to search for bookings based on various parameters, such as the guest's name,
booking dates, length of stay, etc.
4 URL:/bookings/stats: Provides statistical information about the dataset, such as total amount bookings,
average length of stay, average daily rate, etc.
5 URL: /bookings/analysis: Performs advanced data set analysis, generating information and trends based on certain
criteria, such as booking trends by a month, guest demographics, popular meal packages, etc.
More advanced functionality
6 URL: /bookings/nationality
Description: Retrieves orders based on the specified nationality. Parameters: Nationality (str): The nationality for
which you need to receive orders. Returned: Reservations corresponding to the specified nationality.
7 URL: /bookings/popular_meal_package
Description: Extracts the most popular meal package among all bookings. Returns: The most popular package with food.
8 URL: / bookings/avg_length_of_stay
Description: Extracts the average length of stay grouped by booking year and hotel type. Returns: Average length of
stay for each combination of booking year and hotel type.
9 URL: / bookings/total_revenue
Description: Extracts total revenue grouped by booking month and hotel type. Returns: Total revenue for each
combination of booking month and hotel type.
10 URL: /bookings/top_countries
Description: Displays the top 5 countries with the largest number of bookings. Returns: Top 5 countries with the
most bookings.
11 URL: /bookings/repeated_guests_percentage
Description: Extracts the percentage of repeat guests among all bookings. Returns: Percentage of repeat guests.
12 URL: /booking/total_guests_by_year
Description: Returns the total amount guests (adults, children, and infants) by a year of booking. Returns: Total
amount guests by a year of booking.
13 URL: / reservations/avg_daily_rate_resort
Description: Extracts the average daily rate by a month for bookings in resort hotels. Returns: The average daily rate
by a month when booking resort hotels.
14 URL: /reservations/most_common_arrival_day_city
Description: Extracts the most common arrival date on the day of the week when booking hotels in the city. Returns:
The most common arrival date on the day of the week when booking city hotels.
15 URL: / reservations/count_by_hotel_meal
Description: Retrieves the amount bookings grouped by hotel type and meal package. Returns: The amount bookings
depending on the type of hotel and the package of meals.
16 URL: /bookings/total_revenue_resort_by_country
Description: Extracts the total revenue from booking resort hotels by country. Returns: Total revenue from booking
resort hotels by country.
17 URL: /bookings/count_by_hotel_repeated_guest Amount repeat guests
Description: Retrieves the amount bookings grouped by hotel type and repeat guest status. Returns: The amount
bookings broken down by hotel type and repeat guest status.
18 URL: "/upload-csv/"
Description: Allows you to upload files to work with them.

Acknowledgements:
special thanks for the project and feedback to my curators @Arman_Deghoyan and Roman.