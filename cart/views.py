from django.urls import reverse
from django.utils import timezone
import json
from django.shortcuts import get_object_or_404, render,redirect
from django.views.generic import View
from .models import *
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .forms import *
from django. contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.core.paginator import Paginator, Page
from django.views.decorators.csrf import csrf_exempt
import random
import uuid
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.sessions.backends.db import SessionStore

from wkhtmltopdf.views import PDFTemplateResponse
from django.template.loader import get_template
from django.db.models import Q
from django.views.decorators.http import require_GET


# Create your views here.



# ----------- CART SECTION ---------------


def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False,defaults=0)
        items = order.orderitem_set.all()
        num_of_item = order.get_cart_items
    else:
        
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print(cart)
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        num_of_item = order['get_cart_items']

        for i in cart:
            
            num_of_item += int(cart[i]["quantity"])

            product = Product.objects.get(id = i)
            total = (product.selling_price * int(cart[i]["quantity"]))

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]["quantity"]
            msg = ""
            if(cart[i]["quantity"] > product.quantity ):
                cart[i]["quantity"] = product.quantity
                msg = "Only this items left"

            item = {
                'product':{
                    'id': product.id,
                    'name': product.name,
                    'product_image':{
                        'url' : product.product_image.url
                    },
                    'quantity':product.quantity,
                    'selling_price':product.selling_price,
                },
                'quantity': cart[i]["quantity"],
                'get_total': total,
                'msg': msg
            }
            items.append(item)

    context = {'items': items, 'order':order, 'num_of_items': num_of_item}
    return render(request, 'cart/cart.html', context)



def add_to_cart(request):
    
    data = json.loads(request.body)
    
    product_id = data["id"]
    product = Product.objects.get(id=product_id)
    
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer = request.user, complete = False)
        orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)
        if(product.quantity > orderItem.quantity):
           
            product.is_available = True
            orderItem.quantity += 1
            orderItem.save()
            product.save()
            print(product.quantity)
            num_of_item = order.get_cart_items
            return JsonResponse({'num_of_items':num_of_item,'msg':"Product added successfully"})
        else:
            if(created == True):
                orderItem.delete()
            product.is_available = True
            product.save()
            
            return JsonResponse({'status':'Out Of Stock'})


def updatecart(request):
    if request.method == "POST":
            if request.user.is_authenticated:
                prod_id = int(request.POST.get('product_id'))
                product = Product.objects.get(id = prod_id)
                order,created = Order.objects.get_or_create(customer = request.user, complete = False)
                orderItem, created = OrderItem.objects.get_or_create(order = order, product = prod_id)
                if (created == False):
                   
                    prod_qty = int(request.POST.get('product_qty'))
                    action = request.POST.get('action')
                    
                    

                    if product.quantity > orderItem.quantity:
                        order = Order.objects.get(customer = request.user,complete = False)
                        orderItem = OrderItem.objects.get(order = order, product = prod_id)
                        
                        # if (action == "add"):
                        #     product.quantity-=1
                        # elif(action == "subtract"):
                        #     product.quantity+=1
                        orderItem.quantity = prod_qty
                        orderItem.save()
                        order.save()
                        
                        product.save()
                        num_of_item = order.get_cart_items
                        return JsonResponse({"status":"updated successfully", 'num_of_items':num_of_item,'value':True, 'product_quantity':product.quantity})
                    else:
                        if(action == 'subtract'):
                            orderItem.quantity = prod_qty
                            orderItem.save()
                            order.save()
                            product.save()
                        num_of_item = order.get_cart_items
                        return JsonResponse({'status': product.quantity,  'num_of_items':num_of_item,'items_left':"Only "+ str(product.quantity) })
                return JsonResponse({'status':'created successfully'})

def deletecart(request):
    if request.method == "POST":
        prod_id = int(request.POST.get('product_id'))
        order,created = Order.objects.get_or_create(customer = request.user, complete = False)
        orderItem, created = OrderItem.objects.get_or_create(order = order, product = prod_id)
        
        if (created == False):
            orderItem.delete()
            num_of_item = order.get_cart_items
            return JsonResponse({"status":"Deleted successfully",'num_of_items':num_of_item})
    return redirect('/')

