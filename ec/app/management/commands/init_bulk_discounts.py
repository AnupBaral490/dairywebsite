from django.core.management.base import BaseCommand
from app.models import Product, BulkDiscount


class Command(BaseCommand):
    help = 'Initialize sample bulk discounts for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample bulk discounts...'))
        
        # Get all products
        products = Product.objects.all()[:5]  # Limit to first 5 products for demo
        
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Please create products first.'))
            return
        
        created_count = 0
        
        for product in products:
            # Create 3-tier bulk discount structure for each product
            tiers = [
                {'min_quantity': 5, 'discount_percentage': 5.0},
                {'min_quantity': 10, 'discount_percentage': 10.0},
                {'min_quantity': 20, 'discount_percentage': 15.0},
            ]
            
            for tier in tiers:
                discount, created = BulkDiscount.objects.get_or_create(
                    product=product,
                    min_quantity=tier['min_quantity'],
                    defaults={
                        'discount_percentage': tier['discount_percentage'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created: {product.title} - {tier["min_quantity"]}+ items = {tier["discount_percentage"]}% off'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Already exists: {product.title} - {tier["min_quantity"]}+ items'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Complete! Created {created_count} new bulk discount(s) for {len(products)} product(s).'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\nTip: You can modify these in Django admin at /admin/app/bulkdiscount/'
            )
        )
