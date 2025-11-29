from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('shop/category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    # path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('cart/', views.cart, name='cart'),
    path('category/', views.category, name='category'),
    path('checkout/', views.checkout, name='checkout'),
    path('product-details/', views.product_details, name='product-details'),
]