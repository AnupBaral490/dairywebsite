from .models import Cart

def cart_item_count(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
    return {'totalitem': totalitem}
