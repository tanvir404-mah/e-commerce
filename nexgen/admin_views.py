from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Product, Category, Order, CustomUser, StoreSetting, Coupon, Banner, Review, PaymentMethod
from .forms import ProductForm, CategoryForm, OrderStatusForm, AdminCouponForm, BannerForm, ReviewModerationForm, PaymentMethodForm
from django.db.models import F

# Decorator to restrict access to staff/superusers
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_dashboard(request):
    total_revenue = sum(order.total_price for order in Order.objects.filter(status='Delivered'))
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = CustomUser.objects.filter(is_staff=False).count()
    
    pending_orders = Order.objects.filter(status='Pending').count()
    processing_orders = Order.objects.filter(status='Processing').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()
    low_stock_products = Product.objects.filter(stock__lte=F('low_stock_threshold'))
    
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_panel/dashboard.html', context)

# --- PRODUCTS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_products_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/products_list.html', {'products': products})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('admin_products_list')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/product_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_panel/product_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_products_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': product, 'cancel_url': 'admin_products_list'})

# --- CATEGORIES ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_categories_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_panel/categories_list.html', {'categories': categories})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_categories_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_categories_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': category, 'cancel_url': 'admin_categories_list'})

# --- ORDERS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_orders_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/orders_list.html', {'orders': orders})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
            return redirect('admin_order_detail', pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
        
    return render(request, 'admin_panel/order_detail.html', {'order': order, 'form': form})

# --- SETTINGS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_settings(request):
    setting, _ = StoreSetting.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        from .forms import StoreSettingForm
        form = StoreSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store settings updated successfully!')
            return redirect('admin_settings')
    else:
        from .forms import StoreSettingForm
        form = StoreSettingForm(instance=setting)
        
    return render(request, 'admin_panel/admin_settings.html', {'form': form})

# --- COUPONS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_coupons_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/coupons_list.html', {'coupons': coupons})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_coupon_create(request):
    if request.method == 'POST':
        form = AdminCouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('admin_coupons_list')
    else:
        form = AdminCouponForm()
    return render(request, 'admin_panel/coupon_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_coupon_update(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = AdminCouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('admin_coupons_list')
    else:
        form = AdminCouponForm(instance=coupon)
    return render(request, 'admin_panel/coupon_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully!')
        return redirect('admin_coupons_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': coupon, 'cancel_url': 'admin_coupons_list'})


# --- USERS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users_list.html', {'users': users})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_user_detail(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    user_orders = Order.objects.filter(user=user_obj).order_by('-created_at')
    lifetime_spend = sum(order.total_price for order in user_orders.filter(status='Delivered'))
    
    context = {
        'user_obj': user_obj,
        'user_orders': user_orders,
        'lifetime_spend': lifetime_spend,
    }
    return render(request, 'admin_panel/user_detail.html', context)

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_user_toggle_active(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        status_msg = "activated" if user_obj.is_active else "deactivated"
        messages.success(request, f'User account {status_msg}.')
    return redirect('admin_user_detail', pk=pk)

# --- REVIEWS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_reviews_queue(request):
    reviews = Review.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'admin_panel/reviews_queue.html', {'reviews': reviews})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_review_approve(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.is_approved = True
        review.save()
        messages.success(request, 'Review approved successfully.')
    return redirect('admin_reviews_queue')

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_review_reject(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review rejected and deleted.')
    return redirect('admin_reviews_queue')

# --- BANNERS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_banners_list(request):
    banners = Banner.objects.order_by('order', '-id')
    return render(request, 'admin_panel/banners_list.html', {'banners': banners})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner created successfully!')
            return redirect('admin_banners_list')
    else:
        form = BannerForm()
    return render(request, 'admin_panel/banner_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_banner_update(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner updated successfully!')
            return redirect('admin_banners_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'admin_panel/banner_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Banner deleted successfully!')
        return redirect('admin_banners_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': banner, 'cancel_url': 'admin_banners_list'})

# --- INVOICES & REFUNDS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_order_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'admin_panel/order_invoice.html', {'order': order})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_refunds_list(request):
    orders = Order.objects.filter(status='Refund Requested').order_by('-created_at')
    return render(request, 'admin_panel/refunds_list.html', {'orders': orders})


# --- PAYMENT METHODS ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_payments_list(request):
    payments = PaymentMethod.objects.all()
    return render(request, 'admin_panel/payments_list.html', {'payments': payments})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_payment_create(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment Method created successfully!')
            return redirect('admin_payments_list')
    else:
        form = PaymentMethodForm()
    return render(request, 'admin_panel/payment_method_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_payment_update(request, pk):
    payment = get_object_or_404(PaymentMethod, pk=pk)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment Method updated successfully!')
            return redirect('admin_payments_list')
    else:
        form = PaymentMethodForm(instance=payment)
    return render(request, 'admin_panel/payment_method_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_payment_delete(request, pk):
    payment = get_object_or_404(PaymentMethod, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment Method deleted successfully!')
        return redirect('admin_payments_list')
    return render(request, 'admin_panel/confirm_delete.html', {'object': payment, 'cancel_url': 'admin_payments_list'})


# --- ORDER VERIFICATION ---
@user_passes_test(is_admin, login_url='/store-admin/login/')
def admin_order_mark_paid(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.is_paid = True
        if order.status == 'Pending':
            order.status = 'Processing'
        order.save()
        messages.success(request, f'Order #{order.id} verified and marked as PAID.')
    return redirect('admin_order_detail', pk=pk)

