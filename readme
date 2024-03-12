# Delectric Charging Station App Microservices

This repository contains a Docker Compose setup for a Flask-based Charging Station microservice connected to a MySQL database. Below are instructions on how to run the application locally.

## Prerequisites

Make sure you have the following installed on your machine:

- Docker
- Docker Compose

## Setup

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/your-username/delectric-charging-station.git
    cd delectric-charging-station
    ```

2. Create a `.env` file in the root directory and set the required environment variables:

    ```plaintext
    DB_PASSWORD=mypassword #Root password
    DB_USER=myuser
    DB_USER_PASSWORD=userpassword
    ```

   Update the values accordingly.

Note: Make sure no conflicting ports (check compose.yaml)

## Running the Application

Use the following commands to build and run the application:

```bash
docker-compose up --build
```
or
Run in detach mode
```bash
docker-compose up -d
```
This command will build the Docker images and start the services defined in the docker-compose.yml file.

## Accessing the Application
- The Charging Station microservice will be available at http://localhost:5001.
- MySQL database will be accessible at localhost:3306. You can use a database client or any preferred tool to connect to it using the provided credentials.

## Stopping the Application
To stop the running containers, use the following command:
```bash
docker-compose down
```
This command will stop and remove the containers, networks, and volumes defined in the docker-compose.yml file.

