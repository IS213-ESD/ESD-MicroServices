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

# Charging-Stations-Service
create_service "charging-stations-service" "http://delectric-charging-station:5001/chargers"
create_route "charging-stations-service" "/charging-stations/charger" "get_all_charging_stations" "GET"

# Nearby
create_service "nearby-charging-stations-service" "http://delectric-charging-station:5001/nearby_stations_booking"
create_route "nearby-charging-stations-service" "/charging-stations/nearby-chargers" "get_nearby_charging_stations" "POST"

# Add more services and routes as needed for other APIs
# create_service "other-service" "http://localhost:5002"``
# create_route "other-service" "/other-endpoint"

# Add more APIs as needed