# ------------- CART SECTION ENDING ----------------




# ------------- SHOP SECTION ---------------------


def shop(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        num_of_item = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print(cart)
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        num_of_item = order['get_cart_items']

        for i in cart:
            num_of_item += cart[i]["quantity"]

    brand = Brand.objects.all()
    category = Category.objects.all()
    products = Product.objects.all().order_by('id')
    newest = Product.objects.filter(trending = True)
    minMaxPrice = Product.objects.aggregate(Min('selling_price'), Max('original_price'))
    
    paginator = Paginator(products, 3) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    totalpage = page_obj.paginator.num_pages
    print(minMaxPrice)

    context = {'products':page_obj, 'num_of_items': num_of_item, 'newest': newest, 'cats':category, 'brands': brand, 'minMaxPrice':minMaxPrice,
        'page_number': page_number,
        'totalPageList':[n+1 for n in range(totalpage)],
        'total_pages': paginator.num_pages}
    return render(request, 'user/shop.html',context)


def filter_data(request):
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    
    minPrice = request.GET['minPrice']
    maxPrice = request.GET['maxPrice']
    print(maxPrice)
    allProducts = Product.objects.all()
    allProducts = allProducts.filter(selling_price__gte = minPrice)
    allProducts = allProducts.filter(selling_price__lte = maxPrice)
    print(allProducts)
    if len(categories)>0:
        allProducts = allProducts.filter(category__id__in = categories).distinct()
        print(allProducts)
    if len(brands)>0:
        allProducts = allProducts.filter(brand__id__in = brands).distinct()
    print(allProducts)
    
    t = render_to_string('cart/product_list.html', {'data':allProducts})
   

    
    return JsonResponse({'data':t})

def search(request):
    q = request.GET['q']
    data = Product.objects.filter(name__icontains=q).order_by('id')
    return render(request, 'cart/search.html', {'data': data})

@require_GET
def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    # Perform the search using the query parameter
    suggestions = Product.objects.filter(name__icontains=query)[:10]

    # Return a JSON response with the search suggestions
    return JsonResponse({'suggestions': [obj.name for obj in suggestions]})



# ------------ SHOP SECTION ENDING --------------




# -------------- WISHLIST SECTION ---------------


def addtowishlist(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            product_check = Product.objects.get(id= prod_id)
            if(product_check):
                wishlist, created = WishList.objects.get_or_create(customer = request.user)
                
                wishlistitems, created = WishlistItem.objects.get_or_create(wishlist = wishlist, product = product_check)
                if (created == False):
                    return JsonResponse({"status":"Product already in wishlist"})
                else:
                    return JsonResponse({"status":"Product added to wishlist"})
                
            else:
                return JsonResponse({"status":"No such product found"})

        else:
            return JsonResponse({"status":"Login to Continue"})
    return redirect('/')

@login_required(login_url='user_login')
def wishlist(request):
    if request.user.is_authenticated:
        customer = request.user
        wishlist, created = WishList.objects.get_or_create(customer = customer)
        items = wishlist.wishlistitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    context = {'items': items, 'wishlist':wishlist}
    
    return render(request, 'cart/wishlist.html', context)

def deletewishlist(request):
    if request.method == "POST":
        prod_id = int(request.POST.get('product_id'))
        wishlist,created = WishList.objects.get_or_create(customer = request.user)
        wishlistItem, created = WishlistItem.objects.get_or_create(wishlist = wishlist, product = prod_id)
        if (created == False):
            wishlistItem.delete()
            return JsonResponse({"status":"Deleted successfully"})
    return redirect('/')


#-------- WISHLIST ENDING ------------


# -----------PAYMENT SECTION ------------

def payment(request):
    body = json.loads(request.body)
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.filter(product__is_available=True)
    coupon_id = request.session.get('coupon_id')
    billing_address_id = request.session.get('billing_address_id')
    shipping_address_id = request.session.get('shipping_address_id')

    try:
        default_address = BillingAddress.objects.get(customer = request.user, status=True)
        billing_form = BillingAddressForm(instance=default_address)
        shipping_form = ShippingAddressForm(instance = default_address)
    except BillingAddress.DoesNotExist:
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
    
    if billing_address_id:
        try:
            default_address = BillingAddress.objects.get(id = billing_address_id)
        except:
            print("billing address is not in session")

    if shipping_address_id:
        try:
            shipping_address = ShippingAddress.objects.get(id = shipping_address_id)
        except:
            print("shipping address is not in session")
    else:
        shipping_address = ShippingAddress()
        shipping_address.email = default_address.email
        shipping_address.phone_number = default_address.phone_number
        shipping_address.country = default_address.country
        shipping_address.state = default_address.state
        shipping_address.city = default_address.city
        shipping_address.address = default_address.address
        shipping_address.district = default_address.district
        shipping_address.pincode = default_address.pincode
        shipping_address.save()

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id = coupon_id)
            discount = coupon.discount
        except Coupon.DoesNotExist:
            discount = 0
    else:
        discount = 0

    order = Orders.objects.create(customer=request.user)
    total = cart.get_cart_total - discount
    
    order.billing_address = default_address
    order.shipping_address = shipping_address

    
    order.total_price = total
    for item in cart_items:
        OrderedItems.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.selling_price)
    cart_items.delete()

    

    request.session['order_id'] = order.id
    
    payment = Payment(
        user = request.user, 
        payment_id = body['transID'],
        payment_mode = body['payment_method'],
        total_amount = order.total_price,
        status = body['status'],

      
    )
    payment.save()
    order.payment = payment
    
    order.save()



