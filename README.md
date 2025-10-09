# Backend-Lawtabby

A Django backend project supporting authentication (Google, Apple, Microsoft), payments (Stripe, PayPal), PDF handling, and chat functionality.

## Features

- User authentication (email/password, Google, Apple, Microsoft)
- REST API with Django REST Framework
- Payment integration (Stripe, PayPal)
- PDF processing
- Chat module
- Docker support

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <repo-url>
cd Backend-ChatGPT
```

### 2. Install Python 3.11

```sh
brew install python@3.11
```

### 3. Create and Activate Virtual Environment

```sh
python3.11 -m venv venv
source venv/bin/activate
```

### 4. Install Requirements

If you need to create a requirements file:

```sh
pip freeze > requirements.txt
```

To install requirements:

```sh
pip install -r requirements.txt
```

### 5. Generate Django Secret Key

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Run Migrations

```sh
python manage.py makemigrations
python manage.py migrate
```

### 7. Start Development Server

```sh
python manage.py runserver
```



#create requirement file
pip freeze > requirements.txt
install requirement
pip install requirements.txt
python manage.py runserver


brew install python@3.11
python3.11 -m venv venv

For generating the Scret key

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


# create db in postgres

psql -d postgres
psql -h localhost -U postgres
or
psql -U postgres
CREATE DATABASE legal_ai_db;

brew list | grep postgresql

brew services stop postgresql
brew services stop postgresql@14

-- 1️⃣ Create a new database user (role) for Django
CREATE ROLE legal_ai_user1 WITH LOGIN PASSWORD 'legal_ai_pass1';

-- 2️⃣ Create the database your project will use
CREATE DATABASE legal_ai_db OWNER legal_ai_user1;

-- 3️⃣ (Optional) Grant all privileges explicitly
GRANT ALL PRIVILEGES ON DATABASE legal_ai_db TO legal_ai_user;

-- 4️⃣ Verify users and databases
\du
\l

