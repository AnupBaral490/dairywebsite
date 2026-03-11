from django.shortcuts import render, redirect
from django.views import View
from . models import Product, Cart, OrderPlaced, Wishlist, ProductVariant, ProductReview, Farmer, FarmerMessage
from django.db.models import Count, Avg
from django.contrib import messages
from .models import ContactMessage
from . forms import CustomerRegistrationForm, CustomerProfileForm, Customer, ProductReviewForm, FarmerMessageForm, LoginForm
from django.http import JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from .models import Payment
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomerLoyalty, LoyaltyTier, RewardTransaction, Reward, RedeemHistory
from .models import FAQCategory, FAQ, HelpArticle, LiveChatMessage
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Create your views here.
def home(request):
    # Get latest customer reviews
    reviews = ProductReview.objects.select_related('user', 'product').order_by('-created_at')[:6]
    return render(request,"app/home.html",{'reviews': reviews})

def about(request):
    return render(request, "app/about.html")


def contact(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request,"app/contact.html",locals())


class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            try:
                product = product.filter(discounted_price__gte=float(min_price))
            except ValueError:
                min_price = None
        if max_price:
            try:
                product = product.filter(discounted_price__lte=float(max_price))
            except ValueError:
                max_price = None

        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request,"app/category.html",locals())
    
class CategoryTitle(View):
    def get(self, request, val):  # ✅ indent everything inside the method
        # Get products matching the title
        product = Product.objects.filter(title=val)

        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            try:
                product = product.filter(discounted_price__gte=float(min_price))
            except ValueError:
                min_price = None
        if max_price:
            try:
                product = product.filter(discounted_price__lte=float(max_price))
            except ValueError:
                max_price = None

        # Check if product exists to avoid index error
        if product.exists():
            # Get all titles in the same category
            title = Product.objects.filter(category=product[0].category).values('title')
        else:
            title = []

        # Render template with context
        return render(request, "app/category.html", locals())

    

class ProductDetail(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        variants = list(product.variants.all().order_by('pack_size_value'))
        selected_variant = product.default_variant() or (variants[0] if variants else None)

        wishlist = None
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(
                product=product,
                user=request.user
            ).exists()

        reviews = product.reviews.select_related('user')
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        review_count = reviews.count()
        can_review = request.user.is_authenticated and not reviews.filter(user=request.user).exists()

        recent_ids = request.session.get('recently_viewed', [])
        if product.id in recent_ids:
            recent_ids.remove(product.id)
        recent_ids.insert(0, product.id)
        request.session['recently_viewed'] = recent_ids[:6]
        recent_products = Product.objects.filter(id__in=recent_ids[1:])
        recent_map = {item.id: item for item in recent_products}
        recent_products = [recent_map[item_id] for item_id in recent_ids[1:] if item_id in recent_map]

        recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

        # Get bulk discounts for this product
        bulk_discounts = product.bulk_discounts.filter(is_active=True).order_by('min_quantity')

        return render(request, "app/productdetail.html", {
            'product': product,
            'wishlist': wishlist,
            'variants': variants,
            'selected_variant': selected_variant,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'can_review': can_review,
            'review_form': ProductReviewForm(),
            'farmer_form': FarmerMessageForm(),
            'recent_products': recent_products,
            'recommended_products': recommended_products,
            'bulk_discounts': bulk_discounts,
        })
    

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )

        messages.success(request, "Thank you for contacting us! We will reach out soon.")

    return render(request, "app/contact.html")


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Registration Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, "app/customerregistration.html",locals())


class UserLoginView(LoginView):
    template_name = 'app/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse_lazy('profile')
    
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(
                user=user,
                name=name,
                locality=locality,
                mobile=mobile,
                city=city,
                state=state,
                zipcode=zipcode
            )
            reg.save()
            messages.success(request, "Congratulations! Profile Saved Successfully")
        else:
            messages.warning(request, "Invalid Input Data")

        return render(request, 'app/profile.html', {'form': form})


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile update successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")
    
