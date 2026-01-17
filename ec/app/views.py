from django.shortcuts import render, redirect
from django.views import View
from . models import Product, Cart, OrderPlaced
from django.db.models import Count
from django.contrib import messages
from .models import ContactMessage
from . forms import CustomerRegistrationForm, CustomerProfileForm, Customer
from django.http import JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings
from .models import Payment


# Create your views here.
def home(request):
    return render(request,"app/home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")


class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request,"app/category.html",locals())
    
class CategoryTitle(View):
    def get(self, request, val):  # ✅ indent everything inside the method
        # Get products matching the title
        product = Product.objects.filter(title=val)

        # Check if product exists to avoid index error
        if product.exists():
            # Get all titles in the same category
            title = Product.objects.filter(category=product[0].category).values('title')
        else:
            title = []

        # Render template with context
        return render(request, "app/category.html", locals())

    

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    

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
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    
    return render(request, 'app/addtocart.html',locals())

class checkout(View):

    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        famount = 0
        for p in cart_items:
            famount += p.quantity * p.product.discounted_price

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
    

def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    #print("payment_done : oid = ",order_id," pid = ",payment_id," cid = ",cust-id)
    user=request.user
    #return redirect("orders")
    customer=Customer.objects.get(id=cust_id)
    #To update payment status and payment id
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    #To save order details
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect("orders")

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')

        cart_item = Cart.objects.filter(
            product_id=prod_id,
            user=request.user
        ).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()

        cart = Cart.objects.filter(user=request.user)

        amount = 0
        for item in cart:
            amount += item.quantity * item.product.discounted_price

        totalamount = amount + 40

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')

        cart_item = Cart.objects.filter(
            product_id=prod_id,
            user=request.user
        ).first()

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
            item.quantity * item.product.discounted_price
            for item in cart
        )

        shipping = 40 if amount > 0 else 0
        totalamount = amount + shipping

        return JsonResponse({
            'quantity': quantity,
            'amount': amount,
            'totalamount': totalamount
        })
   

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')

        Cart.objects.filter(
            product_id=prod_id,
            user=request.user
        ).delete()

        cart = Cart.objects.filter(user=request.user)

        amount = sum(
            item.quantity * item.product.discounted_price
            for item in cart
        )

        shipping = 40 if amount > 0 else 0
        totalamount = amount + shipping

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount
        })
    

