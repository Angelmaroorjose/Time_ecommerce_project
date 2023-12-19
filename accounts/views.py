import json
import uuid
from django.shortcuts import render,redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from .import verify
from .forms import VerifyForm
from .decorators import verification_required 
from .models import CustomUser, Picture, Product
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm, ReviewForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache


from django.db.models import Avg
#password import
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from cart.models import *

from custom_admin.models import Banner
from django.utils import timezone

# Create your views here.



# --------- USER SECTION -----------
def user_login(request):
    
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None and user.is_active and user.is_superuser == False:
            try:
                redirect_url = request.session.pop('checkout_redirect')
            except:
                pass
            
            login(request, user)
            try:
                if redirect_url:
                    return redirect(redirect_url)
            except:
                    try:
                        cart, created = Order.objects.get_or_create(customer=request.user)
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

                    response = redirect(home)
                    if(response.delete_cookie('cart')):
                        response.delete_cookie('cart')
                    return response
                
        else:
            return render(request, 'user/user_login.html', {'invalid':'Invalid Credentials'})
    return render(request, 'user/user_login.html')


@never_cache
def user_logout(request):
    if request.user.is_authenticated and not request.user.is_superuser:
       logout(request)
       return redirect(home)


def home(request):
    num_of_item = 0
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            customer = request.user
            order, created = Order.objects.get_or_create(customer = customer, complete = False)
            items = order.orderitem_set.all()
            num_of_item = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        num_of_item = order['get_cart_items']

        for i in cart:
            num_of_item += int(cart[i]["quantity"])
            

    now = timezone.now()

    try:
        banner = Banner.objects.filter(start_date__lte=now,
                                          end_date__gte=now)
    except:
        banner = None
    products = Product.objects.all()
    for product in products:
        category = Category.objects.get(id = product.category.id)
        original_price = product.original_price
        try:
            offer = product.offer
            print(offer.discount_amount)
            old_price = original_price * int(offer.discount_amount)/100
            product.selling_price = product.original_price - old_price
            product.offer_status = True
            product.save()
            print(product.offer)
        except:
            pass

        try:
            offer = category.offer
            print(offer.discount_amount)
            new_price = original_price * int(offer.discount_amount)/100
            if(old_price < new_price):
                product.selling_price = product.original_price - new_price
                product.offer_status = True
                product.save()
            print(category.offer)
        except:
            pass

        if not product.offer and not category.offer:
            product.selling_price = product.original_price
            product.offer_status = False
            product.save()
        
       

    return render(request, 'user/index.html',{'products':products, 'num_of_items': num_of_item, 'banner':banner})



def user_signup(request):
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("captcha validation success")
            phone_number = '+91' + str(form.cleaned_data.get('phone_number'))
            form.save()
            return redirect(user_login)
        else:
            print("captcha validation failed")
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})


# ------------- USER SECTION ENDING ------------

# -------------- PRODUCT DETAILS ---------------

def product(request, slug):
    product = get_object_or_404(Product, slug = slug)
    category = Category.objects.get(id = product.category.id)
    related_products = Product.objects.filter(category = category)[:9]
    old_price = 0
    original_price = product.original_price
    num_of_item = 0
    reviewForm = ReviewForm()
    canAdd = True
    
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            reviewCheck = ProductReview.objects.filter(user = request.user, product = product).count()
            customer = request.user
            order, created = Order.objects.get_or_create(customer = customer, complete = False)
            items = order.orderitem_set.all()
            num_of_item = order.get_cart_items
            if reviewCheck > 0:
                canAdd = False
            
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        num_of_item = order['get_cart_items']

        for i in cart:
            
            num_of_item += int(cart[i]["quantity"])
    try:
        offer = product.offer
        print(offer.discount_amount)
        old_price = original_price * int(offer.discount_amount)/100
        product.selling_price = product.original_price - old_price
        product.offer_status = True
        product.save()
        print(product.offer)
    except:
        pass

    try:
        offer = category.offer
        print(offer.discount_amount)
        new_price = original_price * int(offer.discount_amount)/100
        if(old_price < new_price):
            product.selling_price = product.original_price - new_price
            product.offer_status = True
            product.save()
        print(category.offer)
    except:
        pass
    
    if not product.offer and not category.offer:
            product.selling_price = product.original_price
            product.offer_status = False
            product.save()
    
    review = ProductReview.objects.filter(product= product)

    # fetch avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product= product).aggregate(avg_rating = Avg('review_rating'))
    count_reviews = ProductReview.objects.filter(product= product).count()
    
    images = Picture.objects.all().filter(product= product.id)
    context = {'product':product,'images':images, 'related_products': related_products, 
               'num_of_items': num_of_item, 'form':reviewForm, 
               'canAdd':canAdd, 'reviews':review, 'avg_reviews':avg_reviews, 'count_reviews':count_reviews}

    return render(request, 'user/product_details.html', context )