def add_to_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user=request.user
    product_id=request.GET.get('prod_id')
    variant_id=request.GET.get('variant_id')
    product = Product.objects.get(id=product_id)
    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product,
        variant=variant,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    total_savings = 0
    for p in cart:
        amount = amount + p.total_cost
        total_savings = total_savings + p.savings
    shipping = 40 if amount > 0 else 0
    totalamount = amount + shipping
    
    return render(request, 'app/addtocart.html',locals())

class checkout(View):

    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        famount = 0
        for p in cart_items:
            famount += p.total_cost

        totalamount = famount + 40
        razoramount = int(totalamount * 100)  # in paise

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {
            "amount": razoramount,
            "currency": "INR",
            "receipt": "order_rcptid_12"
        }
        payment_response = client.order.create(data=data)
        print(payment_response)

        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()

        return render(request, 'app/checkout.html', locals())

    def post(self, request):
        # This handles the Razorpay payment callback
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # For project purposes, skip signature verification
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_payment_status = 'paid'
            payment.paid = True
            payment.save()
        except Payment.DoesNotExist:
            # Handle if payment record not found
            return redirect('checkout')  # or show error

        # Optionally, mark orders as placed here
        return redirect('orders')  # replace with your order success page
    

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    # 🔒 Safety check
    if not cust_id:
        messages.error(request, "Please select a shipping address")
        return redirect('checkout')

    user = request.user

    # Get customer & payment safely
    customer = get_object_or_404(Customer, id=cust_id)
    payment = get_object_or_404(Payment, razorpay_order_id=order_id)

    # Update payment info
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()

    # Create orders from cart
    total_amount = 0
    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            payment=payment
        )
        # Use cart total so loyalty points match the discounted amount actually paid.
        total_amount += item.total_cost
        item.delete()

    # Award loyalty points (1 point per rupee)
    try:
        loyalty, created = CustomerLoyalty.objects.get_or_create(user=user)
        loyalty.total_orders += 1
        loyalty.lifetime_purchases += total_amount
        loyalty.last_purchase_date = timezone.now()
        loyalty.save()
        
        # Add points based on purchase amount
        points_earned = loyalty.add_points(int(total_amount))
        messages.success(request, f"✨ Order placed! You earned {points_earned} loyalty points!")
    except Exception as e:
        messages.info(request, "Order placed successfully!")

    return redirect("orders")


def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')

        cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()

        cart = Cart.objects.filter(user=request.user)

        amount = 0
        for item in cart:
            amount += item.total_cost

        shipping = 40 if amount > 0 else 0
        totalamount = amount + shipping

        data = {
            'quantity': cart_item.quantity if cart_item else 0,
            'amount': amount,
            'totalamount': totalamount,
            'shipping': shipping
        }
        return JsonResponse(data)
    

def minus_cart(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')

        cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                quantity = cart_item.quantity
            else:
                cart_item.delete()
                quantity = 0
        else:
            quantity = 0

        cart = Cart.objects.filter(user=request.user)

        amount = sum(item.total_cost for item in cart)

        shipping = 40 if amount > 0 else 0
        totalamount = amount + shipping

        return JsonResponse({
            'quantity': quantity,
            'amount': amount,
            'totalamount': totalamount,
            'shipping': shipping
        })
   

def remove_cart(request):
    if request.method == 'GET':
        cart_id = request.GET.get('cart_id')

        Cart.objects.filter(id=cart_id, user=request.user).delete()

        cart = Cart.objects.filter(user=request.user)

        amount = sum(item.total_cost for item in cart)

        shipping = 40 if amount > 0 else 0
        totalamount = amount + shipping

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount,
            'shipping': shipping
        })


def plus_wishlist(request):
    if request.method == 'GET' and request.user.is_authenticated:
        prod_id = request.GET.get('prod_id')
        product = Product.objects.filter(id=prod_id).first()
        if product:
            Wishlist.objects.get_or_create(user=request.user, product=product)
        return JsonResponse({'message': 'Added to wishlist'})
    return JsonResponse({'message': 'Unauthorized'}, status=401)


