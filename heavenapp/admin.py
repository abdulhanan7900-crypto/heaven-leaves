from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'compare_price', 'category', 'stock', 'stock_status', 'featured', 'in_stock', 'created_at']
    list_filter = ['category', 'featured', 'in_stock', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ['featured', 'in_stock', 'stock', 'price']
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return '❌ Out of Stock'
        elif obj.stock < 5:
            return f'⚠️ Low ({obj.stock})'
        return f'✅ In Stock ({obj.stock})'
    stock_status.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key', 'total_items', 'total_price', 'updated_at']
    inlines = [CartItemInline]
    readonly_fields = ['session_key', 'created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'price', 'get_item_total']
    can_delete = False

    def get_item_total(self, obj):
        if obj.price and obj.quantity:
            return f'Rs. {obj.price * obj.quantity:.2f}'
        return 'Rs. 0.00'
    get_item_total.short_description = 'Item Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_full_name', 'email', 'phone', 'city', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at', 'city']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'city']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['subtotal', 'tax', 'shipping', 'total', 'session_key', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Order Details', {
            'fields': ('status', 'subtotal', 'tax', 'shipping', 'total')
        }),
        ('System', {
            'fields': ('session_key', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Customer Name'
    get_full_name.admin_order_field = 'first_name'