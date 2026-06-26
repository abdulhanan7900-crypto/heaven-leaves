from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('category/', views.category_page, name='category'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('account/', views.account, name='account'),
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    
    # Cart API endpoints
    path('api/cart/add/', views.cart_add, name='cart_add'),
    path('api/cart/update/', views.cart_update, name='cart_update'),
    path('api/cart/remove/', views.cart_remove, name='cart_remove'),
    path('api/cart/clear/', views.cart_clear, name='cart_clear'),
    path('api/cart/data/', views.cart_data, name='cart_data'),
]