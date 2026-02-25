from django.contrib import admin
from . models import Product, ProductVariant, ProductReview, Farmer, FarmerMessage
from .models import ContactMessage
from .models import Customer
from .models import Cart
from . models import Payment, OrderPlaced, Wishlist
from .models import LoyaltyTier, CustomerLoyalty, RewardTransaction, Reward, RedeemHistory
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


# Loyalty & Rewards Admin

@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ['tier_name', 'min_points', 'max_points', 'bonus_multiplier', 'color']
    fieldsets = (
        ('Tier Information', {
            'fields': ('tier_name', 'min_points', 'max_points', 'bonus_multiplier'),
        }),
        ('Display', {
            'fields': ('color', 'icon_emoji', 'description'),
        }),
    )


@admin.register(CustomerLoyalty)
class CustomerLoyaltyAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'current_tier', 'total_orders', 'joined_date']
    list_filter = ['current_tier', 'joined_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['joined_date', 'total_orders', 'lifetime_purchases']
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'current_tier'),
        }),
        ('Points & Statistics', {
            'fields': ('total_points', 'lifetime_purchases', 'total_orders'),
        }),
        ('Dates', {
            'fields': ('joined_date', 'last_purchase_date'),
        }),
    )


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty', 'transaction_type', 'points', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty__user__username', 'description']
    readonly_fields = ['created_at', 'loyalty']
    
    def has_add_permission(self, request):
        return False  # Transactions created automatically
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'reward_type', 'points_required', 'is_active', 'times_used']
    list_filter = ['reward_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'reward_type'),
        }),
        ('Points Requirements', {
            'fields': ('points_required',),
        }),
        ('Reward Details', {
            'fields': ('discount_percentage', 'discount_amount', 'free_product'),
        }),
        ('Status & Usage', {
            'fields': ('is_active', 'max_uses', 'times_used'),
        }),
    )


@admin.register(RedeemHistory)
class RedeemHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'reward', 'points_used', 'redeemed_at']
    list_filter = ['reward', 'redeemed_at']
    search_fields = ['customer__username', 'reward__name']
    readonly_fields = ['redeemed_at']
    
    def has_add_permission(self, request):
        return False  # Redemptions created when user redeems
    search_fields = ['farmer__farm_name', 'user__username', 'subject']