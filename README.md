# AgroMart Backend (Django)

This repository contains the **Django-based backend** for **AgroMart**, migrated from an original Go implementation.  
The new backend fully replicates the core functionality of the Go application, including **authentication**, **product management**, **orders**, and **AI chatbot integration**.

---

## 🚀 Migration Overview

The backend was successfully migrated from **Go** to **Django + Django Rest Framework (DRF)** while preserving all existing business logic and API behavior.

### ✅ Features Migrated
- User authentication (signup, login, logout)
- Product and category management
- Order processing and statistics
- Reviews system
- Seller profile information
- Chatbot integration (via local Ollama)

---

## 🏗️ Project Structure

backend_django/
│
├── agromart/ # Django project settings
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── api/ # Main application
│ ├── models.py # Database models
│ ├── views.py # API logic
│ ├── urls.py # API routes
│ └── serializers.py
│
├── db.sqlite3 # SQLite database
├── manage.py
├── requirements.txt
├── test_api.py # API verification script
└── README.md

yaml
Copy code

---

## ⚙️ Tech Stack

- **Backend Framework:** Django  
- **API:** Django Rest Framework (DRF)  
- **Database:** SQLite (default)  
- **Authentication:** Django `AbstractUser`  
- **CORS:** `django-cors-headers`  
- **AI Chatbot:** Ollama (local integration)  

---

## 📦 Models

All original Go structs were replicated as Django models inside `api/models.py`:

- `User` (extends `AbstractUser`)
- `Product`
- `ProductCategory`
- `Order`
- `Review`
- `SellerAbout`

---

## 🔌 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description |
|------|----------|-------------|
| POST | `/signup` | Register user |
| POST | `/login` | Login user |
| POST | `/logout` | Logout user |

### 👤 Users
| Method | Endpoint |
|------|----------|
| GET | `/users/` |

### 📦 Products
| Method | Endpoint | Notes |
|------|----------|-------|
| GET/POST | `/products/` | Supports user filtering & search |

### 🗂️ Categories
| Method | Endpoint |
|------|----------|
| GET/POST | `/category/` |

### 🛒 Orders
| Method | Endpoint |
|------|----------|
| GET/POST | `/order/` |
| GET | `/order/seller-stats/` |
| GET | `/order/monthly-stats/` |

### ⭐ Reviews
| Method | Endpoint |
|------|----------|
| GET/POST | `/review/` |

### 🤖 Chatbot
| Method | Endpoint |
|------|----------|
| POST | `/api/chatbot` |

> ⚠️ Chatbot requires **Ollama running locally**

---

## ✅ Verification Status

API was tested using `test_api.py`.

| Feature | Status |
|------|--------|
| Signup | ✅ Successful |
| Login | ✅ Successful |
| Chatbot | ⚠️ Failed (Ollama not running) |

---

## ▶️ How to Run Locally

### 1. Navigate to project directory
```bash
cd backend_django
2. Install dependencies

pip install -r requirements.txt
3. Apply migrations

python manage.py migrate
4. Start the development server

python manage.py runserver
5. Run API tests

python test_api.py

##👨‍💻 Author

Victor Kiplangat
Backend migration from Go to Django

📜 License

This project is for educational and development purposes.
A license can be added if required.