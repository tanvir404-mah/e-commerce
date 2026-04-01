# 🛒 NexGen - Professional Full-Stack E-commerce Platform

**NexGen** is a high-performance, feature-rich e-commerce solution built with **Django** and **Tailwind CSS**. It is designed to provide a seamless shopping experience for users while offering a powerful, data-driven administrative dashboard for business owners.

## 🚀 Key Features

### 👤 User Experience (Frontend)
* **Dynamic Product Discovery:** Search, filter by category, and sort products with ease.
* **Wishlist & Cart:** Save favorite items for later and manage a persistent shopping cart.
* **Smart Checkout:** Multiple shipping address support and dynamic delivery charge calculation.
* **Coupon System:** Real-time discount application via promo codes.
* **Verified Reviews:** 1-5 star rating system with moderated customer feedback.
* **Order Tracking:** Live status updates (Processing → Shipped → Delivered).
* **User Dashboard:** Manage profile, address book, and view order history.

### 🛡️ Admin Powerhouse (Backend)
* **Advanced Analytics:** Sales charts (Chart.js), revenue tracking, and order statistics.
* **Inventory Control:** Low-stock alerts and automated stock management.
* **Marketing Tools:** Dynamic homepage banners and flash sale management.
* **Order Fulfillment:** Professional invoice generation using print media queries.
* **Moderation:** Approve/Reject customer reviews and manage user access levels.

## 🛠️ Tech Stack
* **Backend:** Python, Django 5.0+
* **Frontend:** Tailwind CSS, JavaScript (Alpine.js/Vanilla)
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Visuals:** Chart.js

## 📦 Installation & Setup

1. **Clone the repository:**
 
   git clone https://github.com/tanvir404-mah/e-commerce.git
   cd e-commerce

2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Database Migration:
python manage.py makemigrations
python manage.py migrate

5.Create a Superuser:
python manage.py createsuperuser

6.Run the server:
python manage.py runserver
Visit http://127.0.0.1:8000/ to view the shop!
   
