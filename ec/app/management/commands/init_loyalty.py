from django.core.management.base import BaseCommand
from app.models import LoyaltyTier, Reward

class Command(BaseCommand):
    help = 'Initialize loyalty tiers and sample rewards'
    
    def handle(self, *args, **options):
        # Create loyalty tiers
        tiers = [
            {
                'tier_name': 'BRONZE',
                'min_points': 0,
                'max_points': 99,
                'bonus_multiplier': 1.0,
                'color': '#CD7F32',
                'icon_emoji': '🥉',
                'description': 'Welcome to our loyalty program! Start earning points on every purchase.'
            },
            {
                'tier_name': 'SILVER',
                'min_points': 100,
                'max_points': 499,
                'bonus_multiplier': 1.25,
                'color': '#C0C0C0',
                'icon_emoji': '🥈',
                'description': 'Great! Earn 1.25x points on all purchases and get exclusive offers.'
            },
            {
                'tier_name': 'GOLD',
                'min_points': 500,
                'max_points': 999,
                'bonus_multiplier': 1.5,
                'color': '#FFD700',
                'icon_emoji': '🥇',
                'description': 'Excellent! Earn 1.5x points and enjoy premium member benefits.'
            },
            {
                'tier_name': 'PLATINUM',
                'min_points': 1000,
                'max_points': 9999999,
                'bonus_multiplier': 2.0,
                'color': '#E5E4E2',
                'icon_emoji': '👑',
                'description': 'You are our VIP! Earn 2x points on all purchases + exclusive perks.'
            }
        ]
        
        for tier_data in tiers:
            tier, created = LoyaltyTier.objects.get_or_create(
                tier_name=tier_data['tier_name'],
                defaults={
                    'min_points': tier_data['min_points'],
                    'max_points': tier_data['max_points'],
                    'bonus_multiplier': tier_data['bonus_multiplier'],
                    'color': tier_data['color'],
                    'icon_emoji': tier_data['icon_emoji'],
                    'description': tier_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created {tier_data["tier_name"]} tier'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ {tier_data["tier_name"]} tier already exists'))
        
        # Create sample rewards
        rewards = [
            {
                'name': '10% Discount',
                'description': 'Get 10% off your next purchase',
                'reward_type': 'DISCOUNT',
                'points_required': 100,
                'discount_percentage': 10,
                'max_uses': None,
                'is_active': True
            },
            {
                'name': '₹200 Discount',
                'description': 'Flat ₹200 discount on checkout',
                'reward_type': 'DISCOUNT',
                'points_required': 250,
                'discount_amount': 200,
                'max_uses': None,
                'is_active': True
            },
            {
                'name': 'Free Organic Milk (1L)',
                'description': 'Get a free 1L pack of organic milk',
                'reward_type': 'FREEPRODUCT',
                'points_required': 150,
                'max_uses': 50,
                'is_active': True
            },
            {
                'name': 'Free Shipping',
                'description': 'Free shipping on your next order',
                'reward_type': 'SHIPPING',
                'points_required': 80,
                'max_uses': None,
                'is_active': True
            },
            {
                'name': '20% Discount',
                'description': 'Premium reward - 20% off entire order',
                'reward_type': 'DISCOUNT',
                'points_required': 500,
                'discount_percentage': 20,
                'max_uses': 25,
                'is_active': True
            },
            {
                'name': 'Weekly Plan Upgrade',
                'description': 'Upgrade to our weekly subscription plan free for 1 month',
                'reward_type': 'UPGRADE',
                'points_required': 300,
                'max_uses': None,
                'is_active': True
            }
        ]
        
        for reward_data in rewards:
            reward, created = Reward.objects.get_or_create(
                name=reward_data['name'],
                defaults={
                    'description': reward_data['description'],
                    'reward_type': reward_data['reward_type'],
                    'points_required': reward_data['points_required'],
                    'discount_percentage': reward_data.get('discount_percentage', 0),
                    'discount_amount': reward_data.get('discount_amount', 0),
                    'max_uses': reward_data['max_uses'],
                    'is_active': reward_data['is_active']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created reward: {reward_data["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Reward already exists: {reward_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n✨ Loyalty system initialized successfully!'))
