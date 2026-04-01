from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product, Category, Order, StoreSetting, Address, Review, Coupon, Banner, ProductImage, PaymentMethod


class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field_class = (
                'appearance-none rounded-2xl relative block w-full px-3 py-4 border border-gray-300 '
                'placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 '
                'focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm '
                'transition-all shadow-sm'
            )
            if isinstance(field.widget, forms.CheckboxInput):
                field_class = 'h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded'
            elif isinstance(field.widget, forms.Select):
                field_class += ' pr-10'
            elif isinstance(field.widget, forms.Textarea):
                field_class += ' resize-none'
            field.widget.attrs.update({'class': field_class})


class CustomUserCreationForm(TailwindFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number')


class ProfileUpdateForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'profile_picture')
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('notify_email', 'notify_sms', 'notify_push')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'sr-only peer',
            })


class AddressForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Address
        fields = ('label', 'full_name', 'phone', 'street_address', 'city', 'postal_code', 'is_default')
        widgets = {
            'is_default': forms.CheckboxInput(),
        }


class ReviewForm(TailwindFormMixin, forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),
        label='Your Rating'
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this product...'}),
        }


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter coupon code',
            'class': (
                'flex-1 rounded-l-2xl px-4 py-3 border border-gray-300 text-gray-900 '
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent '
                'bg-white/70 backdrop-blur-sm shadow-sm text-sm font-medium'
            )
        })
    )


class CategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class ProductForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'slug', 'description', 'price', 'sale_price', 'is_on_sale', 'stock', 'low_stock_threshold', 'category', 'image']


class OrderStatusForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class StoreSettingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = StoreSetting
        fields = ['currency', 'tax_percentage', 'base_shipping_cost', 'free_shipping_threshold', 'stripe_public_key', 'stripe_secret_key', 'paypal_client_id']
        labels = {
            'currency': 'Store Primary Currency',
            'tax_percentage': 'Tax Rate (%)',
            'base_shipping_cost': 'Base Shipping Cost',
            'free_shipping_threshold': 'Free Shipping Threshold',
        }


class AdminCouponForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'min_order', 'is_active']


class BannerForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'link', 'is_active', 'order']


class ProductImageForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


class ReviewModerationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ['is_approved']


class PaymentMethodForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['provider_name', 'account_number', 'account_type', 'instruction', 'logo', 'is_active']

