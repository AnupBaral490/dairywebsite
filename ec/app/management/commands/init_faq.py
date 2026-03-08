from django.core.management.base import BaseCommand
from app.models import FAQCategory, FAQ, HelpArticle
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initialize FAQ and Help Center with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing FAQ & Help Center...')

        # Create FAQ Categories
        categories_data = [
            {
                'name': 'Orders & Delivery',
                'slug': 'orders-delivery',
                'description': 'Questions about ordering and delivery process',
                'icon': 'fa-shipping-fast',
                'order': 1
            },
            {
                'name': 'Products & Quality',
                'slug': 'products-quality',
                'description': 'Information about our products and quality standards',
                'icon': 'fa-box',
                'order': 2
            },
            {
                'name': 'Payments & Pricing',
                'slug': 'payments-pricing',
                'description': 'Payment methods, pricing, and refunds',
                'icon': 'fa-credit-card',
                'order': 3
            },
            {
                'name': 'Account & Profile',
                'slug': 'account-profile',
                'description': 'Account management and profile settings',
                'icon': 'fa-user-circle',
                'order': 4
            },
            {
                'name': 'Loyalty & Rewards',
                'slug': 'loyalty-rewards',
                'description': 'Questions about our loyalty program',
                'icon': 'fa-gift',
                'order': 5
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = FAQCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))

        # Create FAQs
        faqs_data = [
            {
                'category': 'orders-delivery',
                'question': 'How long does delivery take?',
                'answer': 'We typically deliver within 24-48 hours for orders placed within city limits. For outstation orders, delivery may take 3-5 business days. You can track your order status in the Orders section of your account.',
                'is_featured': True,
                'order': 1
            },
            {
                'category': 'orders-delivery',
                'question': 'Can I change or cancel my order?',
                'answer': 'Yes! You can cancel your order within 2 hours of placing it. To cancel, go to your Orders page and click "Cancel Order". After 2 hours, the order is processed and cannot be cancelled. For changes, please contact our support team.',
                'is_featured': True,
                'order': 2
            },
            {
                'category': 'orders-delivery',
                'question': 'What are your delivery hours?',
                'answer': 'We deliver between 7 AM to 9 PM on all days. You can select your preferred delivery time slot during checkout. Morning deliveries (7-9 AM) are most popular for fresh dairy products.',
                'order': 3
            },
            {
                'category': 'orders-delivery',
                'question': 'Do you offer same-day delivery?',
                'answer': 'Yes! Orders placed before 6 PM are eligible for same-day delivery. Same-day delivery is available for select areas within city limits. Check your pincode during checkout to see if same-day delivery is available.',
                'order': 4
            },
            {
                'category': 'products-quality',
                'question': 'Are your products 100% organic?',
                'answer': 'We source our dairy products from certified organic farms. All our milk, curd, and ghee products are made from milk of grass-fed cows. We maintain strict quality control and provide traceability from farm to table.',
                'is_featured': True,
                'order': 1
            },
            {
                'category': 'products-quality',
                'question': 'How should I store dairy products?',
                'answer': 'All dairy products should be refrigerated immediately upon delivery. Milk and curd should be stored at 4°C or below. Ghee can be stored at room temperature in an airtight container. Please check product labels for specific storage instructions.',
                'order': 2
            },
            {
                'category': 'products-quality',
                'question': 'What is the shelf life of your products?',
                'answer': 'Fresh milk: 3-4 days when refrigerated. Curd: 2-3 days. Paneer: 3-4 days. Ghee: 6 months at room temperature. Ice cream: Up to 3 months when frozen. Always check the "Best Before" date on the packaging.',
                'order': 3
            },
            {
                'category': 'payments-pricing',
                'question': 'What payment methods do you accept?',
                'answer': 'We accept all major payment methods including Credit/Debit Cards, Net Banking, UPI, Digital Wallets (Paytm, PhonePe, Google Pay), and Cash on Delivery. All online payments are processed securely through Razorpay.',
                'is_featured': True,
                'order': 1
            },
            {
                'category': 'payments-pricing',
                'question': 'Do you offer bulk order discounts?',
                'answer': 'Yes! We offer automatic bulk discounts when you order larger quantities. Discounts range from 5% to 15% based on quantity. The discount is automatically applied in your cart. Check product pages for specific discount tiers.',
                'order': 2
            },
            {
                'category': 'payments-pricing',
                'question': 'What is your refund policy?',
                'answer': 'If you receive a damaged or quality-compromised product, please report it within 24 hours of delivery. We offer full refund or replacement. Refunds are processed within 5-7 business days to your original payment method.',
                'order': 3
            },
            {
                'category': 'account-profile',
                'question': 'How do I create an account?',
                'answer': 'Click on "Registration" in the top menu. Fill in your details including name, email, phone number, and password. Once registered, you can manage your addresses, track orders, and earn loyalty points.',
                'order': 1
            },
            {
                'category': 'account-profile',
                'question': 'I forgot my password. How do I reset it?',
                'answer': 'Click on "Login" and then select "Forgot Password". Enter your registered email address. You\'ll receive a password reset link via email. Click the link and set a new password.',
                'order': 2
            },
            {
                'category': 'account-profile',
                'question': 'Can I have multiple delivery addresses?',
                'answer': 'Yes! You can add multiple delivery addresses to your profile. Go to Profile > Addresses to add, edit, or delete addresses. You can select your preferred address during checkout.',
                'order': 3
            },
            {
                'category': 'loyalty-rewards',
                'question': 'How does the loyalty program work?',
                'answer': 'Earn points on every purchase! For every ₹100 spent, you earn 10 loyalty points. Points can be redeemed for discounts, free products, or special perks. Check your loyalty dashboard to see your points balance and tier status.',
                'is_featured': True,
                'order': 1
            },
            {
                'category': 'loyalty-rewards',
                'question': 'What are loyalty tiers?',
                'answer': 'We have 4 tiers: Bronze, Silver, Gold, and Platinum. Higher tiers offer bonus point multipliers and exclusive rewards. Your tier is automatically upgraded based on your total points. Each tier unlocks better benefits!',
                'order': 2
            },
            {
                'category': 'loyalty-rewards',
                'question': 'How can I redeem my rewards?',
                'answer': 'Visit the Rewards Shop from your account menu. Browse available rewards and click "Redeem" on any reward you can afford. Your points will be deducted and the reward will be applied to your next eligible order.',
                'order': 3
            }
        ]

        faq_count = 0
        for faq_data in faqs_data:
            category_slug = faq_data.pop('category')
            category = categories[category_slug]
            
            faq, created = FAQ.objects.get_or_create(
                category=category,
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                faq_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Created {faq_count} FAQs'))

        # Create Help Articles
        articles_data = [
            {
                'title': 'Getting Started with Fresh Dairy',
                'slug': 'getting-started',
                'category': 'account-profile',
                'summary': 'Everything you need to know to start ordering fresh dairy products online',
                'content': '''Welcome to Fresh Dairy! This guide will help you get started with ordering.

Step 1: Create Your Account
Click on Registration in the menu. Fill in your details and verify your email address.

Step 2: Browse Products
Explore our catalog of fresh dairy products. Use filters to find exactly what you need.

Step 3: Add to Cart
Click "Add to Cart" on any product. You can adjust quantities and select variants.

Step 4: Checkout
Review your cart and proceed to checkout. Add your delivery address and select a payment method.

Step 5: Track Your Order
After placing your order, you can track its status in the Orders section of your account.

That's it! Enjoy fresh dairy delivered to your doorstep.''',
                'tags': 'getting started, beginner, tutorial, setup',
                'is_featured': True
            },
            {
                'title': 'Understanding Product Variants and Pack Sizes',
                'slug': 'product-variants',
                'category': 'products-quality',
                'summary': 'Learn about different pack sizes and how to choose the right variant',
                'content': '''We offer products in multiple pack sizes to suit your needs.

What are Product Variants?
Variants are different pack sizes of the same product. For example, milk is available in 500ml, 1L, and 2L packs.

How to Select a Variant
On the product page, you'll see a dropdown to select pack size. Pricing adjusts automatically based on the selected variant.

Stock Availability
Each variant has separate stock. If one size is out of stock, try another size.

Bulk Discounts
Larger pack sizes often have better unit pricing. Plus, bulk quantity discounts apply automatically!

Tips for Choosing
- For daily use: Choose smaller packs for better freshness
- For families: Larger packs offer better value
- For gifts: We offer special gift packs in premium variants''',
                'tags': 'variants, pack sizes, products, options',
                'is_featured': True
            },
            {
                'title': 'Maximizing Your Loyalty Rewards',
                'slug': 'loyalty-rewards-guide',
                'category': 'loyalty-rewards',
                'summary': 'Pro tips to earn and redeem loyalty points effectively',
                'content': '''Get the most out of our loyalty program with these tips!

Earning Points
- Earn 10 points per ₹100 spent
- Higher tiers get bonus multipliers (up to 1.5x)
- Special promotions offer extra points

Loyalty Tiers
Bronze (0-999 points): 1x multiplier
Silver (1000-2499 points): 1.1x multiplier
Gold (2500-4999 points): 1.25x multiplier
Platinum (5000+ points): 1.5x multiplier

Smart Redemption
- Save points for high-value rewards
- Check the Rewards Shop regularly for special offers
- Some rewards have limited availability

Pro Tips
1. Combine orders to reach bulk discount + earn more points
2. Higher tier = more points earned = faster rewards
3. Redeemed rewards can be combined with other offers
4. Points never expire as long as your account is active

Track Your Progress
Check your Loyalty Dashboard to see your current tier, points balance, and transaction history.''',
                'tags': 'loyalty, rewards, points, tiers, maximize',
                'is_featured': True
            },
            {
                'title': 'Payment Methods and Security',
                'slug': 'payment-security',
                'category': 'payments-pricing',
                'summary': 'Information about payment options and security measures',
                'content': '''Your payment security is our top priority.

Accepted Payment Methods
- Credit/Debit Cards (Visa, Mastercard, RuPay)
- Net Banking (all major banks)
- UPI (GPay, PhonePe, Paytm, etc.)
- Digital Wallets
- Cash on Delivery (COD)

Security Measures
All online payments are processed through Razorpay, a PCI-DSS compliant payment gateway. We never store your card details on our servers.

Why Choose Online Payment?
- Instant order confirmation
- Faster processing
- Exclusive online payment offers
- Digital receipts

Cash on Delivery
COD is available for orders up to ₹2000. A small convenience fee may apply.

Failed Payments
If your payment fails, the amount is automatically refunded within 5-7 business days. You can retry placing the order.

Payment Receipts
All payment receipts are emailed to you and available in your Order History.''',
                'tags': 'payment, security, razorpay, cod, cards',
            },
            {
                'title': 'Quality Assurance and Farm to Table',
                'slug': 'quality-assurance',
                'category': 'products-quality',
                'summary': 'How we ensure the highest quality dairy products',
                'content': '''Our commitment to quality starts at the farm.

Farm Partnerships
We work directly with certified organic farms. All our partner farms follow strict quality protocols and animal welfare standards.

Quality Testing
Every batch undergoes:
- Purity tests
- Pasteurization verification
- Nutritional analysis
- Taste and freshness checks

Cold Chain Management
Products are stored at optimal temperatures from farm to your doorstep. Our delivery vehicles are refrigerated to maintain freshness.

Packaging
We use food-grade, BPA-free packaging. All products are sealed to prevent contamination.

What Makes Our Products Special?
- Milk from grass-fed, free-range cows
- No added preservatives or artificial hormones
- Regular third-party quality audits
- Traceability - know your product source

Quality Guarantee
If you're not satisfied with product quality, we offer 100% refund or replacement within 24 hours of delivery.

Certifications
- FSSAI Licensed
- Organic Certification
- ISO 9001:2015 Quality Management''',
                'tags': 'quality, organic, farm, testing, standards',
            }
        ]

        article_count = 0
        admin_user = User.objects.filter(is_superuser=True).first()

        for article_data in articles_data:
            category_slug = article_data.pop('category')
            article_data['category'] = categories[category_slug]
            article_data['author'] = admin_user

            article, created = HelpArticle.objects.get_or_create(
                slug=article_data['slug'],
                defaults=article_data
            )
            if created:
                article_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Created {article_count} help articles'))
        self.stdout.write(self.style.SUCCESS('FAQ & Help Center initialization complete! 🎉'))