def addtocart(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            product_id = int(request.POST.get('product_id'))
            prod_qty = int(request.POST.get('product_qty'))
            print(prod_qty)
            product_check = Product.objects.get(id=product_id)
            
            if(product_check.quantity):
                prod_qty = int(request.POST.get('product_qty'))
                if product_check.quantity >= prod_qty:
                    order,created = Order.objects.get_or_create(customer = request.user, complete = False)
               
                    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product_check)
                   
                    
                    orderItem.quantity += prod_qty
                    
                    if(orderItem.quantity > product_check.quantity):
                        orderItem.quantity = product_check.quantity
                        product_check.save()
                        orderItem.save()
                        order.save()
                        num_of_item = order.get_cart_items
                        return JsonResponse({"failure":"Product already exists in the cart ! Cannot add product",'num_of_items':num_of_item})
                    product_check.save()
                    orderItem.save()
                    order.save()
                    num_of_item = order.get_cart_items
                    return JsonResponse({"status":"Product added successfully",'num_of_items':num_of_item})
                
                elif(product_check.quantity == 0):
                    product_check.is_available = False
                    product_check.save()
                    
                    return JsonResponse({"failure":"Out of stock"})
                elif(prod_qty > product_check.quantity):
                    return JsonResponse({'failure':"Out of stock"})
                elif(product_check.quantity == 1):
                    product_check.quantity -=1
                    product_check.save()
                    order,created = Order.objects.get_or_create(customer = request.user, complete = False)
               
                    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product_check)
                    orderItem.quantity+=1
                    orderItem.save()
                    order.save()
                    return JsonResponse({"status":"Last One successfully added to cart!"})
                else:
                    return JsonResponse({"status":"Only"+str(product_check.quantity) + " quantity available"})
                
            else:
                return JsonResponse({"status":"No such product found"})
        else:
            return JsonResponse({"status":"Login to Continue"})
    return redirect('/')

# --------------PRODUCT DETAILS ENDING --------------



# ------------ OTP LOGIN SECTION --------------
def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_no = request.session.get('phone')
            
            
            if verify.check(phone_no, code):
                print("checked")
                
                user = CustomUser.objects.get(username = request.session.get('username'))
                userobj = CustomUser.objects.filter(username = request.session.get('username'))
                print(user)
                print(user.is_authenticated)
                print(user.is_active)
                print(user.is_superuser)
                if userobj is not None and user.is_active and user.is_superuser == False:
                    print(user.is_authenticated)
                    login(request, user)
                    return redirect(home)
                print(user)
                return redirect(home)
            else:
                print("error")
    else:
        form = VerifyForm()
    return render(request, 'user/verify.html', {'form': form})


def phone_verify(request):
    if request.method == "POST":
        
        phone = '+91'+  str(request.POST['phone_number'])
        if check_phone_number(phone):
            verify.send(phone)
            user = username_password(phone)
            request.session['username'] = user.username
            print(user.username)
            user.is_verified = True
            user.is_active = True
            request.session['phone'] = phone
            return redirect(verify_code)
        else:
            context = "Please register first"
            return render(request, 'phone_verify.html',{'context':context})
    return render(request, 'user/phone_verify.html')

def username_password(phone):
    user = CustomUser.objects.filter(phone_number=phone)[0]
    return user

def check_phone_number(phone_number):
    try:
        phone = CustomUser.objects.filter(phone_number=phone_number)[0]
        return True
    except CustomUser.DoesNotExist:
        return False

# --------- OTP LOGIN ENDING -----------  


# ---------- FORGOT PASSWORD SECTION ------------
def password_reset_request(request):
     if request.method == "POST":
       
          password_reset_form = PasswordResetForm(request.POST)

          if password_reset_form.is_valid():
               
               data = password_reset_form.cleaned_data['email']
               associated_users = CustomUser.objects.filter(Q(email = data))

               if associated_users.exists():
                    print(associated_users)
                    for user in associated_users:
                         subject = "Password Reset Requested"
                         email_template_name = "main/password/password_reset_email.txt"
                         c = {
                              "email":user.email,
                              "domain":'16.16.200.144',
                              "site_name":'Website',
                              "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                              "user":user,
                              'token':default_token_generator.make_token(user),
                              'protocol':'http',
                         }
                         email = render_to_string(email_template_name, c)
                         try:
                              send_mail(subject, email,'alensabu12xtz@gmail.com', [user.email], fail_silently=False)
                         except BadHeaderError:
                              return HttpResponse("Invalid header found")
                         return redirect('password_reset/done/')
     password_reset_form = PasswordResetForm()

     return render(request=request, template_name="password_reset/password_reset.html", context={"password_reset_form":password_reset_form})

# ---------- FORGOT PASSWORD SECTION ENDING ------------------                           
                              




def about(request):
    return render(request, 'user/about.html')

def contact (request):
    return render(request, 'user/contact.html')






# --------- USER PROFILE SECTION ---------

def user_profile(request, id=3):
    product = get_object_or_404(Product, id=id)
    images = Picture.objects.all().filter(product= product.id)
    return render(request, 'user/product_details_1.html',{'product':product,'images':images})

def user_profile_edit(request):
    msg = None
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance = request.user)
        if form.is_valid():
            phone_number = '+91' + str(form.cleaned_data.get('phone_number'))
            form.save()
            
            msg = "Data has been saved"
   
    form = CustomUserChangeForm(instance = request.user)
   
    context = {'form':form, 'msg':msg}
    return render(request, 'user/user_edit.html', context)


# --------------- USER ADDRESS SECTION ---------------

def address_list(request):
    addresses = BillingAddress.objects.filter(customer=request.user).order_by('id')
    return render(request, 'addressbook/address_list.html', {'addresses': addresses})

def delete_address(request, id):
    get_object_or_404(BillingAddress, id=id).delete()
    return redirect(address_list)

def activate_address(request):
    a_id = str(request.GET['id'])
    BillingAddress.objects.update(status = False)
    BillingAddress.objects.filter(id = a_id).update(status = True)
    data = {}
    return JsonResponse({'bool':True})



def save_review(request, id):
    product = Product.objects.get(id = id)
    user = request.user

    review = ProductReview.objects.create(
        user = user,
        product = product,
        review_text = request.POST['review_text'],
        review_rating = request.POST['review_rating']
    )
    review_rating = request.POST['review_rating']
    count_review = ProductReview.objects.filter(product= product).count()
    data = {
        'user':user.username, 
        'review_text':request.POST['review_text'],
        'review_rating':request.POST['review_rating'],
        'count_review':count_review
    }
    return JsonResponse({'bool':True, 'data':data})