def minus_wishlist(request):
    if request.method == 'GET' and request.user.is_authenticated:
        prod_id = request.GET.get('prod_id')
        Wishlist.objects.filter(user=request.user, product_id=prod_id).delete()
        return JsonResponse({'message': 'Removed from wishlist'})
    return JsonResponse({'message': 'Unauthorized'}, status=401)


def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items})


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(composition__icontains=query)
        )
    return render(request, 'app/search.html', {'query': query, 'results': results})


def add_review(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, pk=pk)
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "You already reviewed this product.")
        return redirect('product-detail', pk=pk)

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks for your review!")
        else:
            messages.warning(request, "Please correct the review form.")
    return redirect('product-detail', pk=pk)


def farmer_detail(request, pk):
    farmer = get_object_or_404(Farmer, pk=pk)
    products = farmer.products.all()
    return render(request, 'app/farmer_detail.html', {
        'farmer': farmer,
        'products': products,
        'farmer_form': FarmerMessageForm(),
    })


def contact_farmer(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    farmer = get_object_or_404(Farmer, pk=pk)
    product_id = request.POST.get('product_id')
    product = None
    if product_id:
        product = Product.objects.filter(id=product_id, farmer=farmer).first()

    if request.method == 'POST':
        form = FarmerMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.farmer = farmer
            message.user = request.user
            message.product = product
            message.save()
            if farmer.email:
                subject = message.subject or f"New message about {product.title if product else 'your products'}"
                body_lines = [
                    f"From: {request.user.username}",
                    f"Email: {request.user.email}",
                ]
                if product:
                    body_lines.append(f"Product: {product.title}")
                body_lines.append("")
                body_lines.append(message.message)
                send_mail(
                    subject,
                    "\n".join(body_lines),
                    settings.DEFAULT_FROM_EMAIL,
                    [farmer.email],
                    fail_silently=False,
                )
                if request.user.email:
                    user_subject = "We received your message"
                    user_body_lines = [
                        f"Hi {request.user.username},",
                        "",
                        "Thanks for contacting the farmer. Here is a copy of your message:",
                        "",
                        f"Subject: {subject}",
                    ]
                    if product:
                        user_body_lines.append(f"Product: {product.title}")
                    user_body_lines.append("")
                    user_body_lines.append(message.message)
                    user_body_lines.append("")
                    user_body_lines.append("We will connect you with the farmer soon.")
                    send_mail(
                        user_subject,
                        "\n".join(user_body_lines),
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                    )
                messages.success(request, "Your message was sent to the farmer.")
            else:
                messages.warning(request, "Message saved, but the farmer has no email on file.")
        else:
            messages.warning(request, "Please correct the form and try again.")
    return redirect('farmer-detail', pk=pk)


# Loyalty & Rewards Views

@login_required(login_url='login')
def loyalty_dashboard(request):
    """Display customer loyalty dashboard"""
    customer_loyalty, created = CustomerLoyalty.objects.get_or_create(user=request.user)
    
    # Get transaction history
    transactions = RewardTransaction.objects.filter(loyalty=customer_loyalty).order_by('-created_at')[:10]
    
    # Get all tiers for display
    tiers = LoyaltyTier.objects.all().order_by('min_points')
    
    # Calculate progress to next tier
    current_points = customer_loyalty.total_points
    current_tier = customer_loyalty.current_tier
    
    next_tier = None
    points_to_next = None
    
    if current_tier:
        next_tier = LoyaltyTier.objects.filter(min_points__gt=current_tier.min_points).order_by('min_points').first()
        if next_tier:
            points_to_next = next_tier.min_points - current_points
    
    context = {
        'loyalty': customer_loyalty,
        'transactions': transactions,
        'tiers': tiers,
        'current_points': current_points,
        'next_tier': next_tier,
        'points_to_next': max(0, points_to_next) if points_to_next else None,
        'tier_progress': (current_points / (next_tier.min_points if next_tier else 100)) * 100 if next_tier else 100
    }
    
    return render(request, 'app/loyalty_dashboard.html', context)


@login_required(login_url='login')
def rewards_shop(request):
    """Display available rewards to redeem"""
    customer_loyalty, created = CustomerLoyalty.objects.get_or_create(user=request.user)
    
    # Get all active rewards
    rewards = Reward.objects.filter(is_active=True).order_by('points_required')
    
    # Filter by reward type if specified
    reward_type = request.GET.get('type')
    if reward_type:
        rewards = rewards.filter(reward_type=reward_type)
    
    # Check which rewards the user can afford
    available_rewards = []
    for reward in rewards:
        can_afford = customer_loyalty.total_points >= reward.points_required
        is_available = reward.is_available()
        available_rewards.append({
            'reward': reward,
            'can_afford': can_afford,
            'is_available': is_available
        })
    
    context = {
        'loyalty': customer_loyalty,
        'available_rewards': available_rewards,
        'reward_types': Reward.REWARD_TYPES
    }
    
    return render(request, 'app/rewards_shop.html', context)


@login_required(login_url='login')
def redeem_reward(request, reward_id):
    """Redeem a specific reward"""
    customer_loyalty = CustomerLoyalty.objects.get(user=request.user)
    reward = get_object_or_404(Reward, id=reward_id, is_active=True)
    
    # Check if user can redeem
    if not reward.is_available():
        messages.error(request, "This reward is no longer available.")
        return redirect('rewards-shop')
    
    if customer_loyalty.total_points < reward.points_required:
        messages.error(request, f"You need {reward.points_required - customer_loyalty.total_points} more points.")
        return redirect('rewards-shop')
    
    # Perform redemption
    if customer_loyalty.redeem_points(reward.points_required, reward.name):
        reward.times_used += 1
        reward.save()
        
        # Create redemption history
        RedeemHistory.objects.create(
            customer=request.user,
            reward=reward,
            points_used=reward.points_required
        )
        
        messages.success(request, f"🎉 Successfully redeemed {reward.name}! Check your email for details.")
        
        # Send email to user
        email_body = f"""
Hello {request.user.first_name or request.user.username},

Congratulations! You've successfully redeemed: {reward.name}

Points Used: {reward.points_required}
Remaining Points: {customer_loyalty.total_points}

Details: {reward.description}

Thank you for being a loyal customer!

Best regards,
Fresh Dairy Team
        """
        
        send_mail(
            f"Reward Redeemed: {reward.name}",
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True,
        )
    else:
        messages.error(request, "Redemption failed. Please try again.")
    
    return redirect('rewards-shop')


@login_required(login_url='login')
def my_rewards(request):
    """Display user's redeemed rewards history"""
    redeemed = RedeemHistory.objects.filter(customer=request.user).order_by('-redeemed_at')
    
    context = {
        'redeemed_rewards': redeemed,
        'total_redeemed': redeemed.count()
    }
    
    return render(request, 'app/my_rewards.html', context)


# FAQ & Help Center Views

def faq_center(request):
    """Main FAQ page with categories and search"""
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    
    # Get all active categories
    categories = FAQCategory.objects.filter(is_active=True)
    
    # Filter FAQs
    faqs = FAQ.objects.filter(is_active=True)
    
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) | 
            Q(answer__icontains=search_query)
        )
    
    if category_slug:
        faqs = faqs.filter(category__slug=category_slug)
    
    # Get featured FAQs if no search/filter
    featured_faqs = None
    if not search_query and not category_slug:
        featured_faqs = FAQ.objects.filter(is_active=True, is_featured=True)[:5]
    
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    context = {
        'categories': categories,
        'faqs': faqs,
        'featured_faqs': featured_faqs,
        'search_query': search_query,
        'selected_category': category_slug,
        'totalitem': totalitem,
    }
    
    return render(request, 'app/faq_center.html', context)


