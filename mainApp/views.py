from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import os
import razorpay
from django.core.mail import send_mail
from django.conf import settings
from OnlineBazar.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from random import randint

from requests import session
from .models import *


def homePage(request):
    products = Product.objects.all()
    products = products[::-1]
    if(request.method == 'POST'):
        try:
            email = request.POST.get("email")
            n = Newslatter()
            n.email = email
            n.save()
        except:
            pass
        return HttpResponseRedirect("/")
    return render(request, "index.html", {"Product": products})


def shopPage(request, mc, sc, br):
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    if(request.method == "POST"):
        search = request.POST.get('search')
        products = Product.objects.filter(Q(name__icontains=search))
    else:
        if(mc == "All" and sc == "All" and br == "All"):
            products = Product.objects.all()
        elif(mc != "All" and sc == "All" and br == "All"):
            products = Product.objects.filter(
                maincategory=Maincategory.objects.get(name=mc))
        elif(mc == "All" and sc != "All" and br == "All"):
            products = Product.objects.filter(
                subcategory=Subcategory.objects.get(name=sc))
        elif(mc == "All" and sc == "All" and br != "All"):
            products = Product.objects.filter(brand=Brand.objects.get(name=br))
        elif(mc != "All" and sc != "All" and br == "All"):
            products = Product.objects.filter(maincategory=Maincategory.objects.get(
                name=mc), subcategory=Subcategory.objects.get(name=sc))
        elif(mc != "All" and sc == "All" and br != "All"):
            products = Product.objects.filter(maincategory=Maincategory.objects.get(
                name=mc), brand=Brand.objects.get(name=br))
        elif(mc == "All" and sc != "All" and br != "All"):
            products = Product.objects.filter(subcategory=Subcategory.objects.get(
                name=sc), brand=Brand.objects.get(name=br))
        else:
            products = Product.objects.filter(maincategory=Maincategory.objects.get(
                name=mc), subcategory=Subcategory.objects.get(name=sc), brand=Brand.objects.get(name=br))

    products = products[::-1]
    return render(request, "shop.html", {"Product": products,
                                         "Maincategory": maincategory,
                                         "Subcategory": subcategory,
                                         "Brand": brand,
                                         "mc": mc, "sc": sc, "br": br
                                         })


def login(request):
    if(request.method == 'POST'):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if(user is not None):
            auth.login(request, user)
            if(user.is_superuser):
                return HttpResponseRedirect("/admin/")
            else:
                return HttpResponseRedirect("/profile/")
        else:
            messages.error(request, "Invalid User Name or Password")
    return render(request, "login.html")


