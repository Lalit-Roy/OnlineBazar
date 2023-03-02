from django import template
from mainApp.models import CheckoutProducts
from mainApp.models import Checkout
register = template.Library()


@register.filter("checkColor")
def checkColor(color, item):
    flag = False
    for i in color.split(","):
        if(i==item):
            flag=True
            break
    return flag

@register.filter("checkSize")
def checkSize(size, item):
    flag = False
    for i in size.split(","):
        if(i==item):
            flag=True
            break
    return flag

@register.filter("orderStatus")
def orderStatus(request, num):
    if(num==0):
        return "Cancelled"
    elif(num==1):
        return "Not Packed"
    elif(num==2):
        return "Packed"
    elif(num==3):
        return "Out For Delivery"
    else:
        return "Delivered"

@register.filter("paymentStatus")
def paymentStatus(request, num):
    if(num==1):
        return "Pending"
    else:
        return "Done"
@register.filter("paymentStatusCon")
def paymentStatusCon(request, num):
    if(num==1):
        return True
    else:
        return False

@register.filter("orderItem")
def orderItem(request, num):
    check = Checkout.objects.get(id=num)
    p = CheckoutProducts.objects.filter(checkout=check)
    return p


@register.filter("Stock")
def Stock(request, data):
    if(data=="In Stock"):
        return True
    else:
        return False
