#!/bin/bash

# Function to delete all routes associated with a service in Kong
delete_routes() {
    local service_id=$1
    local route_ids=$(curl -s http://localhost:8001/services/$service_id/routes | jq -r '.data[].id')
    for route_id in $route_ids; do
        curl -i -X DELETE http://localhost:8001/routes/$route_id
    done
}

# Function to delete all services in Kong
delete_services() {
    local service_ids=$(curl -s http://localhost:8001/services/ | jq -r '.data[].id')
    for service_id in $service_ids; do
        delete_routes $service_id
        curl -i -X DELETE http://localhost:8001/services/$service_id
    done
}

# Delete all services and routes
delete_services