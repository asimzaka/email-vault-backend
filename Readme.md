# Project Setup and Running with Docker Compose

This project uses Docker Compose to manage and run its services, which include RabbitMQ, MySQL, an email transmitter, and a Flask application. Follow these steps to configure and start the project.

## Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Step 1: Environment Variables
The project requires environment variables to be configured in two files:
1. **`local.env`** - This file contains environment-specific values for local development (e.g., RabbitMQ host, MySQL user).
2. **`.env.secrets`** - This file holds sensitive data (e.g., passwords, tokens) that should not be committed to version control.

### Step 2: Set Up Environment Files
1. Create a `local.env` file with the following structure and customize values for your environment:
    ```env
    MYSQL_USER=user
    MYSQL_PASSWORD=password
    MYSQL_DATABASE=email_vault_db
    QUEUE_NAME_PREFIX=email_queue_
    FLASK_ENV=local
    ```
2. Create a `.env.secrets` file containing sensitive values. An example structure for this file should include:
    ```env
    SECRET_KEY=your_secret_key
    RABBITMQ_USER=rabbitmq_user
    RABBITMQ_PASSWORD=rabbitmq_password
    ```

3. For sharing environment variable names (without values) with others, create a `.env.secrets.example` file in your repository:
    ```env
    SECRET_KEY=
    RABBITMQ_USER=
    RABBITMQ_PASSWORD=
    ```

### Step 3: Run Docker Compose
Start all services using Docker Compose:
```bash
docker-compose up --build
