from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category

def home(request):
    # Featured products (carousel items)
    featured_products = Product.objects.filter(featured=True, in_stock=True)[:3]
    
    # Latest products
    latest_products = Product.objects.filter(in_stock=True).order_by('-created_at')[:8]
    
    # Products with discount
    discounted_products = Product.objects.filter(
        in_stock=True
    ).exclude(compare_price=None)[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'discounted_products': discounted_products,
    }
    return render(request, 'index.html', context)

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(in_stock=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
    }
    return render(request, 'shop.html', context)

# def product_detail(request, slug):
#     product = get_object_or_404(Product, slug=slug, in_stock=True)
#     related_products = Product.objects.filter(
#         category=product.category, 
#         in_stock=True
#     ).exclude(id=product.id)[:4]
    
#     context = {
#         'product': product,
#         'related_products': related_products,
#     }
#     return render(request, 'shop-detail.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def account(request):
    return render(request, 'account.html')

def cart(request):
    return render(request, 'cart.html')

def category(request):
    return render(request, 'category.html')

def checkout(request):
    return render(request, 'checkout.html')

def product_details(request):
    return render(request, 'product-details.html')