def wallet_payment(request):
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.filter(product__is_available=True)
    coupon_id = request.session.get('coupon_id')
    billing_address_id = request.session.get('billing_address_id')
    shipping_address_id = request.session.get('shipping_address_id')

    wallet, created = Wallet.objects.get_or_create(user = request.user)
    if(wallet.balance == None):
        wallet.balance = 0
    if(wallet.balance >= cart.total_price):

    
        try:
            default_address = BillingAddress.objects.get(customer = request.user, status=True)
            billing_form = BillingAddressForm(instance=default_address)
            shipping_form = ShippingAddressForm(instance = default_address)
        except BillingAddress.DoesNotExist:
            billing_form = BillingAddressForm()
            shipping_form = ShippingAddressForm()
        
        if billing_address_id:
            try:
                default_address = BillingAddress.objects.get(id = billing_address_id)
            except:
                print("billing address is not in session")
        

        if shipping_address_id:
            try:
                shipping_address = ShippingAddress.objects.get(id = shipping_address_id)
            except:
                print("shipping address is not in session")
        else:
            shipping_address = ShippingAddress()
            shipping_address.email = default_address.email
            shipping_address.phone_number = default_address.phone_number
            shipping_address.country = default_address.country
            shipping_address.state = default_address.state
            shipping_address.city = default_address.city
            shipping_address.address = default_address.address
            shipping_address.district = default_address.district
            shipping_address.pincode = default_address.pincode
            shipping_address.save()

        
        

        order = Orders.objects.create(customer=request.user)
        total = cart.total_price
        order.billing_address = default_address
        order.shipping_address = shipping_address
        order.total_price = total
        
        for item in cart_items:
            product_quantity(id=item.product.id, quantity=item.quantity)

        for item in cart_items:
            OrderedItems.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.selling_price)
        cart_items.delete()

        payment = Payment(
            user = request.user, 
            payment_id = str(uuid.uuid4()),
            payment_mode = "Wallet",
            total_amount = order.total_price, 
            status = "Pending",

        
        )
        payment.save()
        order.payment = payment
        order.save()

        request.session['order_id'] = order.id
        wallet.balance -= order.total_price
        wallet.save()
        return JsonResponse({'status':"Your Order Has been placed successfully"})
    
    else:

        return JsonResponse({'status': "Not enough balance in your wallet", "failure":True})



        