def faq_detail(request, faq_id):
    """View single FAQ with helpful feedback"""
    faq = get_object_or_404(FAQ, id=faq_id, is_active=True)
    faq.increment_view()
    
    # Handle helpful feedback
    if request.method == 'POST' and request.user.is_authenticated:
        feedback = request.POST.get('feedback')
        if feedback == 'helpful':
            faq.helpful_count += 1
            faq.save()
            messages.success(request, "Thank you for your feedback!")
        elif feedback == 'not_helpful':
            faq.not_helpful_count += 1
            faq.save()
            messages.info(request, "Thanks for letting us know. We'll improve this answer.")
        return redirect('faq-detail', faq_id=faq.id)
    
    # Get related FAQs
    related_faqs = FAQ.objects.filter(
        category=faq.category, 
        is_active=True
    ).exclude(id=faq.id)[:3]
    
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    context = {
        'faq': faq,
        'related_faqs': related_faqs,
        'totalitem': totalitem,
    }
    
    return render(request, 'app/faq_detail.html', context)


def help_center(request):
    """Help center with articles"""
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    tag = request.GET.get('tag', '')
    
    # Get published articles
    articles = HelpArticle.objects.filter(is_published=True)
    
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    
    if tag:
        articles = articles.filter(tags__icontains=tag)
    
    # Get featured articles
    featured_articles = None
    if not search_query and not category_slug and not tag:
        featured_articles = HelpArticle.objects.filter(
            is_published=True, 
            is_featured=True
        )[:3]
    
    # Get categories
    categories = FAQCategory.objects.filter(is_active=True)
    
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    context = {
        'articles': articles,
        'featured_articles': featured_articles,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_tag': tag,
        'totalitem': totalitem,
    }
    
    return render(request, 'app/help_center.html', context)