def signup(request):
    if(request.method == "POST"):
        actype = request.POST.get('actype')
        if(actype == "seller"):
            u = Seller()
        else:
            u = Buyer()
        u.name = request.POST.get("name")
        u.username = request.POST.get("username")
        u.email = request.POST.get("email")
        u.phone = request.POST.get("phone")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        if(password == cpassword):
            try:
                user = User.objects.create_user(
                    username=u.username, password=password, email=u.email)
                user.save()
                u.save()
                subject = 'Thanks to Create an Account with US : Team Online Bazar'
                message = """
                                Thanks %s to create an account with US
                                Team : Online Bazar
                                keep shopping with us
                                http://localhost:8000
                        """ % (u.name)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [u.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return HttpResponseRedirect("/login/")
            except:
                messages.success(request, "Your Account is Created!!! Login to Enter!!")
                return HttpResponseRedirect("/login/")
        else:
            messages.error(
                request, "Password and Confirm Password does not matched!!!!")
    return render(request, "signup.html")


@login_required(login_url='/login/')
def profilePage(request):
    user = User.objects.get(username=request.user)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        try:
            seller = Seller.objects.get(username=request.user)
            products = Product.objects.filter(seller=seller)
            products = products[::-1]
            return render(request, "sellerProfile.html", {"User": seller, "Products": products})
        except:
            buyer = Buyer.objects.get(username=request.user)
            wishlist = Wishlist.objects.filter(buyer=buyer)
            checkouts = Checkout.objects.filter(buyer=buyer)
            checkouts = checkouts[::-1]
            return render(request, "buyerProfile.html", {"User": buyer, "Wishlist": wishlist, "Orders": checkouts})


@login_required(login_url='/login/')
def updateProfilePage(request):
    user = User.objects.get(username=request.user)
    if(user.is_superuser):
        return HttpResponseRedirect("/admin/")
    else:
        try:
            user = Seller.objects.get(username=request.user)
        except:
            user = Buyer.objects.get(username=request.user)
        if(request.method == "POST"):
            user.name = request.POST.get('name')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
            user.addressline1 = request.POST.get('addressline1')
            user.addressline2 = request.POST.get('addressline2')
            user.addressline3 = request.POST.get('addressline3')
            user.pin = request.POST.get('pin')
            user.city = request.POST.get('city')
            user.state = request.POST.get('state')
            if(request.FILES.get("pic")):
                if(user.pic and user.pic != "noimage.png"):
                    os.remove("media/"+str(user.pic))
                user.pic = request.FILES.get('pic')
            user.save()
            return HttpResponseRedirect("/profile/")
    return render(request, "updateProfile.html", {"User": user})


@login_required(login_url='/login/')
def addProduct(request):
    maincategory = Maincategory.objects.all()
    subcategory = Subcategory.objects.all()
    brand = Brand.objects.all()
    if(request.method == "POST"):
        p = Product()
        p.name = request.POST.get('name')
        p.maincategory = Maincategory.objects.get(
            name=request.POST.get('maincategory'))
        p.subcategory = Subcategory.objects.get(
            name=request.POST.get('subcategory'))
        p.brand = Brand.objects.get(name=request.POST.get('brand'))
        p.baseprice = int(request.POST.get('baseprice'))
        p.discount = int(request.POST.get('discount'))
        p.finalprice = p.baseprice-p.baseprice*p.discount/100
        color = ""
        if(request.POST.get("Red")):
            color = color+"Red,"
        if(request.POST.get("Green")):
            color = color+"Green,"
        if(request.POST.get("Yellow")):
            color = color+"Yellow,"
        if(request.POST.get("Pink")):
            color = color+"Pink,"
        if(request.POST.get("White")):
            color = color+"White,"
        if(request.POST.get("Black")):
            color = color+"Black,"
        if(request.POST.get("Blue")):
            color = color+"Blue,"
        if(request.POST.get("Brown")):
            color = color+"Brown,"
        if(request.POST.get("SkyBlue")):
            color = color+"SkyBlue,"
        if(request.POST.get("Orange")):
            color = color+"Orange,"
        if(request.POST.get("Navy")):
            color = color+"Navy,"
        if(request.POST.get("Gray")):
            color = color+"Gray,"
        size = ""
        if(request.POST.get("S")):
            size = size+"S,"
        if(request.POST.get("SM")):
            size = size+"SM,"
        if(request.POST.get("M")):
            size = size+"M,"
        if(request.POST.get("L")):
            size = size+"L,"
        if(request.POST.get("XL")):
            size = size+"XL,"
        if(request.POST.get("XXL")):
            size = size+"XXL,"
        if(request.POST.get("XXXL")):
            size = size+"XXXL,"
        p.color = color
        p.size = size
        p.description = request.POST.get('description')
        p.stock = request.POST.get('stock')
        p.pic1 = request.FILES.get('pic1')
        p.pic2 = request.FILES.get('pic2')
        p.pic3 = request.FILES.get('pic3')
        p.pic4 = request.FILES.get('pic4')
        try:
            p.seller = Seller.objects.get(username=request.user)
        except:
            return HttpResponseRedirect("/profile/")
        p.save()
        subject = 'Checkout Our Latest Products on Online Bazar : Team Online Bazar'
        message = """
                        hey!!
                        We upload some more latest products with best offerce
                        please checkout 
                        Team : Online Bazar
                        keep shopping with us
                        http://localhost:8000/single-product-page/%d                    
                """ % (p.id)
        email_from = settings.EMAIL_HOST_USER
        subscribers = Newslatter.objects.all()
        recipient_list = subscribers
        send_mail(subject, message, email_from, recipient_list)
        return HttpResponseRedirect("/profile/")
    return render(request, "addProduct.html", {"Maincategory": maincategory, "Subcategory": subcategory, "Brand": brand})


@login_required(login_url='/login/')
def deleteProduct(request, num):
    try:
        p = Product.objects.get(id=num)
        seller = Seller.objects.get(username=request.user)
        if(p.seller == seller):
            p.delete()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")


@login_required(login_url='/login/')
def editProduct(request, num):
    try:
        p = Product.objects.get(id=num)
        seller = Seller.objects.get(username=request.user)
        if(p.seller == seller):
            maincategory = Maincategory.objects.exclude(name=p.maincategory)
            subcategory = Subcategory.objects.exclude(name=p.subcategory)
            brand = Brand.objects.exclude(name=p.brand)
            if(request.method == "POST"):
                p.name = request.POST.get('name')
                p.maincategory = Maincategory.objects.get(
                    name=request.POST.get('maincategory'))
                p.subcategory = Subcategory.objects.get(
                    name=request.POST.get('subcategory'))
                p.brand = Brand.objects.get(name=request.POST.get('brand'))
                p.baseprice = int(request.POST.get('baseprice'))
                p.discount = int(request.POST.get('discount'))
                p.finalprice = p.baseprice-p.baseprice*p.discount/100
                color = ""
                if(request.POST.get("Red")):
                    color = color+"Red,"
                if(request.POST.get("Green")):
                    color = color+"Green,"
                if(request.POST.get("Yellow")):
                    color = color+"Yellow,"
                if(request.POST.get("Pink")):
                    color = color+"Pink,"
                if(request.POST.get("White")):
                    color = color+"White,"
                if(request.POST.get("Black")):
                    color = color+"Black,"
                if(request.POST.get("Blue")):
                    color = color+"Blue,"
                if(request.POST.get("Brown")):
                    color = color+"Brown,"
                if(request.POST.get("SkyBlue")):
                    color = color+"SkyBlue,"
                if(request.POST.get("Orange")):
                    color = color+"Orange,"
                if(request.POST.get("Navy")):
                    color = color+"Navy,"
                if(request.POST.get("Gray")):
                    color = color+"Gray,"
                size = ""
                if(request.POST.get("S")):
                    size = size+"S,"
                if(request.POST.get("SM")):
                    size = size+"SM,"
                if(request.POST.get("M")):
                    size = size+"M,"
                if(request.POST.get("L")):
                    size = size+"L,"
                if(request.POST.get("XL")):
                    size = size+"XL,"
                if(request.POST.get("XXL")):
                    size = size+"XXL,"
                if(request.POST.get("XXXL")):
                    size = size+"XXXL,"
                p.color = color
                p.size = size
                p.description = request.POST.get('description')
                p.stock = request.POST.get('stock')
                if(request.FILES.get('pic1')):
                    if(p.pic1):
                        os.remove("media/"+str(p.pic1))
                    p.pic1 = request.FILES.get('pic1')
                if(request.FILES.get('pic2')):
                    if(p.pic2):
                        os.remove("media/"+str(p.pic2))
                    p.pic2 = request.FILES.get('pic2')
                if(request.FILES.get('pic3')):
                    if(p.pic3):
                        os.remove("media/"+str(p.pic3))
                    p.pic3 = request.FILES.get('pic3')
                if(request.FILES.get('pic4')):
                    if(p.pic4):
                        os.remove("media/"+str(p.pic4))
                    p.pic4 = request.FILES.get('pic4')
                p.save()
                return HttpResponseRedirect("/profile/")
            return render(request, "editProduct.html", {"Product": p, "Maincategory": maincategory, "Subcategory": subcategory, "Brand": brand})
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")


def singleProductPage(request, num):
    p = Product.objects.get(id=num)
    color = p.color.split(",")
    color = color[:-1]
    size = p.size.split(",")
    size = size[:-1]
    return render(request, "singleProductPage.html", {"Product": p, "Color": color, "Size": size})


def addToWishlist(request, num):
    try:
        buyer = Buyer.objects.get(username=request.user)
        wishlist = Wishlist.objects.filter(buyer=buyer)
        p = Product.objects.get(id=num)
        flag = False
        for i in wishlist:
            if(i.product == p):
                flag = True
                break
        if(flag == False):
            w = Wishlist()
            w.buyer = buyer
            w.product = p
            w.save()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")


@login_required(login_url='/login/')
def deleteWishlist(request, num):
    try:
        w = Wishlist.objects.get(id=num)
        buyer = Buyer.objects.get(username=request.user)
        if(w.buyer == buyer):
            w.delete()
        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")


def addTOCart(request):
    pid = request.POST.get('pid')
    color = request.POST.get('color')
    size = request.POST.get('size')
    cart = request.session.get("cart", None)
    if(cart):
        if(pid in cart.keys() and color == cart[pid][1] and size == cart[pid][2]):
            pass
        else:
            count = len(cart.keys())
            count = count+1
            cart.setdefault(str(count), [pid, 1, color, size])
    else:
        cart = {"1": [pid, 1, color, size]}

    request.session['cart'] = cart
    return HttpResponseRedirect("/cart/")


def cartPage(request):
    cart = request.session.get("cart", None)
    total = 0
    shipping = 0
    final = 0
    if(cart):
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total = total+p.finalprice*values[1]
        if(len(cart.values()) >= 1 and total < 1000):
            shipping = 150
        final = total+shipping
    return render(request, "cart.html", {"Cart": cart, "Total": total, "Shipping": shipping, "Final": final})


def updateCart(request, id, num):
    cart = request.session.get("cart", None)
    if(cart):
        if(num == "-1"):
            if(cart[id][1] > 1):
                q = cart[id][1]
                q = q-1
                cart[id][1] = q
        else:
            q = cart[id][1]
            q = q+1
            cart[id][1] = q

        request.session["cart"] = cart
    return HttpResponseRedirect("/cart/")


def deleteCart(request, id):
    cart = request.session.get("cart", None)
    if(cart):
        cart.pop(id)
        request.session['cart'] = cart
    return HttpResponseRedirect("/cart/")


client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))


