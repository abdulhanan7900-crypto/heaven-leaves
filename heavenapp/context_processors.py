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
    """Add categories and megamenu products to every template context."""
    categories = Category.objects.all()
    # Featured products for megamenu
    nav_featured = Product.objects.filter(featured=True, in_stock=True, stock__gt=0)[:4]
    # New arrivals for megamenu
    nav_new = Product.objects.filter(in_stock=True, stock__gt=0).order_by('-created_at')[:4]
    # Sale/discounted products for megamenu
    nav_sale = Product.objects.filter(
        in_stock=True, stock__gt=0
    ).exclude(compare_price=None).order_by('-created_at')[:4]
    return {
        'all_categories': categories,
        'nav_featured': nav_featured,
        'nav_new': nav_new,
        'nav_sale': nav_sale,
    }
