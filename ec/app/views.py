from django.shortcuts import render, redirect
from django.views import View
from . models import Product, Cart, OrderPlaced, Wishlist, ProductVariant, ProductReview, Farmer, FarmerMessage
from django.db.models import Count, Avg
from django.contrib import messages
from .models import ContactMessage
from . forms import CustomerRegistrationForm, CustomerProfileForm, Customer, ProductReviewForm, FarmerMessageForm
from django.http import JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from .models import Payment
from django.shortcuts import get_object_or_404

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
    for p in cart:
        unit_price = p.variant.discounted_price if p.variant else p.product.discounted_price
        value = p.quantity * unit_price
        amount = amount + value
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
            unit_price = p.variant.discounted_price if p.variant else p.product.discounted_price
            famount += p.quantity * unit_price

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
        item.delete()

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
            amount += item.quantity * item.product.discounted_price

        totalamount = amount + 40
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

        amount = sum(
            item.quantity * (item.variant.discounted_price if item.variant else item.product.discounted_price)
            for item in cart
        )

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

        amount = sum(
            item.quantity * (item.variant.discounted_price if item.variant else item.product.discounted_price)
            for item in cart
        )

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
    