@login_required(login_url='/login/')
def checkoutPage(request):
    cart = request.session.get("cart", None)
    total = 0
    shipping = 0
    final = 0
    if(cart):
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total = total+p.finalprice*values[1]
        if(len(cart.values()) >= 1 and total < 1000):
            shipping = 150
        final = total+shipping
    try:
        buyer = Buyer.objects.get(username=request.user)
        if(request.method == "POST"):
            mode = request.POST.get('mode')
            check = Checkout()
            check.buyer = buyer
            check.total = total
            check.shipping = shipping
            check.final = final
            check.save()
            for value in cart.values():
                cp = CheckoutProducts()
                p = Product.objects.get(id=int(value[0]))
                cp.name = p.name
                cp.pic = p.pic1.url
                cp.size = value[3]
                cp.color = value[2]
                cp.price = p.finalprice
                cp.qty = value[1]
                cp.total = p.finalprice*value[1]
                cp.checkout = check
                cp.save()
            request.session['cart'] = {}
            if(mode == "COD"):
                return HttpResponseRedirect("/confirmation/")
            else:
                orderAmount = check.final*100
                orderCurrency = "INR"
                paymentOrder = client.order.create(
                    dict(amount=orderAmount, currency=orderCurrency, payment_capture=1))
                paymentId = paymentOrder['id']
                check.mode = "Net Banking"
                check.save()
                return render(request, "pay.html", {
                    "amount": orderAmount,
                    "api_key": RAZORPAY_API_KEY,
                    "order_id": paymentId,
                    "User": buyer
                })
        return render(request, "checkout.html", {"Cart": cart, "Total": total, "Shipping": shipping, "Final": final, "User": buyer})
    except:
        return HttpResponseRedirect("/profile/")


