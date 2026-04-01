from .models import StoreSetting, Banner

def store_settings(request):
    try:
        settings = StoreSetting.objects.get(pk=1)
        currency = settings.currency
    except StoreSetting.DoesNotExist:
        currency = '$'
    
    banners = Banner.objects.filter(is_active=True).order_by('order')
    
    return {
        'STORE_CURRENCY': currency,
        'banners': banners
    }
