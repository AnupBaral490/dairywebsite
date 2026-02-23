from django.contrib import admin
from . models import Product, ProductVariant, ProductReview, Farmer, FarmerMessage
from .models import ContactMessage
from .models import Customer
from .models import Cart
from . models import Payment, OrderPlaced, Wishlist
# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','farmer','product_image']
    list_display_links = ['id', 'title']


@admin.register(ProductVariant)
class ProductVariantModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'pack_size_value', 'pack_size_unit', 'discounted_price', 'stock', 'is_default']
    list_filter = ['pack_size_unit', 'is_default']
    search_fields = ['product__title']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'locality', 'city', 'state', 'zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display=['id','user','customer','product','variant','quantity','ordered_date','status','payment']

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product']


@admin.register(ProductReview)
class ProductReviewModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__title', 'user__username']


@admin.register(Farmer)
class FarmerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'farm_name', 'name', 'location', 'phone', 'email']
    search_fields = ['farm_name', 'name', 'location']
    list_display_links = ['id', 'farm_name']


@admin.register(FarmerMessage)
class FarmerMessageModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'farmer', 'user', 'product', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['farmer__farm_name', 'user__username', 'subject']