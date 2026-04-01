from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Shop
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('checkout/coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/reorder/', views.reorder, name='reorder'),
    path('order/<int:order_id>/refund/', views.request_refund, name='request_refund'),

    # Wishlist
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Reviews
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),

    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/notifications/', views.update_notifications, name='update_notifications'),
    path('profile/addresses/add/', views.add_address, name='add_address'),
    path('profile/addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('profile/addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('profile/addresses/<int:address_id>/default/', views.set_default_address, name='set_default_address'),

    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
]
