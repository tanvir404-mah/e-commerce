import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import (
    Category, Product, Cart, CartItem,
    Order, OrderItem, Address, Wishlist, Review, Coupon, PaymentMethod
)
from .forms import (
    CustomUserCreationForm, ProfileUpdateForm, NotificationPreferencesForm,
    AddressForm, ReviewForm, CouponForm
)


# ─────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


def get_wishlist_ids(request):
    """Returns a set of product IDs in the current user's wishlist."""
    if request.user.is_authenticated:
        return set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    return set()


# ─────────────────────────────────────────────────────────────
# SHOP
# ─────────────────────────────────────────────────────────────

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    search_query = request.GET.get('search')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(title__icontains=search_query)

    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'wishlist_ids': get_wishlist_ids(request),
    }
    return render(request, 'nexgen/home.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    already_reviewed = False
    can_review = False

    if request.user.is_authenticated:
        # Check against ALL reviews (not just approved ones) to prevent double submission
        already_reviewed = product.reviews.filter(user=request.user).exists()

        has_ordered = OrderItem.objects.filter(
            order__user=request.user, 
            product=product, 
            order__status__in=['Delivered', 'Shipped', 'Processing']
        ).exists()
        
        can_review = has_ordered and not already_reviewed

    in_wishlist = product.id in get_wishlist_ids(request)

    context = {
        'product': product,
        'reviews': reviews,
        'can_review': can_review,
        'already_reviewed': already_reviewed,
        'review_form': ReviewForm() if can_review else None,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'nexgen/product_detail.html', context)


# ─────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────

def view_cart(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    total_price = sum(item.product.get_display_price * item.quantity for item in items)
    return render(request, 'nexgen/cart.html', {
        'cart': cart, 'items': items, 'total_price': total_price
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Added {product.title} to your cart.")
        return redirect('cart')
    return redirect('home')


def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 0))
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect('cart')


# ─────────────────────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────────────────────

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        in_wishlist = False
    else:
        in_wishlist = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})

    messages.success(
        request,
        f"{'Added to' if in_wishlist else 'Removed from'} your wishlist."
    )
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ─────────────────────────────────────────────────────────────
# REVIEWS
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    has_ordered = OrderItem.objects.filter(
        order__user=request.user, 
        product=product, 
        order__status__in=['Delivered', 'Shipped', 'Processing']
    ).exists()
    already_reviewed = Review.objects.filter(user=request.user, product=product).exists()

    if not has_ordered or already_reviewed:
        messages.error(request, "You cannot review this product.")
        return redirect('product_detail', pk=product.id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.is_approved = False  # Changed back to False for Admin Moderation
        review.save()
        messages.success(request, "Thanks for your review!")
    else:
        messages.error(request, "Please select a valid rating.")
    return redirect('product_detail', pk=product.id)


# ─────────────────────────────────────────────────────────────
# COUPON
# ─────────────────────────────────────────────────────────────

@require_POST
def apply_coupon(request):
    form = CouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code'].upper().strip()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            # Check min order
            cart = get_or_create_cart(request)
            items = cart.items.all()
            total = sum(item.product.get_display_price * item.quantity for item in items)
            if total < coupon.min_order:
                messages.error(
                    request,
                    f"This coupon requires a minimum order of ${coupon.min_order}."
                )
            else:
                request.session['coupon_id'] = coupon.id
                request.session['coupon_discount'] = float(coupon.calculate_discount(total))
                messages.success(
                    request,
                    f"Coupon '{coupon.code}' applied! You save "
                    f"{'%g%%' % coupon.value if coupon.discount_type == 'percent' else '$' + str(coupon.value)}."
                )
        except Coupon.DoesNotExist:
            request.session.pop('coupon_id', None)
            messages.error(request, "Invalid or expired coupon code.")
    return redirect('checkout')


def remove_coupon(request):
    request.session.pop('coupon_id', None)
    request.session.pop('coupon_discount', None)
    messages.info(request, "Coupon removed.")
    return redirect('checkout')


# ─────────────────────────────────────────────────────────────
# CHECKOUT & ORDERS
# ─────────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    subtotal = sum(item.product.get_display_price * item.quantity for item in items)

    from decimal import Decimal
    
    # Resolve coupon from session
    coupon = None
    discount = Decimal(str(request.session.get('coupon_discount', 0)))
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            # Recalculate correctly in case cart changed
            discount_val = coupon.calculate_discount(subtotal)
            request.session['coupon_discount'] = float(discount_val)
            discount = Decimal(str(discount_val))
        except Coupon.DoesNotExist:
            request.session.pop('coupon_id', None)
            request.session.pop('coupon_discount', None)
            discount = Decimal(0)

    from .models import StoreSetting
    try:
        settings = StoreSetting.objects.get(pk=1)
        shipping_cost = Decimal('0.00') if (settings.free_shipping_threshold is not None and subtotal >= settings.free_shipping_threshold) else settings.base_shipping_cost
    except StoreSetting.DoesNotExist:
        shipping_cost = Decimal('0.00')

    total_price = subtotal - discount + shipping_cost
    saved_addresses = request.user.addresses.all()
    coupon_form = CouponForm()
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '').strip()
        payment_provider_id = request.POST.get('payment_provider_id')
        sender_number = request.POST.get('sender_number', '')
        transaction_id = request.POST.get('transaction_id', '')

        # Use saved address if selected
        address_id = request.POST.get('saved_address_id')
        if address_id:
            try:
                addr = Address.objects.get(id=address_id, user=request.user)
                shipping_address = (
                    f"{addr.full_name}\n{addr.street_address}\n{addr.city} {addr.postal_code}\n{addr.phone}"
                )
            except Address.DoesNotExist:
                pass

        payment_provider = None
        if payment_provider_id:
            try:
                payment_provider = PaymentMethod.objects.get(id=payment_provider_id, is_active=True)
            except PaymentMethod.DoesNotExist:
                pass

        if not shipping_address:
            messages.error(request, "Please provide a shipping address.")
        elif not payment_provider:
             messages.error(request, "Please select a payment method.")
        else:
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_price=total_price,
                discount_amount=discount,
                coupon=coupon,
                payment_provider=payment_provider,
                sender_number=sender_number,
                transaction_id=transaction_id,
                is_paid=False,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.get_display_price,
                    quantity=item.quantity,
                )
                item.product.stock -= item.quantity
                item.product.save()

            cart.items.all().delete()
            request.session.pop('coupon_id', None)
            request.session.pop('coupon_discount', None)
            messages.success(request, f"Order #{order.id} placed successfully! 🎉")
            return redirect('order_detail', order_id=order.id)

    active_payment_methods = PaymentMethod.objects.filter(is_active=True)

    return render(request, 'nexgen/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total_price': total_price,
        'coupon': coupon,
        'coupon_form': coupon_form,
        'saved_addresses': saved_addresses,
        'active_payment_methods': active_payment_methods,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product').all()

    # Build tracking timeline
    all_statuses = ['Pending', 'Processing', 'Shipped', 'Out for Delivery', 'Delivered']
    cancelled = order.status in ['Cancelled', 'Refund Requested']
    current_index = all_statuses.index(order.status) if order.status in all_statuses else -1

    return render(request, 'nexgen/order_detail.html', {
        'order': order,
        'items': items,
        'all_statuses': all_statuses,
        'current_index': current_index,
        'cancelled': cancelled,
    })


@login_required
@require_POST
def reorder(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_or_create_cart(request)

    added = 0
    for item in original_order.items.select_related('product').all():
        if item.product.stock > 0:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
            if not created:
                cart_item.quantity += item.quantity
            else:
                cart_item.quantity = item.quantity
            cart_item.save()
            added += 1

    if added:
        messages.success(request, f"Added {added} item(s) from Order #{order_id} back to your cart.")
    else:
        messages.warning(request, "No items could be added (out of stock).")
    return redirect('cart')


@login_required
@require_POST
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Delivered':
        order.status = 'Refund Requested'
        order.save()
        messages.success(request, f"Refund requested for Order #{order.id}.")
    else:
        messages.error(request, "Refund can only be requested for delivered orders.")
    return redirect('order_detail', order_id=order.id)


# ─────────────────────────────────────────────────────────────
# USER DASHBOARD
# ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    tab = request.GET.get('tab', 'orders')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    addresses = request.user.addresses.all()

    tabs = [
        ('orders', 'My Orders', 'package'),
        ('profile', 'My Profile', 'user'),
        ('addresses', 'Address Book', 'map-pin'),
        ('wishlist', 'Wishlist', 'heart'),
        ('notifications', 'Notifications', 'bell'),
    ]

    user = request.user
    notification_prefs = [
        ('email', 'Email Notifications', 'Order updates, promotions & newsletters', 'mail', 'notify_email', user.notify_email),
        ('sms', 'SMS Notifications', 'Text alerts for order status changes', 'message-square', 'notify_sms', user.notify_sms),
        ('push', 'Push Notifications', 'Browser alerts for sales & flash deals', 'bell', 'notify_push', user.notify_push),
    ]

    context = {
        'tab': tab,
        'tabs': tabs,
        'orders': orders,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
        'notification_prefs': notification_prefs,
        'profile_form': ProfileUpdateForm(instance=request.user),
        'notif_form': NotificationPreferencesForm(instance=request.user),
        'address_form': AddressForm(),
    }
    return render(request, 'nexgen/dashboard.html', context)



@login_required
@require_POST
def update_profile(request):
    form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully!")
    else:
        messages.error(request, "Please correct the errors below.")
    return redirect('/dashboard/?tab=profile')


@login_required
@require_POST
def update_notifications(request):
    form = NotificationPreferencesForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Notification preferences saved!")
    else:
        messages.error(request, "Could not save preferences.")
    return redirect('/dashboard/?tab=notifications')


@login_required
@require_POST
def add_address(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, f"{address.label} address added.")
    else:
        messages.error(request, "Please fill in all required address fields.")
    return redirect('/dashboard/?tab=addresses')


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated.")
            return redirect('/dashboard/?tab=addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'nexgen/edit_address.html', {'form': form, 'address': address})


@login_required
@require_POST
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address removed.")
    return redirect('/dashboard/?tab=addresses')


@login_required
@require_POST
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"'{address.label}' set as your default address.")
    return redirect('/dashboard/?tab=addresses')


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to NexGen!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
