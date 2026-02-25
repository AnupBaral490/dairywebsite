from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

CATEGORY_CHOICES=(
    ('CR','Curd'),
    ('ML','Milk'),
    ('LS','Lassi'),
    ('MS','Milkshake'),
    ('PN','Paneer'),
    ('GH','Ghee'),
    ('CZ','Cheese'),
    ('IC','Ice-Creams'),
)

STATE_CHOICES = (
    ('Koshi', 'Koshi Pradesh'),
    ('Madhesh', 'Madhesh Pradesh'),
    ('Bagmati', 'Bagmati Pradesh'),
    ('Gandaki', 'Gandaki Pradesh'),
    ('Lumbini', 'Lumbini Pradesh'),
    ('Karnali', 'Karnali Pradesh'),
    ('Sudurpashchim', 'Sudurpashchim Pradesh'),
)



class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    farmer = models.ForeignKey('Farmer', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    def __str__(self):
        return self.title

    def default_variant(self):
        return self.variants.filter(is_default=True).first()

    @property
    def effective_discounted_price(self):
        variant = self.default_variant()
        return variant.discounted_price if variant else self.discounted_price

    @property
    def effective_selling_price(self):
        variant = self.default_variant()
        return variant.selling_price if variant else self.selling_price


VARIANT_UNIT_CHOICES = (
    ('ML', 'ml'),
    ('GM', 'g'),
)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    pack_size_value = models.PositiveIntegerField()
    pack_size_unit = models.CharField(max_length=2, choices=VARIANT_UNIT_CHOICES)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    stock = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} - {self.pack_size_label()}"

    def pack_size_label(self):
        return f"{self.pack_size_value}{self.get_pack_size_unit_display()}"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        unit_price = self.variant.discounted_price if self.variant else self.product.discounted_price
        return self.quantity * unit_price
    
STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),
)
    
class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

    
class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - {self.user.username} ({self.rating})"


class Farmer(models.Model):
    name = models.CharField(max_length=120)
    farm_name = models.CharField(max_length=160)
    location = models.CharField(max_length=160)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='farmers', blank=True, null=True)

    def __str__(self):
        return f"{self.farm_name} - {self.name}"


class FarmerMessage(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=120)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.farmer.farm_name} - {self.user.username}"


# Loyalty & Rewards Models
class LoyaltyTier(models.Model):
    TIER_CHOICES = (
        ('BRONZE', 'Bronze Tier'),
        ('SILVER', 'Silver Tier'),
        ('GOLD', 'Gold Tier'),
        ('PLATINUM', 'Platinum Tier'),
    )
    
    tier_name = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    min_points = models.IntegerField(default=0)
    max_points = models.IntegerField(default=9999999)
    bonus_multiplier = models.FloatField(default=1.0)  # 1.0 = 1x, 1.1 = 1.1x points
    description = models.TextField()
    color = models.CharField(max_length=20, default='#999999')
    icon_emoji = models.CharField(max_length=5, default='⭐')
    
    class Meta:
        ordering = ['min_points']
    
    def __str__(self):
        return f"{self.tier_name} (from {self.min_points} points)"


class CustomerLoyalty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty')
    total_points = models.IntegerField(default=0)
    current_tier = models.ForeignKey(LoyaltyTier, on_delete=models.SET_NULL, null=True, blank=True)
    lifetime_purchases = models.FloatField(default=0)
    total_orders = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    
    def update_tier(self):
        """Update customer tier based on points"""
        tier = LoyaltyTier.objects.filter(
            min_points__lte=self.total_points,
            max_points__gte=self.total_points
        ).first()
        if tier:
            self.current_tier = tier
            self.save()
    
    def get_bonus_multiplier(self):
        """Get point multiplier for current tier"""
        if self.current_tier:
            return self.current_tier.bonus_multiplier
        return 1.0
    
    def add_points(self, points):
        """Add points to customer account"""
        multiplier = self.get_bonus_multiplier()
        final_points = int(points * multiplier)
        self.total_points += final_points
        self.update_tier()
        RewardTransaction.objects.create(
            loyalty=self,
            transaction_type='EARN',
            points=final_points,
            description=f'Order purchase ({final_points} points)'
        )
        return final_points
    
    def redeem_points(self, points, reward_name):
        """Redeem points"""
        if self.total_points >= points:
            self.total_points -= points
            self.update_tier()
            RewardTransaction.objects.create(
                loyalty=self,
                transaction_type='REDEEM',
                points=points,
                description=f'Redeemed: {reward_name}'
            )
            return True
        return False
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points ({self.current_tier})"


class RewardTransaction(models.Model):
    TRANSACTION_CHOICES = (
        ('EARN', 'Points Earned'),
        ('REDEEM', 'Points Redeemed'),
        ('BONUS', 'Bonus Points'),
        ('EXPIRE', 'Points Expired'),
    )
    
    loyalty = models.ForeignKey(CustomerLoyalty, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    points = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.loyalty.user.username} - {self.transaction_type} {self.points} points"


class Reward(models.Model):
    REWARD_TYPES = (
        ('DISCOUNT', 'Discount'),
        ('FREEPRODUCT', 'Free Product'),
        ('SHIPPING', 'Free Shipping'),
        ('UPGRADE', 'Subscription Upgrade'),
    )
    
    name = models.CharField(max_length=120)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    points_required = models.IntegerField()
    discount_percentage = models.FloatField(default=0)  # For discount rewards
    discount_amount = models.FloatField(default=0)  # For discount rewards
    free_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(null=True, blank=True)  # None = unlimited
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['points_required']
    
    def __str__(self):
        return f"{self.name} - {self.points_required} points"
    
    def is_available(self):
        if not self.is_active:
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return True


class RedeemHistory(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redeemed_rewards')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('OrderPlaced', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.customer.username} redeemed {self.reward.name}"