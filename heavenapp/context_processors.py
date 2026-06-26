from django.core.cache import cache
from .models import Cart, Category, Product


def cart_context(request):
    """Add cart info to every template context."""
    session_key = request.session.session_key
    cart_item_count = 0
    cart_total = '0.00'
    
    if session_key:
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_item_count = cart.total_items
            cart_total = str(cart.grand_total)
        except (Cart.DoesNotExist, Exception):
            pass
    
    return {
        'cart_item_count': cart_item_count,
        'cart_total': cart_total,
    }


def categories_context(request):
    """Add categories and megamenu products to every template context.

    Results are cached for 5 minutes to avoid repeated database queries.
    """
    cache_key = 'header_categories_context'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    categories = list(Category.objects.prefetch_related('products'))
    # Featured products for megamenu
    nav_featured = list(Product.objects.filter(featured=True, in_stock=True, stock__gt=0)[:4])
    # New arrivals for megamenu
    nav_new = list(Product.objects.filter(in_stock=True, stock__gt=0).order_by('-created_at')[:4])
    # Sale/discounted products for megamenu
    nav_sale = list(Product.objects.filter(
        in_stock=True, stock__gt=0
    ).exclude(compare_price=None).order_by('-created_at')[:4])

    result = {
        'all_categories': categories,
        'nav_featured': nav_featured,
        'nav_new': nav_new,
        'nav_sale': nav_sale,
    }
    cache.set(cache_key, result, timeout=300)
    return result