def help_article_detail(request, slug):
    """View single help article"""
    article = get_object_or_404(HelpArticle, slug=slug, is_published=True)
    article.increment_view()
    
    # Handle helpful feedback
    if request.method == 'POST' and request.user.is_authenticated:
        feedback = request.POST.get('feedback')
        if feedback == 'helpful':
            article.helpful_count += 1
            article.save()
            messages.success(request, "Glad we could help!")
        elif feedback == 'not_helpful':
            article.not_helpful_count += 1
            article.save()
            messages.info(request, "We appreciate your feedback and will improve this article.")
        return redirect('help-article-detail', slug=article.slug)
    
    # Get related articles
    related_articles = HelpArticle.objects.filter(
        is_published=True
    ).exclude(id=article.id)
    
    if article.category:
        related_articles = related_articles.filter(category=article.category)[:3]
    else:
        related_articles = related_articles[:3]
    
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'totalitem': totalitem,
    }
    
    return render(request, 'app/help_article_detail.html', context)


# Live Chat Views

def live_chat(request):
    """Live chat interface with professional chatbot features"""
    import uuid
    import json
    from django.http import JsonResponse
    
    # Get or create session ID
    session_id = request.session.get('chat_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = session_id
    
    # Handle message submission
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            msg = LiveChatMessage.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                name=request.POST.get('name', ''),
                email=request.POST.get('email', ''),
                message=message_text,
                is_staff_message=False
            )
            
            # Check for common queries and auto-respond
            auto_response = check_and_generate_auto_response(message_text)
            if auto_response:
                # Create auto-response message
                LiveChatMessage.objects.create(
                    session_id=session_id,
                    user=None,
                    message=auto_response,
                    is_staff_message=True
                )
            
            return JsonResponse({'success': True, 'message_id': msg.id})
    
    # Get messages for this session
    messages_list = LiveChatMessage.objects.filter(session_id=session_id)
    
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    
    context = {
        'chat_messages': messages_list,
        'session_id': session_id,
        'totalitem': totalitem,
    }
    
    return render(request, 'app/live_chat.html', context)


