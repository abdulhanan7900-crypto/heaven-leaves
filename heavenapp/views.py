import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, ProductImage, Cart, CartItem, Order, OrderItem


def _get_or_create_cart(request):
    """Get or create a cart for the current session."""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


# ============================================================
# Page Views
# ============================================================

@ensure_csrf_cookie
def home(request):
    featured_products = Product.objects.filter(featured=True, in_stock=True, stock__gt=0)[:3]
    latest_products = Product.objects.filter(in_stock=True, stock__gt=0).order_by('-created_at')[:8]
    discounted_products = Product.objects.filter(
        in_stock=True, stock__gt=0
    ).exclude(compare_price=None)[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'discounted_products': discounted_products,
        'categories': categories,
    }
    return render(request, 'index.html', context)


@ensure_csrf_cookie
def category_page(request):
    categories = Category.objects.all()
    products = Product.objects.filter(in_stock=True, stock__gt=0)
    selected_category = None
    
    # Filter by category slug
    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    
    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sort
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'products': page_obj,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'category.html', context)


@ensure_csrf_cookie
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category,
        in_stock=True,
        stock__gt=0,
    ).exclude(id=product.id)[:4]
    images = product.images.all()
    
    context = {
        'product': product,
        'related_products': related_products,
        'images': images,
    }
    return render(request, 'product-details.html', context)


@ensure_csrf_cookie
def cart_page(request):
    cart = None
    cart_items = []
    session_key = request.session.session_key
    if session_key:
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_items = cart.items.select_related('product').all()
        except Cart.DoesNotExist:
            pass
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart.html', context)


@ensure_csrf_cookie
def checkout_page(request):
    cart = None
    cart_items = []
    session_key = request.session.session_key
    if session_key:
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_items = cart.items.select_related('product').all()
        except Cart.DoesNotExist:
            pass
    
    if request.method == 'POST':
        if not cart or not cart_items:
            return redirect('cart')
        
        # Create order
        order = Order.objects.create(
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            zip_code=request.POST.get('zip_code', ''),
            country=request.POST.get('country', 'Pakistan'),
            subtotal=cart.subtotal,
            tax=cart.tax,
            shipping=cart.shipping,
            total=cart.grand_total,
            session_key=session_key,
        )
        
        # Create order items and reduce stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
            )
            # Reduce product stock
            product = item.product
            product.stock -= item.quantity
            if product.stock <= 0:
                product.in_stock = False
            product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        # Store order id in session and redirect (prevents re-submission on refresh)
        request.session['last_order_id'] = order.id
        return redirect('order_confirmation')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'checkout.html', context)


# Static pages
def about(request):
    return render(request, 'about.html')


def order_confirmation(request):
    """Show order confirmation page after successful checkout."""
    order_id = request.session.get('last_order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.prefetch_related('items__product').get(id=order_id)
        except Order.DoesNotExist:
            pass
    if not order:
        return redirect('home')
    return render(request, 'order-confirmation.html', {'order': order})


def contact(request):
    return render(request, 'contact.html')


def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


def account(request):
    return render(request, 'account.html')


# ============================================================
# Cart API Endpoints (AJAX)
# ============================================================

@require_POST
def cart_add(request):
    """Add a product to the cart."""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    
    if not product.is_available:
        return JsonResponse({'success': False, 'error': 'Product is out of stock'}, status=400)
    
    cart = _get_or_create_cart(request)
    
    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock} items available in stock',
                'stock': product.stock,
            }, status=400)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if cart_item.quantity > product.stock:
        cart_item.quantity = product.stock
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart',
        'cart_count': cart.total_items,
        'cart_total': str(cart.grand_total),
        'item_quantity': cart_item.quantity,
    })


@require_POST
def cart_update(request):
    """Update item quantity in the cart."""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'success': False, 'error': 'No cart found'}, status=400)
    
    try:
        cart = Cart.objects.get(session_key=session_key)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Item not found in cart'}, status=404)
    
    product = cart_item.product
    if quantity <= 0:
        cart_item.delete()
    elif quantity > product.stock:
        return JsonResponse({
            'success': False,
            'error': f'Only {product.stock} items available in stock',
            'stock': product.stock,
        }, status=400)
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    # Refresh cart data
    cart.refresh_from_db()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items,
        'cart_total': str(cart.grand_total),
        'subtotal': str(cart.subtotal),
        'tax': str(cart.tax),
        'shipping': str(cart.shipping),
        'grand_total': str(cart.grand_total),
        'item_total': str(cart_item.total_price) if cart_item.pk else '0',
    })


@require_POST
def cart_remove(request):
    """Remove an item from the cart."""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'success': False, 'error': 'No cart found'}, status=400)
    
    try:
        cart = Cart.objects.get(session_key=session_key)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
    
    cart.refresh_from_db()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items,
        'cart_total': str(cart.grand_total),
        'subtotal': str(cart.subtotal),
        'tax': str(cart.tax),
        'shipping': str(cart.shipping),
        'grand_total': str(cart.grand_total),
    })


@require_POST
def cart_clear(request):
    """Clear the entire cart."""
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'success': False, 'error': 'No cart found'}, status=400)
    
    try:
        cart = Cart.objects.get(session_key=session_key)
        cart.items.all().delete()
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No cart found'}, status=400)
    
    return JsonResponse({
        'success': True,
        'cart_count': 0,
        'cart_total': '0',
    })


def cart_data(request):
    """Get current cart data (GET)."""
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({
            'items': [],
            'count': 0,
            'subtotal': '0',
            'tax': '0',
            'shipping': '0',
            'grand_total': '0',
        })
    
    try:
        cart = Cart.objects.get(session_key=session_key)
        items = []
        for item in cart.items.select_related('product').all():
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_slug': item.product.slug,
                'product_image': item.product.image.url if item.product.image else '',
                'price': str(item.product.price),
                'quantity': item.quantity,
                'total': str(item.total_price),
                'stock': item.product.stock,
            })
        
        return JsonResponse({
            'items': items,
            'count': cart.total_items,
            'subtotal': str(cart.subtotal),
            'tax': str(cart.tax),
            'shipping': str(cart.shipping),
            'grand_total': str(cart.grand_total),
        })
    except Cart.DoesNotExist:
        return JsonResponse({
            'items': [],
            'count': 0,
            'subtotal': '0',
            'tax': '0',
            'shipping': '0',
            'grand_total': '0',
        })