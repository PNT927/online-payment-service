# Online Payment Service

A full-stack web application developed using Django that allows users to securely send and request payments through a web-based interface. The system includes user account management, transaction tracking, notifications, administrative tools, and a REST API for currency conversion.

This project was developed as part of a university module and was later extended with PostgreSQL, Docker, environment variable configuration, and AWS deployment experience.

## Tech Stack

* Python
* Django
* PostgreSQL
* Docker & Docker Compose
* HTML
* CSS
* Bootstrap
* JavaScript
* AWS EC2

## Key Features

### User Features

* User registration and authentication
* Secure login and logout
* Dashboard displaying account balance and notifications
* Send payments to other users
* Request payments from other users
* View transaction history
* Manage account information

### Administrator Features

* View and manage user accounts
* Monitor all transactions
* Create administrator accounts
* Delete user accounts

### Security Features

* Django Authentication system
* Password hashing
* CSRF protection
* XSS protection
* SQL injection prevention through Django ORM
* HTTPS support using SSL certificates

### API Features

* REST API for currency conversion
* JSON-based responses
* Multi-currency support

## Database

The application uses PostgreSQL to store:

* User accounts
* Transactions
* Payment requests
* Notifications

## Docker Support

The application has been containerised using Docker and Docker Compose, allowing both the Django application and PostgreSQL database to be started using a single command.

## Running the Project

Clone the repository:

```bash
git clone https://github.com/PNT927/online-payment-service.git
```

Navigate to the project directory:

```bash
cd online-payment-service
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000
```

## Future Improvements

* Email notifications for payment requests and transactions
* Improved user interface and responsive design
* Additional API endpoints
* Automated testing and CI/CD pipeline

## Author

Philip Tagoe Jr


