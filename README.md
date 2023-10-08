# Skyproduct Django App

![CI Workflow](https://github.com/antibagr/skypro.interview.django.products/actions/workflows/makefile.yml/badge.svg?event=push)![coverage badge](./coverage.svg)

The "Skyproduct" Django app is a powerful e-commerce solution designed to manage and display product data efficiently. It provides a comprehensive database for storing product information and offers insightful data analytics for sales. With built-in authentication and deployment using Nginx, Gunicorn, and Unicorn, Skyproduct ensures a secure and high-performance environment for your e-commerce needs.

## Table of Contents

- [Skyproduct Django App](#skyproduct-django-app)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
    - [Product Database](#product-database)
    - [Aggregated Product Table](#aggregated-product-table)
    - [Monthly Sales Analytics](#monthly-sales-analytics)
    - [User Authentication](#user-authentication)
    - [Deployment with Nginx, Gunicorn, and Unicorn](#deployment-with-nginx-gunicorn-and-unicorn)
  - [Installation](#installation)
    - [Poetry](#poetry)
    - [Dependencies](#dependencies)
    - [Enviroment variables](#enviroment-variables)
    - [Migrate](#migrate)
    - [Populate initial data (Optional)](#populate-initial-data-optional)
    - [Run](#run)
      - [Dev](#dev)
      - [Production](#production)
  - [Usage](#usage)
  - [Development](#development)
    - [Linting](#linting)
    - [Running the Server](#running-the-server)
    - [Docker Compose](#docker-compose)
  - [Testing](#testing)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
    - [All Tests](#all-tests)
  - [License](#license)

## Features

### Product Database

Skyproduct comes equipped with a robust product database that allows you to store detailed information about your products. Each product can have attributes like name, description, price, and category, ensuring that you can efficiently manage your product catalog.

### Aggregated Product Table

Skyproduct simplifies the process of monitoring your product sales by providing an aggregated product table. This table displays a summary of essential product information, including name, category, and aggregated sales data. This feature allows you to gain quick insights into your product performance.

### Monthly Sales Analytics

Keeping track of your sales trends is crucial for making informed business decisions. Skyproduct offers two distinct views for sales analytics:

1.  **Last Month Aggregated Sales:** Skyproduct compiles data from the previous month to give you an overview of how your products performed in the past.

2.  **Current Month Aggregated Sales:** Stay up-to-date with your sales in real-time. Skyproduct calculates and displays the sales data for the current month, helping you make timely adjustments to your business strategy.

### User Authentication

Skyproduct includes a robust user authentication system, ensuring that only authorized personnel can access sensitive areas of your e-commerce platform. This feature provides peace of mind and protects your valuable data.

### Deployment with Nginx, Gunicorn, and Unicorn

Skyproduct is ready for production deployment, thanks to its integration with Nginx, Gunicorn, and Unicorn. This stack ensures high performance, availability, and high-load resistance for your e-commerce website.

## Installation

> **Note for Windows Users:**
>
> If you are using Windows, it's important to ensure that you have Windows Subsystem for Linux (WSL) 2 installed and configured correctly before running the provided commands under a WSL terminal. WSL 2 provides a Linux-compatible environment that can be used for development tasks.
>
> To install and set up WSL 2 on your Windows machine, please follow the official Microsoft documentation: [Install Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install).
>
> Once WSL 2 is set up, make sure to use the WSL terminal for running the commands specified in this documentation for a seamless development experience.
>
> If you encounter any issues related to WSL or need further assistance, please refer to the Microsoft WSL documentation or seek support from the WSL community.


### Poetry

Install poetry using your package manager or [official guide](https://python-poetry.org/docs/#installation). (Project was maintained mostly with `1.6.1`)

### Dependencies

The easiest way to install required and dev dependencies is as follows:

```bash
make install
```

### Enviroment variables

| Environment Variable   | Description                                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| SECRET_KEY             | Django's secret key used for cryptographic functions. Keep this value secret and secure.            |
| DJANGO_ALLOWED_HOSTS   | A list of allowed hostnames or IP addresses that can access the Django application.                 |
| DJANGO_INTERNAL_IPS    | A list of your local machine IP addresses used by Django debug toolbar (not required in production) |
| DJANGO_SETTINGS_MODULE | Specifies the Django settings module to be used. Typically set to the development settings.         |
| DB_ENGINE              | Specifies the database engine to be used, in this case, PostgreSQL.                                 |
| DB_DATABASE            | The name of the PostgreSQL database for the Django application.                                     |
| DB_USER                | The username used to connect to the PostgreSQL database.                                            |
| DB_PASSWORD            | The password used to authenticate the PostgreSQL database user.                                     |
| DB_HOST                | The hostname of the PostgreSQL database server.                                                     |
| DB_PORT                | The port number to connect to the PostgreSQL database server.                                       |
| DB_NAME                | An alternative database name, typically set to 'postgres' for PostgreSQL configurations.            |
| DATABASE               | An alias for the 'DB_NAME' environment variable, used in Django settings.                           |
| NGINX_PORT             | The port number on which the Nginx web server should listen.                                        |
| REDIS_BACKEND          | The connection URL for the Redis cache backend, specifying the Redis server and port to use.        |

1.  **Create a `.env` File:**

    -   Create a `.env` file in the root directory of your project if it doesn't already exist.

2.  **Open the `.env` File:**

    -   Open the `.env` file using a text editor of your choice.

3.  **Define Environment Variables:**

    -   Inside the `.env` file, define the following environment variables, providing values specific to your project:

        ```env
        SECRET_KEY=django-secure-chw!h4ulgqj4=agc%@yhi9fj8^4sqn2gbiq38!!e+fact9f-7
        DJANGO_ALLOWED_HOSTS='localhost 127.0.0.1 [::1]'
        DJANGO_INTERNAL_IPS='localhost 127.0.0.1 [::1]'
        DJANGO_SETTINGS_MODULE=api.settings.development
        DB_ENGINE=django.db.backends.postgresql
        DB_DATABASE=hello_django_dev
        DB_USER=hello_django
        DB_PASSWORD=hello_django
        DB_HOST=db
        DB_PORT=5432
        DB_NAME=postgres
        DATABASE=postgres
        NGINX_PORT=8888
        REDIS_BACKEND=redis://redis:6379/0
        ```

    -   Replace the values in the above example with your specific configuration.

4.  **Save the `.env` File:**

    -   Save the changes to the `.env` file.

### Migrate

To create all the neccessary tables and migrations, run:

```bash
make db_update
```

### Populate initial data (Optional)

To populate the database with initial data, follow these steps:

1.  Open your terminal or command prompt.

2.  Navigate to the project directory where your Django app is located.

3.  Run the following command to access the Django management script:

```bash
make shell
```

In the Django management shell, type the following command to import the required tools:

```python
from app.common.populate import populate_async, populate_threads, Settings
```

Now, you can use either populate_async() or populate_threads() function to populate your database with initial data (no configuration required):

```python
populate_async()
# or
populate_threads()
```

You can also fine-tune the process with custom settings:

```python
settings = Settings(
    categories_count=10,
    products_per_category_count=10,
    customers_count=10,
    carts_per_customer_count=10,
    cart_items_per_cart_count=10,
)
```

Run populate_threads:

```python
populate_threads(settings, threads_count=4)
```

Or run populate_async:

```python
populate_async(settings, tasks_count=4)
```

> **Note:**
> 
> You can use both the `populate_threads` and `populate_async` functions interchangeably.
> However, it is recommended to use `populate_async` for small amounts of data and `populate_threads` for more substantial batch processing, capable of handling up to millions of items efficiently.

### Run

#### Dev

To run development server run:

```bash
make run
```

Now you can check your [localhost:8888](http://localhost:8888)

#### Production

To run production server on the local machine:

1.  Install Docker Compose following the [official guide](https://docs.docker.com/compose/install/).
2.  Build and run all containers locally:

```bash
make compose-up
```

Now you can check your [localhost:8000](http://localhost:8000)

## Usage

Describe how to use your app here.

## Development

Formatting
To format the source code, run:

```bash
make format
```

### Linting

To lint the source code, run:

```bash
make lint
```

### Running the Server

To run the development Django server, use:

```bash
make run
```

### Docker Compose

To run the development Django server with Docker Compose, use:

```bash
make compose-up
```

To stop the development Django server with Docker Compose, use:

```bash
make compose-down
```

## Testing

### Unit Tests

To run unit tests, use:

```bash
make tests-units
```

### Integration Tests

To run integration tests, use:

```bash
make tests-integrations
```

### All Tests

To run all available tests, use:

```bash
make test
```

## License

This project is licensed under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/) License - see the [LICENSE](./LICENCE) file for details.