from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='admin_panel/admin_login.html'), name='admin_login'),
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('settings/', admin_views.admin_settings, name='admin_settings'),
    
    # Products
    path('products/', admin_views.admin_products_list, name='admin_products_list'),
    path('products/add/', admin_views.admin_product_create, name='admin_product_create'),
    path('products/edit/<int:pk>/', admin_views.admin_product_update, name='admin_product_update'),
    path('products/delete/<int:pk>/', admin_views.admin_product_delete, name='admin_product_delete'),
    
    # Categories
    path('categories/', admin_views.admin_categories_list, name='admin_categories_list'),
    path('categories/add/', admin_views.admin_category_create, name='admin_category_create'),
    path('categories/edit/<int:pk>/', admin_views.admin_category_update, name='admin_category_update'),
    path('categories/delete/<int:pk>/', admin_views.admin_category_delete, name='admin_category_delete'),
    
    # Orders & Refunds
    path('orders/', admin_views.admin_orders_list, name='admin_orders_list'),
    path('orders/<int:pk>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:pk>/invoice/', admin_views.admin_order_invoice, name='admin_order_invoice'),
    path('refunds/', admin_views.admin_refunds_list, name='admin_refunds_list'),
    
    # Coupons
    path('coupons/', admin_views.admin_coupons_list, name='admin_coupons_list'),
    path('coupons/add/', admin_views.admin_coupon_create, name='admin_coupon_create'),
    path('coupons/edit/<int:pk>/', admin_views.admin_coupon_update, name='admin_coupon_update'),
    path('coupons/delete/<int:pk>/', admin_views.admin_coupon_delete, name='admin_coupon_delete'),
    
    # Users
    path('users/', admin_views.admin_users_list, name='admin_users_list'),
    path('users/<int:pk>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('users/<int:pk>/toggle-active/', admin_views.admin_user_toggle_active, name='admin_user_toggle_active'),

    # Reviews
    path('reviews/', admin_views.admin_reviews_queue, name='admin_reviews_queue'),
    path('reviews/<int:pk>/approve/', admin_views.admin_review_approve, name='admin_review_approve'),
    path('reviews/<int:pk>/reject/', admin_views.admin_review_reject, name='admin_review_reject'),

    # Banners
    path('banners/', admin_views.admin_banners_list, name='admin_banners_list'),
    path('banners/add/', admin_views.admin_banner_create, name='admin_banner_create'),
    path('banners/edit/<int:pk>/', admin_views.admin_banner_update, name='admin_banner_update'),
    path('banners/delete/<int:pk>/', admin_views.admin_banner_delete, name='admin_banner_delete'),

    # Payment Methods
    path('payments/', admin_views.admin_payments_list, name='admin_payments_list'),
    path('payments/add/', admin_views.admin_payment_create, name='admin_payment_create'),
    path('payments/edit/<int:pk>/', admin_views.admin_payment_update, name='admin_payment_update'),
    path('payments/delete/<int:pk>/', admin_views.admin_payment_delete, name='admin_payment_delete'),
    
    # Order Payment Verification
    path('orders/<int:pk>/mark-paid/', admin_views.admin_order_mark_paid, name='admin_order_mark_paid'),
]
