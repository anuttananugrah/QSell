# Qsell - Premium Marketplace Platform

Qsell is a modern, high-performance marketplace platform built with Django. It enables users to list, discover, and trade products with ease, featuring integrated chat, wishlist management, and secure payment processing.

## 🚀 Features

- **User Authentication**: Secure signup/login with customizable user profiles.
- **Product Management**: Dynamic product listings with category filtering and search.
- **Real-time Chat**: Integrated messaging system for buyers and sellers.
- **Wishlist**: Users can save products for later.
- **Payment Processing**: Integrated with **Razorpay** for secure transactions.
- **Admin Dashboard**: Custom administrative tools for managing reports, users, and listings.
- **Cloud Media**: Permanent image storage powered by **Cloudinary**.
- **Modern UI**: Fully responsive design with a focus on user experience.

## 🛠️ Tech Stack

- **Backend**: Django 6.0 (Python)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Image Hosting**: Cloudinary
- **Static Assets**: WhiteNoise (Compressed & Cached)
- **Payments**: Razorpay
- **Security**: Environment variable management via `python-decouple`
- **Deployment**: Optimized for Render

## ⚙️ Local Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd qsell
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your credentials:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=sqlite:///db.sqlite3
    CLOUD_NAME=your_cloudinary_name
    API_KEY=your_cloudinary_key
    API_SECRET=your_cloudinary_secret
    RAZORPAY_KEY_ID=your_key
    RAZORPAY_KEY_SECRET=your_secret
    ```

5.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Start the server**:
    ```bash
    python manage.py runserver
    ```

## 🌐 Deployment

This project is configured for one-click deployment on **Render**.

- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn rehub.wsgi`

---
*Created with ❤️ by [Your Name/GitHub]*
