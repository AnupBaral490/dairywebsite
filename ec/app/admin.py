from django.contrib import admin
from . models import Product, ProductVariant, ProductReview, Farmer, FarmerMessage, BulkDiscount
from .models import ContactMessage
from .models import Customer
from .models import Cart
from . models import Payment, OrderPlaced, Wishlist
from .models import LoyaltyTier, CustomerLoyalty, RewardTransaction, Reward, RedeemHistory
from .models import FAQCategory, FAQ, HelpArticle, LiveChatMessage
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


@admin.register(BulkDiscount)
class BulkDiscountModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'min_quantity', 'discount_percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__title']
    list_editable = ['is_active']
    ordering = ['product', 'min_quantity']
    fieldsets = (
        ('Product & Quantity', {
            'fields': ('product', 'min_quantity'),
        }),
        ('Discount Settings', {
            'fields': ('discount_percentage', 'is_active'),
        }),
    )


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


# FAQ & Help Center Admin

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'faq_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    def faq_count(self, obj):
        return obj.faqs.count()
    faq_count.short_description = 'Number of FAQs'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_featured', 'is_active', 'views', 'helpful_count']
    list_filter = ['category', 'is_featured', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_featured', 'is_active']
    readonly_fields = ['views', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Question & Answer', {
            'fields': ('category', 'question', 'answer'),
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active'),
        }),
        ('Statistics', {
            'fields': ('views', 'helpful_count', 'not_helpful_count'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'is_featured', 'views', 'created_at']
    list_filter = ['category', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'summary', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    readonly_fields = ['views', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'slug', 'category', 'author'),
        }),
        ('Content', {
            'fields': ('summary', 'content', 'featured_image'),
        }),
        ('Tags & Categories', {
            'fields': ('tags',),
        }),
        ('Publication Settings', {
            'fields': ('is_published', 'is_featured'),
        }),
        ('Statistics', {
            'fields': ('views', 'helpful_count', 'not_helpful_count'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
    list_display = ['get_sender', 'message_preview', 'is_staff_message', 'is_read', 'created_at']
    list_filter = ['is_staff_message', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'message', 'user__username']
    readonly_fields = ['session_id', 'user', 'name', 'email', 'created_at']
    
    def get_sender(self, obj):
        if obj.user:
            return obj.user.username
        return obj.name or obj.email or "Anonymous"
    get_sender.short_description = 'Sender'
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def has_add_permission(self, request):
        return True  # Allow staff to send messages