def cash_on_delivery(request):
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.filter(product__is_available=True)
    coupon_id = request.session.get('coupon_id')
    billing_address_id = request.session.get('billing_address_id')
    shipping_address_id = request.session.get('shipping_address_id')

    
    try:
        default_address = BillingAddress.objects.get(customer = request.user, status=True)
        billing_form = BillingAddressForm(instance=default_address)
        shipping_form = ShippingAddressForm(instance = default_address)
    except BillingAddress.DoesNotExist:
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
    
    if billing_address_id:
        try:
            default_address = BillingAddress.objects.get(id = billing_address_id)
        except:
            print("billing address is not in session")
    

    if shipping_address_id:
        try:
            shipping_address = ShippingAddress.objects.get(id = shipping_address_id)
        except:
            print("shipping address is not in session")
    else:
        shipping_address = ShippingAddress()
        shipping_address.email = default_address.email
        shipping_address.phone_number = default_address.phone_number
        shipping_address.country = default_address.country
        shipping_address.state = default_address.state
        shipping_address.city = default_address.city
        shipping_address.address = default_address.address
        shipping_address.district = default_address.district
        shipping_address.pincode = default_address.pincode
        shipping_address.save()


    order = Orders.objects.create(customer=request.user)
    total = cart.total_price
    order.billing_address = default_address
    order.shipping_address = shipping_address
    order.total_price = total
    
    for item in cart_items:
        product_quantity(id=item.product.id, quantity=item.quantity)

    for item in cart_items:
        OrderedItems.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.selling_price)
    cart_items.delete()

    payment = Payment(
        user = request.user, 
        payment_id = str(uuid.uuid4()),
        payment_mode = "COD",
        total_amount = order.total_price, 
        status = "Pending",

      
    )
    payment.save()
    order.payment = payment
    order.save()

    request.session['order_id'] = order.id
    return redirect(order_confirmation)

def beforerazorpay(request):
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.all()

    total = cart.total_price
    customer = request.user.username
    return JsonResponse({
        'total_price': total,
        
        'user': customer,
    })

def razorpay(request):
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.filter(product__is_available=True)
    coupon_id = request.session.get('coupon_id')
    billing_address_id = request.session.get('billing_address_id')
    shipping_address_id = request.session.get('shipping_address_id')

    
    try:
        default_address = BillingAddress.objects.get(customer = request.user, status=True)
        billing_form = BillingAddressForm(instance=default_address)
        shipping_form = ShippingAddressForm(instance = default_address)
    except BillingAddress.DoesNotExist:
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
    
    if billing_address_id:
        try:
            default_address = BillingAddress.objects.get(id = billing_address_id)
        except:
            print("billing address is not in session")
    

    if shipping_address_id:
        try:
            shipping_address = ShippingAddress.objects.get(id = shipping_address_id)
        except:
            print("shipping address is not in session")
    else:
        shipping_address = ShippingAddress()
        shipping_address.email = default_address.email
        shipping_address.phone_number = default_address.phone_number
        shipping_address.country = default_address.country
        shipping_address.state = default_address.state
        shipping_address.city = default_address.city
        shipping_address.address = default_address.address
        shipping_address.district = default_address.district
        shipping_address.pincode = default_address.pincode
        shipping_address.save()

    print(shipping_address)
    
    order = Orders.objects.create(customer=request.user)
    total = cart.total_price
    order.billing_address = default_address
    order.shipping_address = shipping_address
    order.total_price = total
    
    

    for item in cart_items:
        OrderedItems.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.selling_price)
    cart_items.delete()

    
    payment_mode = request.POST.get('payment_mode')
    payment_id = request.POST.get('payment_id')
    payment = Payment(
        user = request.user, 
        payment_id = payment_id,
        payment_mode = payment_mode,
        total_amount = order.total_price, 
        status = "Pending",

      
    )
    payment.save()
    order.payment = payment
    order.save()

    return JsonResponse({'status':"Your Order Has been placed successfully"})

# ------------ PAYMENT SECTION ENDING -------------



#---------- ORDER SECTION -------------

