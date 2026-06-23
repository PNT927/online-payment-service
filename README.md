# Online Payment Service

## Overview

This project was developed as part of the Web Applications and Services module at the University of Sussex.

The aim of the project was to create a secure online payment service where users can send payments, request payments from other users, and manage their accounts through a web-based interface. The application was built using Django and PostgreSQL and follows a multi-layered architecture consisting of presentation, business logic, data access, security, and web service layers.

## Features

### User Features

* User registration and login
* Dashboard showing account balance and notifications
* Send payments to other users
* Request payments from other users
* View transaction history
* Profile page displaying account information

### Administrator Features

* View all user accounts
* View all transactions
* Create administrator accounts
* Delete user accounts

### Security Features

* User authentication using Django Authentication
* Password hashing
* CSRF protection
* XSS protection
* SQL injection protection through Django ORM
* HTTPS support using SSL certificates

### Web Services

* REST API for currency conversion
* JSON responses
* Support for multiple currencies

## Technologies Used

* Python
* Django
* PostgreSQL
* Docker
* HTML
* CSS
* Bootstrap
* JavaScript

## Database

The application uses PostgreSQL to store account information, transactions, payment requests and notifications.

## Docker Support

The application has been containerised using Docker and Docker Compose. This allows the application and database to be started with a single command.

## Running the Project

1. Clone the repository

```bash
git clone <repository-url>
```

2. Navigate to the project folder

```bash
cd webapps2026
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Run migrations

```bash
python manage.py migrate
```

5. Start the development server

```bash
python manage.py runserver
```

6. Open the application

```text
http://127.0.0.1:8000
```

## Author

Philip Tagoe Jr

University of Sussex

Computer Science
