#!/bin/bash

# Function to create a service in Kong
create_service() {
    local name=$1
    local url=$2
    curl -i -X POST --url http://localhost:8001/services/ --data "name=$name" --data "url=$url"
}

# Function to create a route for a service in Kong
create_route() {
    local service_name=$1
    local path=$2
    local name=$3
    local methods=$4
    curl -i -X POST --url http://localhost:8001/services/$service_name/routes --data "name=$name" --data "paths[]=$path" "methods[]=$methods"
}

# Create endpoints for each API

# # 5101 COMPLEX - Handle Bookings
# create_service "getbookingbyuserapi" "http://delectric-complex-handle-bookings:5101/booking-complex/user"
# create_route "getbookingbyuserapi" "/booking-complex/user" "getbookingbyuserapi" "GET"

# # 5102 COMPLEX - Handle End Booking
# create_service "endbookingapi" "http://delectric-book_charger:5102/book-charger-complex/complete-booking"
# create_route "endbookingapi" "/book-charger-complex/complete-booking" "endbooking" "POST"

# # 5102 COMPLEX - Handle Cancel Booking
# create_service "cancelbookingapi" "http://delectric-book_charger:5102/book-charger-complex/cancel-booking"
# create_route "cancelbookingapi" "/book-charger-complex/cancel-booking" "cancelbookingapi" "POST"

# # 5102 COMPLEX - Handle Create Booking
# create_service "createbookingapi" "http://delectric-book_charger:5102/book-charger-complex/book-charger"
# create_route "createbookingapi" "/book-charger-complex/book-charger" "createbookingapi" "POST"

# # 5101 COMPLEX - Handle Create Booking
# create_service "createbookingapi" "http://delectric-book_charger:5102/book-charger-complex/book-charger"
# create_route "createbookingapi" "/book-charger-complex/book-charger" "createbookingapi" "POST"

# # 5001 SIMPLE - Get Nearby Booking (Filter by Avail)
# create_service "nearbychargingstationapi" "http://delectric-charging-station:5001/charging-station/nearby_stations_booking"
# create_route "nearbychargingstationapi" "/charging-station/nearby_stations_booking" "nearbychargingstationapi" "POST"

# 5001 SIMPLE - Get Nearby Chargers (No filter)
create_service "nearbychargingstationallapi" "http://delectric-charging-station:5001/charging-station/nearby-chargers"
create_route "nearbychargingstationallapi" "/charging-station/nearby-chargers" "nearbychargingstationallapi" "POST"

# # 5001 SIMPLE - Get Chargers 
# create_service "getchargingstationapi" "http://delectric-charging-station:5001/charging-station/chargers"
# create_route "getchargingstationapi" "/charging-station/chargers" "getchargingstationapi" "POST"

# # 5001 SIMPLE - Get Charging Station Booking 
# create_service "getbookingchargingstationapi" "http://delectric-charging-station:5001/charging-station-booking/charger"
# create_route "getbookingchargingstationapi" "/charging-station-booking/charger" "getbookingchargingstationapi" "GET"