def checkout_guest(request):
    if not request.user.is_authenticated:
        # Store the current URL to redirect the user back to the checkout page
        request.session['checkout_redirect'] = request.path
        return redirect('/user_login') # Replace 'login' with the name of your login view
    else:
        cart, created = Order.objects.get_or_create(customer=request.user)

    # Add cart items from cookies to the user's cart
        try:
            cart_cookie = json.loads(request.COOKIES.get('cart'))
            print(cart_cookie)
            for item in cart_cookie:
                if item:
                    quantity = cart_cookie[item]["quantity"]
                    print(quantity, item)
                    product = Product.objects.get(id = item)
                    cart_item, created = OrderItem.objects.get_or_create(order=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
        except:
            pass

        response = redirect(place_order)
        if(response.delete_cookie('cart')):
            response.delete_cookie('cart')
        return response

@login_required(login_url='user_login')
def place_order(request):
    cart = Order.objects.get(customer=request.user)
    cart_items = cart.orderitem_set.filter(product__is_available=True)
    print(cart_items)
    coupon_id = request.session.get('coupon_id')

    if not cart_items.exists():
        return redirect('cart')
    
    billing_address_id = request.session.get('billing_address_id')
    shipping_address_id = request.session.get('shipping_address_id')
    
    if not billing_address_id:
        try:
            default_address = BillingAddress.objects.get(customer = request.user, status=True)
            billing_form = BillingAddressForm(instance=default_address)
            shipping_form = ShippingAddressForm(instance = default_address)
        except BillingAddress.DoesNotExist:
            billing_form = BillingAddressForm()
            shipping_form = ShippingAddressForm()
            return redirect(address)
    


    if billing_address_id:
        try:
            default_address = BillingAddress.objects.get(id = billing_address_id)
        except:
            print("billing address is not in session")

    if shipping_address_id:
        try:
            shipping_address = ShippingAddress.objects.get(id = shipping_address_id)
        except:
            print("shipping address is not in session")

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id = coupon_id)
            discount = coupon.discount
            
        except Coupon.DoesNotExist:
            discount = 0
    else:
        discount = 0

    

    if 'coupon_id' in request.session:
        del request.session['coupon_id']

    customer = request.user
    order, created = Order.objects.get_or_create(customer = customer, complete = False,defaults=0)
    items = order.orderitem_set.filter(product__is_available=True)
    total = sum([item.get_total for item in items])
    if total == None:
            total = 0
    
    order.total_price = total
    print(order.total_price)
    order.total_price -= discount
    
    
    num_of_item = order.get_cart_items
    
    order.save()

    context = {'items': items, 'order':order, 'coupon_form': CouponForm(), 'discount': discount, 'address': default_address, 'num_of_items':num_of_item}
    return render(request, 'cart/checkout.html',context)

def order_confirmation(request):
    orders = Orders.objects.filter(customer=request.user).order_by('created_at').last()
    order_items = OrderedItems.objects.filter(order = orders.id)
    
    context = {'orders': orders, 'billing_address': orders.billing_address, 'shipping_address':orders.shipping_address,
                'ordered_items':order_items,'order-total':orders.get_order_total, 'order-items-total':orders.get_cart_items}
    return render(request, 'cart/confirmation.html', context)

@login_required(login_url='user_login')
def order_summary(request):
    orders = Orders.objects.filter(customer=request.user).order_by("-created_at")
    context = {'orders': orders}
    return render(request, 'cart/order_summary.html', context)

def order_details(request, id):
    order = Orders.objects.get( id = id)
    order_items = OrderedItems.objects.filter(order = id)
    return render(request, 'cart/order_details.html',{'order_items':order_items, 'orders': order, 'id':id})


def cancel_order(request, id):

    order = get_object_or_404(Orders, id= id)
    order.status = 'Cancelled'
    order.cancelled = True
    order.save()
    return redirect(order_summary)

def initiate_return(request, order_id, product_id):
    order = Orders.objects.get(id=order_id)
    if order.customer != request.user:
        return redirect("home")

    
    if request.method == "POST":
        form = ReturnForm(request.POST)
        if form.is_valid():
            product_id = product_id
            product = Product.objects.get(id=product_id)
            orderItem = OrderedItems.objects.get(order = order, product = product)
            reason = form.cleaned_data["reason"]
            new_return = Return(
                order=order,
                product=orderItem,
                reason=reason,
                status="pending",
                user=request.user
            )
            new_return.save()
            order.status = "Return Requested"
            orderItem.status = "Return Requested"
            orderItem.save()
            order.save()
            return redirect(order_details, id=order_id)
    else:
        form = ReturnForm()
        product = Product.objects.get(id=product_id)
        orderItem = OrderedItems.objects.get(order = order, product = product)
        form.product = orderItem
        print(orderItem.product)
    return render(request, "cart/return_product.html", {"order": order, "form": form, 'order_item':orderItem})

