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