@login_required(login_url='/login/')
def paymentSuccess(request, rppid, rpoid, rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check = check[::-1]
    check = check[0]
    check.rppid = rppid
    check.rpoid = rpoid
    check.rpsid = rpsid
    check.paymentstatus = 2
    check.save()
    return HttpResponseRedirect('/confirmation/')


@login_required(login_url='/login/')
def paynow(request, num):
    try:
        buyer = Buyer.objects.get(username=request.user)
    except:
        return HttpResponseRedirect("/profile/")

    check = Checkout.objects.get(id=num)
    orderAmount = check.final*100
    orderCurrency = "INR"
    paymentOrder = client.order.create(
        dict(amount=orderAmount, currency=orderCurrency, payment_capture=1))
    paymentId = paymentOrder['id']
    check.save()
    return render(request, "pay.html", {
        "amount": orderAmount,
        "api_key": RAZORPAY_API_KEY,
        "order_id": paymentId,
        "User": buyer
    })


def confirmationPage(request):
    subject = 'Thanks to Shop with US : Team Online Bazar'
    buyer = Buyer.objects.get(username=request.user)
    message = """
                    Thanks %s to Shop with US
                    Team : Online Bazar
                    keep shopping with us
                    http://localhost:8000                    
            """ % (buyer.name)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [buyer.email, ]
    send_mail(subject, message, email_from, recipient_list)
    return render(request, "confirmation.html")


def contactPage(request):
    if(request.method == "POST"):
        c = Contact()
        c.name = request.POST.get("name")
        c.email = request.POST.get("email")
        c.phone = request.POST.get("phone")
        c.subject = request.POST.get("subject")
        c.message = request.POST.get("message")
        c.save()
        subject = 'Your Query Has been Submitted : Team Online Bazar'
        message = """
                        Thanks to Share your Query with us
                        Our Team will Contact You Soon
                        Team : Online Bazar
                        keep shopping with us
                        http://localhost:8000                    
                   """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [c.email, ]
        send_mail(subject, message, email_from, recipient_list)

        messages.success(
            request, "Your Query Has Been Submitted!!!! Our Team Wll Contact You Soon")
    return render(request, "contact.html")


def forgetUsername(request):
    if(request.method == "POST"):
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if(user is not None):
            try:
                user = Buyer.objects.get(username=username)
            except:
                user = Seller.objects.get(username=username)
            num = randint(100000, 999999)
            request.session['otp'] = num
            request.session['user'] = username
            subject = 'OTP for Password Reset : Team Online Bazar'
            message = """
                            OTP : %d
                            Team : Online Bazar
                            keep shopping with us
                            http://localhost:8000                    
                    """ % num
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, message, email_from, recipient_list)
            return HttpResponseRedirect("/forget-otp/")
        else:
            messages.error(request, "User Name not Found")
    return render(request, "forget-username.html")


def forgetOTP(request):
    if(request.method == "POST"):
        otp = int(request.POST.get("otp"))
        sessionOTP = request.session.get('otp', None)
        if(otp == sessionOTP):
            return HttpResponseRedirect("/forget-password/")
        else:
            messages.error(request, "Invalid OTP")
    return render(request, "forget-otp.html")


def forgetPassword(request):
    if(request.method == "POST"):
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        if(password == cpassword):
            user = User.objects.get(username=request.session.get("user"))
            user.set_password(password)
            user.save()
            return HttpResponseRedirect("/login/")
        else:
            messages.error(
                request, "Password and Confirm Password Does't Matched")
    return render(request, "forget-password.html")
