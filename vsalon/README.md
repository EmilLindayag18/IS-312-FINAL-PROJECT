# VSalon - Salon Management System

A complete Python Flask web application for salon management with MySQL database (XAMPP compatible).

## Features

### Customer Features
- ✅ Register, Login, Profile Management
- ✅ Book, Reschedule, Cancel Appointments
- ✅ Service Selection with Staff Preference
- ✅ View Upcoming & Past Bookings
- ✅ Shop Products Online
- ✅ CRM - Service History & Preferences

### Admin Features
- ✅ Secure Admin Login (RBAC)
- ✅ Dashboard with Sales & Appointment Overview
- ✅ Appointment Management & Staff Assignment
- ✅ Staff Management & Scheduling
- ✅ Inventory Management with Low-Stock Alerts
- ✅ Product Management (Shop CRUD)
- ✅ POS & Sales Monitoring
- ✅ Reports & Analytics
- ✅ Service Management

## Setup Instructions

### 1. Prerequisites
- Python 3.8+ installed
- XAMPP installed and running (Apache + MySQL)

### 2. Create the Database
1. Start XAMPP → Start **Apache** and **MySQL**
2. Open phpMyAdmin: http://localhost/phpmyadmin
3. Click **Import** → Choose `database.sql` → Click **Go**

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

> **Note (Windows):** You may need to install `mysqlclient` separately:
> ```bash
> pip install mysqlclient
> ```
> If it fails, download the wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Go to: **http://localhost:5000**

## Default Admin Account
- **Email:** admin@vsalon.com
- **Password:** admin123

> ⚠️ After importing the database, you need to update the admin password hash.
> Run this once in Python:
> ```python
> from werkzeug.security import generate_password_hash
> print(generate_password_hash('admin123'))
> ```
> Then update the admin record in phpMyAdmin with the generated hash.

## Project Structure
```
vsalon/
├── app.py                  # Main Flask application (all routes)
├── database.sql            # MySQL database schema + sample data
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── static/
│   └── css/
│       └── style.css      # Complete CSS design system
└── templates/
    ├── base.html           # Public page layout
    ├── homepage.html       # Landing page
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── services.html       # Services listing
    ├── shop.html           # Product shop
    ├── about.html          # About page
    ├── admin/
    │   ├── base_admin.html # Admin layout with sidebar
    │   ├── dashboard.html  # Admin dashboard
    │   ├── appointments.html
    │   ├── staff.html
    │   ├── services.html
    │   ├── products.html
    │   ├── inventory.html
    │   ├── pos.html
    │   └── reports.html
    └── customer/
        ├── base_customer.html # Customer layout with sidebar
        ├── dashboard.html
        ├── book_appointment.html
        ├── appointments.html
        ├── reschedule.html
        └── profile.html
```

## Pages Summary

| Page | URL | Description |
|------|-----|-------------|
| Homepage | `/` | Landing page with services & products |
| Login | `/login` | User authentication |
| Register | `/register` | New customer registration |
| Services | `/services` | Browse all services |
| Shop | `/shop` | Browse & buy products |
| About | `/about` | About VSalon |
| Customer Dashboard | `/customer/dashboard` | Customer overview |
| Book Appointment | `/customer/book` | Book new appointment |
| My Appointments | `/customer/appointments` | View all appointments |
| Profile | `/customer/profile` | Edit profile + CRM history |
| Admin Dashboard | `/admin/dashboard` | Admin overview + stats |
| Manage Appointments | `/admin/appointments` | Update bookings, assign staff |
| Manage Staff | `/admin/staff` | Add/manage staff members |
| Manage Services | `/admin/services` | Add/manage services |
| Manage Products | `/admin/products` | Product CRUD |
| Inventory | `/admin/inventory` | Stock levels + alerts |
| POS | `/admin/pos` | Point of sale transactions |
| Reports | `/admin/reports` | Sales & performance analytics |

## IDE Support
- ✅ VS Code
- ✅ PyCharm
- ✅ Any Python IDE

## Deployment
Can be deployed on:
- PythonAnywhere
- Railway
- Render
- Heroku
- Any VPS with Python + MySQL