def invoice(request, order_id, product_id):
    order = Orders.objects.get( id = order_id)
    product = Product.objects.get(id = product_id)
    order_item = OrderedItems.objects.get(order = order, product = product)
    discount = order.get_order_total - order.total_price
    print(discount)
    context = { 'orders': order, 'id':order_id, 'order_item': order_item , 'discount':discount}
    return render(request, 'cart/invoice.html', context)


#-------- ORDER SECTION ENDING -------------


def process_payment(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % order.total_cost().quantize(
            Decimal('.01')),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment/process_payment.html', {'order': order, 'form': form})


@csrf_exempt
def payment_done(request):
    return render(request, 'payment/payment_done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/payment_cancelled.html')



#------------ ADDRESS SECTION --------------

def add_address(request):
    msg = ""
    
    if request.method == 'POST':
        form =BillingAddressForm(request.POST)
        if form.is_valid():
        
            saveForm = form.save(commit= False)
            saveForm.customer = request.user
            if (saveForm.status):
                BillingAddress.objects.update(status = False)
                saveForm.status = True
            saveForm.save()
            msg = "Your address has been saved"
        print(form.errors)
    else:
        form = BillingAddressForm()
    print(form.errors)
    return render(request, 'addressbook/add_address.html', {'form': form, 'msg':msg})

def address(request):
    if request.method == 'POST':
        billing_form = BillingAddressForm(request.POST)
        
        shipping_form = ShippingAddressForm(request.POST)
        
        if billing_form.is_valid() and shipping_form.is_valid():
            billing_address = billing_form.save(commit=False)
            shipping_address = shipping_form.save(commit=False)
            billing_address.customer = request.user
            shipping_address.customer = request.user
            billing_address.save()
            shipping_address.save()
            
            request.session['billing_address_id'] = billing_address.id 
            request.session['shipping_address_id'] = shipping_address.id 
            return redirect(place_order)
        else:
            print(billing_form.errors)
    else:
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
    
    context = {'form':billing_form, 'ship_form':shipping_form}
    return render(request, 'cart/address.html', context)

# --------------ADDRESSS SECTION ENDING --------------

# --------------COUPON SECTION ------------------
def apply_coupon(request):
    order = Order.objects.get(customer = request.user)
    items = order.orderitem_set.filter(product__is_available=True)
    total = sum([item.get_total for item in items])
    now = timezone.now()
    code = request.POST.get('coupon_code')
    
    try:
        coupon = Coupon.objects.get(code__iexact=code,
                                         valid_from__lte=now,
                                         valid_to__gte=now,
                                         active=True)
        
        if (total >= coupon.min_price):
            request.session['coupon_id'] = coupon.id
            return JsonResponse({'success': True, 'message': 'Correct coupon code'})
        else:
            request.session['coupon_id'] = None
            return JsonResponse({'success':False, 'message': "Coupon cannot be applied ! Minimum price should be greater"})
    except Coupon.DoesNotExist:
        request.session['coupon_id'] = None
        return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    
# -----------------COUPON SECTION ENDING-----------------


# ----------------- WALLET SECTION START ----------------

def wallet(request):
    orders = Orders.objects.filter(
        Q(status="ReturnApproved") & 
        Q(payment__payment_mode__in=["PayPal", "RazorPay", "COD", "Wallet"]) |
        Q(status="Cancelled", payment__payment_mode__in=["PayPal", "RazorPay", "Wallet"])
    ).filter(customer=request.user)
    print(orders)
    try:
        wallet = Wallet.objects.get(user = request.user)
        if(not wallet.balance):
            wallet.balance = 0
    except:
        wallet = Wallet.objects.create(user = request.user)
        if(not wallet.balance):
            wallet.balance = 0
    context = {'wallet': wallet, 'orders':orders}
    return render(request, 'wallet/main.html', context)



# ----------------- WALLET SECTION ENDING ----------------






# ------------- HELPER METHODS --------------------

def product_quantity(id, quantity):
    product = Product.objects.get(id = id)
    product.quantity -= quantity
    product.save()

# --------------HELPER METHODS ENDING --------------