def check_and_generate_auto_response(message_text):
    """Generate auto-response for common queries"""
    message_lower = message_text.lower().strip()
    
    # Don't auto-respond to very short messages that might be greetings
    if len(message_lower) <= 2:
        return None
    
    # Common queries and responses
    auto_responses = {
        'shipping': {
            'keywords': ['shipping', 'delivery', 'how long', 'when will', 'how many days', 'delivery time'],
            'response': 'Thank you for your inquiry! We offer multiple shipping options with standard and express delivery. Shipping times typically range from 2-7 business days depending on your location. You can track your order in real-time through your account dashboard. Is there anything specific about shipping you\'d like to know?'
        },
        'return': {
            'keywords': ['return', 'refund', 'exchange', 'return policy', 'send back'],
            'response': 'Great question! We have a hassle-free 30-day return policy. If you\'re not satisfied with your purchase, you can initiate a return through your account. Please ensure the item is in its original condition with all original packaging. Our team will process your return within 5-7 business days. Would you like help starting a return?'
        },
        'payment': {
            'keywords': ['payment', 'pay', 'credit card', 'debit', 'upi', 'wallet', 'payment method', 'card'],
            'response': 'We accept all major credit cards, debit cards, digital wallets (Google Pay, Apple Pay), and net banking options. All your transactions are encrypted with bank-level security. If you\'re experiencing any payment issues, I\'m here to help! What specific issue are you facing?'
        },
        'order': {
            'keywords': ['order', 'my order', 'order status', 'track', 'tracking', 'where is my'],
            'response': 'You can check your order status anytime by visiting your account dashboard and clicking "My Orders". You\'ll receive email updates at each stage - from confirmation to dispatch, and finally delivery. Each order has a tracking number for real-time updates. Can I help you with a specific order?'
        },
        'product': {
            'keywords': ['product', 'item', 'size', 'color', 'available', 'stock', 'in stock', 'recommendation'],
            'response': 'We have a wide range of products across multiple categories. You can browse by category, use our search feature, or check trending items. If you need specific product recommendations or have questions about a particular item, I\'m happy to help! What are you looking for?'
        },
        'account': {
            'keywords': ['account', 'password', 'reset', 'login', 'sign up', 'register', 'profile', 'my profile'],
            'response': 'Managing your account is easy! You can update your profile information, manage addresses, view order history, and more from your dashboard. For security-related questions like password resets, we can guide you step-by-step. What would you like to know about your account?'
        },
        'discount': {
            'keywords': ['discount', 'coupon', 'promo', 'code', 'offer', 'sale', 'special price'],
            'response': 'We regularly offer special discounts and promotions! Check your email for exclusive deals, browse our "Offers" section, and apply coupon codes at checkout. Loyalty members get extra rewards and early access to sales. Would you like information about our current promotions?'
        },
        'contact': {
            'keywords': ['contact', 'email', 'phone', 'call', 'customer service', 'reach you'],
            'response': 'You can reach us through multiple channels - live chat (here!), email at support@yourdomain.com, or visit our Help Center for FAQs. We typically respond within minutes during business hours. Is there something specific I can help you with right now?'
        },
        'help': {
            'keywords': ['can you help', 'need help', 'help me', 'assistance', 'support'],
            'response': 'Absolutely! I\'m here to help. Could you please tell me more about what you need assistance with? Whether it\'s about an order, product information, returns, or anything else, I\'m happy to help guide you through it!'
        }
    }
    
    # Check for keyword matches
    for category, data in auto_responses.items():
        for keyword in data['keywords']:
            if keyword in message_lower:
                return data['response']
    
    # Don't auto-respond to very short messages
    return None


def live_chat_messages(request):
    """AJAX endpoint to get new messages with enhanced data"""
    session_id = request.session.get('chat_session_id')
    if not session_id:
        return JsonResponse({'messages': []})
    
    last_message_id = request.GET.get('last_id', 0)
    
    new_messages = LiveChatMessage.objects.filter(
        session_id=session_id,
        id__gt=last_message_id
    ).order_by('id')
    
    messages_data = [{
        'id': msg.id,
        'message': msg.message,
        'is_staff': msg.is_staff_message,
        'created_at': msg.created_at.strftime('%H:%M'),
        'sender': msg.user.username if msg.user else (msg.name or 'Support Agent'),
        'timestamp': msg.created_at.isoformat()
    } for msg in new_messages]
    
    return JsonResponse({'messages': messages_data, 'total': new_messages.count()})

