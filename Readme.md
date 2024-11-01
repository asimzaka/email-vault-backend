# Project Setup and Running with Docker Compose

This project uses Docker Compose to manage and run its services, which include RabbitMQ, MySQL, an email transmitter, and a Flask application. Follow these steps to configure and start the project.

## Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Step 1: Environment Variables
The project requires environment variables to be configured in two files:
1. **`.env.secrets`** - This file holds sensitive data (e.g., passwords, tokens) that should not be committed to version control.
2. **`local.env`** - This file contains environment-specific values for local development (e.g., RabbitMQ host, MySQL user).

### Step 2: Set Up Environment Files
1. Copy **`.env.example.secrets`** into **`.env.secrets`** and update variables
2. **`APP_ENV`** in **`.env.secrets`** will determine the file name if **`APP_ENV=local`** then other variables will be in file: **`local.env`**
3. if you change APP_ENV=local then copy local.env to new file

### For Example 
```
APP_ENV=test # Defined in .env.secrets

Other file name will be: test.env

Copy all local.env variables to test.env

```

4. Update the docker-compose.yaml file to pick env variable from correct file.

### For Example to use test.env

```
    rabbitmq:
      env_file:
        - local.env # Change it to test.env
        - .env.secrets
    email-transmitter:
      env_file:
        - local.env # Change it to test.env
        - .env.secrets
    mysqldb:
      env_file:
        - local.env # Change it to test.env
        - .env.secrets

```

### Step 3: Run Docker Compose
Start all services using Docker Compose:
```bash
docker-compose up --build

```