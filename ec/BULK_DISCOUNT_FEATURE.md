# Bulk Order Discount Feature

## Overview
The bulk order discount feature allows customers to receive automatic discounts when purchasing larger quantities of products. Discounts are applied in tiers based on quantity thresholds.

## Features Implemented

### 1. **BulkDiscount Model**
- Stores discount tiers for each product
- Configurable minimum quantity and discount percentage
- Can be activated/deactivated per tier
- Prevents duplicate tiers with unique_together constraint

### 2. **Automatic Discount Calculation**
- Cart items automatically calculate bulk discounts
- Best applicable discount tier is selected based on quantity
- Shows savings amount to customers

### 3. **Admin Interface**
- Easy management of bulk discounts through Django admin
- Filter by active status and creation date
- Search by product name
- Quick edit for active status

### 4. **Customer-Facing Display**
- Product detail page shows available bulk discount tiers
- Cart page highlights applied discounts
- Shows total savings in cart summary
- Visual indicators for discounted items

## How to Set Up Bulk Discounts

### Step 1: Access Django Admin
1. Go to `http://your-domain/admin/`
2. Login with admin credentials
3. Navigate to **Bulk Discounts** section

### Step 2: Create Discount Tiers
1. Click "Add Bulk Discount"
2. Select a product
3. Set minimum quantity (e.g., 5)
4. Set discount percentage (e.g., 10 for 10% off)
5. Check "Is active" to enable
6. Save

### Example Configuration
For a Milk product, you might create:
- **Tier 1**: Buy 5+ items → 5% OFF
- **Tier 2**: Buy 10+ items → 10% OFF
- **Tier 3**: Buy 20+ items → 15% OFF

## How It Works for Customers

### 1. **Browsing Products**
- Customers see bulk discount information on product detail pages
- Alert box shows all available discount tiers
- Example: "Buy 5+ items and get 5% OFF"

### 2. **Adding to Cart**
- Customers add products with desired quantity
- Discounts automatically apply based on quantity

### 3. **Viewing Cart**
- Green badge shows which items have bulk discounts applied
- Individual item savings displayed
- Total bulk discount savings shown in summary
- Original price shown with strikethrough

### 4. **Checkout**
- Final total reflects all bulk discounts
- Customers pay reduced price automatically

## Technical Details

### Model Fields
```python
class BulkDiscount(models.Model):
    product = ForeignKey to Product
    min_quantity = PositiveIntegerField (minimum to qualify)
    discount_percentage = FloatField (0-100)
    is_active = BooleanField (enable/disable)
    created_at = DateTimeField (tracking)
```

### Cart Calculations
- `unit_price`: Base price per unit
- `bulk_discount`: Best applicable discount tier
- `bulk_discount_amount`: Total discount amount
- `total_cost`: Final price after discount
- `savings`: Total amount saved

### Discount Selection Logic
- System finds all active discounts for the product
- Filters by those where `min_quantity <= cart_quantity`
- Selects highest minimum quantity tier (most generous)
- Calculates and applies discount automatically

## Best Practices

### 1. **Tiered Structure**
- Create progressive tiers (5%, 10%, 15%)
- Ensure higher quantities = higher discounts
- Don't overlap min_quantity values unnecessarily

### 2. **Marketing**
- Promote bulk discounts on homepage
- Highlight savings in product listings
- Send emails about bulk purchase benefits

### 3. **Stock Management**
- Ensure sufficient stock for bulk orders
- Monitor inventory levels for popular bulk items
- Update ProductVariant stock accordingly

### 4. **Seasonal Promotions**
- Temporarily increase discount percentages
- Use is_active flag for quick enable/disable
- Create special bulk deals for holidays

## Testing the Feature

### Manual Testing Steps
1. **Create Bulk Discounts** in admin for a product
2. **Visit Product Page** - verify discount tiers display
3. **Add Quantity** that qualifies for discount
4. **Check Cart** - ensure discount applied and savings shown
5. **Checkout** - verify final price correct
6. **Test Multiple Items** - ensure each calculates independently

### Test Scenarios
- ✅ Quantity below minimum → No discount
- ✅ Quantity at minimum → Discount applies
- ✅ Quantity qualifies for multiple tiers → Highest applies
- ✅ Inactive discounts → Should not apply
- ✅ No discounts configured → Standard pricing
- ✅ Multiple products with different discounts → Each calculated independently

## Database Migration
Already applied: `0011_bulkdiscount.py`
- Created `app_bulkdiscount` table
- Added foreign key to products
- Added unique constraint on (product, min_quantity)

## Future Enhancements (Optional)
- Category-wide bulk discounts
- Time-limited bulk deals
- User-specific bulk pricing (wholesale accounts)
- Bulk discount analytics dashboard
- CSV import for bulk discount setup
- API endpoints for discount management

## Support
For issues or questions:
1. Check Django admin logs
2. Review cart calculations in views
3. Inspect template variable output
4. Check database constraints

## Files Modified
- `models.py` - Added BulkDiscount model and Cart updates
- `admin.py` - Added BulkDiscount admin interface
- `views.py` - Updated show_cart, checkout, ProductDetail
- `addtocart.html` - Display bulk discounts and savings
- `productdetail.html` - Show available bulk discount tiers
- `migrations/0011_bulkdiscount.py` - Database schema

---
**Feature Version**: 1.0
**Last Updated**: February 27, 2026
