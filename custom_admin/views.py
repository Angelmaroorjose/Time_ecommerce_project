from io import BytesIO
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse_lazy

from django.core.paginator import Paginator

from django.db.models import Max, Min, Count, Avg, Sum
from cart.models import *
from .forms import BrandForm, CouponForm, OrderForm, ProductForm, Product, Category, CategoryForm, ProductImageForm
from django.contrib.auth import authenticate, login,logout
from accounts.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from accounts.forms import CustomUserCreationForm


from django.views.generic.edit import CreateView, DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,TemplateView

from django.db.models.functions import ExtractMonth, TruncMonth, Coalesce, TruncYear
import calendar
from .forms import *
from django.db.models import Q
from django.template.loader import render_to_string



from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from openpyxl import Workbook
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows

from datetime import datetime, timedelta
from django.contrib import messages

# Create your views here.

# ------------- ADMIN LOGIN - LOGOUT SECTION ---------------------

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(admin_dashboard)
    
    if request.method=='POST':
        
        username=request.POST['username']
        password=request.POST['password']
        adminuser=authenticate(username=username,password=password)
        if adminuser is not None:
            if adminuser.is_superuser:
                login(request,adminuser)
                return redirect(admin_dashboard)
        else:
            return render(request,'custom_admin/admin_login.html',{'invalid':"Invalid Credentials"})
    else:
         return render(request,'custom_admin/admin_login.html')


def admin_logout(request):
    if request.user.is_authenticated and request.user.is_superuser:
       logout(request)
       return redirect(admin_login)
    


@login_required(login_url='admin_login')
def admin_dashboard(request):
    if request.user.is_superuser:
        # orders = Orders.objects.annotate(month = ExtractMonth('created_at')).values('month').annotate(count = Count('id')).values('month', 'count')
        total_sales = Orders.objects.aggregate(Sum('total_price'))['total_price__sum']
        total_users = CustomUser.objects.count()
        total_orders = Orders.objects.count()

        year = datetime.now().year
        start_date = datetime(year=year, month=1, day=1)
        end_date = datetime(year=year, month=12, day=31)

        orders = Orders.objects.filter(created_at__gte=start_date, created_at__lte=end_date) \
                            .annotate(month=TruncMonth('created_at')) \
                            .values('month') \
                            .annotate(count=Coalesce(Count('id'), 0)) \
                            .order_by('month')

        labels_orders = [start_date.strftime('%B %Y')]
        data_orders = [0]

        for order in orders:
            while order['month'].strftime('%B %Y') != labels_orders[-1]:
                labels_orders.append((datetime.strptime(labels_orders[-1], '%B %Y') + timedelta(days=31)).strftime('%B %Y'))
                data_orders.append(0)
            data_orders[-1] = order['count']

        
        
        users = CustomUser.objects.filter(date_joined__gte=start_date, date_joined__lte=end_date) \
                            .annotate(month=TruncMonth('date_joined')) \
                            .values('month') \
                            .annotate(count=Coalesce(Count('id'), 0)) \
                            .order_by('month')

        
        labels_users = [start_date.strftime('%B %Y')]
        data_users = [0]

        for order in users:
            while order['month'].strftime('%B %Y') != labels_users[-1]:
                labels_users.append((datetime.strptime(labels_users[-1], '%B %Y') + timedelta(days=31)).strftime('%B %Y'))
                data_users.append(0)
            data_users[-1] = order['count']
        
        
        recent_orders = Orders.objects.order_by('-created_at')[:10]

        context = {'recent_orders': recent_orders, 'totalSales': total_sales, 'totalUsers': total_users, 'total_orders': total_orders, 'labels_orders': labels_orders, 'data_orders': data_orders, 'labels_users': labels_users, 'data_users': data_users}
        return render(request, 'custom_admin/index.html', context)
    else:
        return redirect(admin_login)



# ------------------ADMIN USER SECTION ---------------

@never_cache
@login_required(login_url='admin_login')
def block_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    user.is_active = False
    user.save()
    return redirect(display_user)

@never_cache
@login_required(login_url='admin_login')
def unblock_user(request, id):
    user = get_object_or_404(CustomUser, id = id)
    user.is_active = True
    user.save()
    return redirect(display_user)


@login_required(login_url='admin_login')
def display_user(request):
    if request.user.is_superuser:
        user = CustomUser.objects.all()
        return render(request, 'custom_admin/display_user.html', {'user':user})
    else:
        return redirect(admin_login)

@never_cache
@login_required(login_url='admin_login')
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print('hi')
        if form.is_valid():
            print("hello")
            form.save()
            return redirect(display_user)
    else:
        form = CustomUserCreationForm()
        print('h')
    return render(request, 'custom_admin/add_user.html',{'form':form})




# --------------ADMIN BRAND SECTION ---------------

@never_cache
@login_required(login_url='admin_login')
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            form.save()
            return redirect(display_brand)
    else:
        form = BrandForm()
       
    return render(request, 'custom_admin/add_brand.html',{'form':form})



@login_required(login_url='admin_login')
def display_brand(request):
    if request.user.is_superuser:
        brand = Brand.objects.all()
        return render(request, 'custom_admin/display_brand.html', {'categories': brand})
    else:
        return redirect(admin_login)


@never_cache
@login_required(login_url='admin_login')
def delete_brand(request, id):
    get_object_or_404(Brand, id=id).delete()
    return redirect(display_brand)


@never_cache
@login_required(login_url='admin_login')
def update_brand(request, id):
    category = get_object_or_404(Brand, id=id)
    if request.method == "POST":
        form = BrandForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            return redirect(display_category)
    else:
        form = BrandForm(instance = category)
    return render(request, 'custom_admin/update_brand.html',{'form':form})



# ---------------- ADMIN CATEGORY SECTION -----------------

@never_cache
@login_required(login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        print('hi')
        if form.is_valid():
            print("hello")
            form.save()
            return redirect(display_category)
    else:
        form = CategoryForm()
        print('h')
    return render(request, 'custom_admin/add_category.html',{'form':form})

@never_cache
@login_required(login_url='admin_login')
def display_category(request):
    categories = Category.objects.all()
    return render(request, 'custom_admin/display_category.html', {'categories': categories})

@never_cache
@login_required(login_url='admin_login')
def update_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            return redirect(display_category)
    else:
        form = CategoryForm(instance = category)
    return render(request, 'custom_admin/update_category.html',{'form':form})

@never_cache
@login_required(login_url='admin_login')
def delete_category(request, id):
    get_object_or_404(Category, id=id).delete()
    return redirect(display_category)



# -----------------ADMIN PRODUCT SECTION -----------------------

ImageFormSet = ProductImageFormSet = inlineformset_factory(Product, Picture, form=ProductImageForm, extra=5)
@never_cache
@login_required(login_url='admin_login')
def add_product(request):
    
    if request.method == 'POST':
        
        form = ProductForm(request.POST, request.FILES)
        image_form = ProductImageFormSet(request.POST, request.FILES,instance=Product())
        if form.is_valid() and image_form.is_valid():
            product = form.save(commit=False)
            product.save()
            image_form.instance = product
            image_form.save()
            return redirect(display_product)
    else:
        form = ProductForm()
        image_form = ProductImageFormSet(instance=Product())
    return render(request, 'custom_admin/add_product.html', {'form': form,'image_form':image_form})

@never_cache
@login_required(login_url='admin_login')
def update_product(request,id):
    product = get_object_or_404(Product, id= id)
    image_form = ImageFormSet(request.POST or None, request.FILES or None, instance=product )
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid() and image_form.is_valid():
            product = form.save()
            image_form.save()
            return redirect(display_product)
    else:
        form = ProductForm(instance=product)
    return render(request, 'custom_admin/update_product.html', {'form': form, 'image_form':image_form})


@login_required(login_url='admin_login')
def display_product(request):
    products = Product.objects.all()
    return render(request, 'custom_admin/display_product.html',{'products':products})


@never_cache
@login_required(login_url='admin_login')
def delete_product(request, id):
    get_object_or_404(Product, id=id).delete()
    return redirect(display_product)



# --------------  ADMIN COUPON SECTION -----------------------

class CouponListView(ListView):
    model = Coupon
    template_name = 'custom_admin/display_coupon.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coupons = Coupon.objects.all()
        context['coupons'] = coupons
        return context
    
class CouponCreateView(CreateView):
    template_name = 'custom_admin/add_coupon.html'
    form_class = CouponForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context 


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            coupon = form.save()
            return redirect('display_coupon')
        return super().get(request, *args, **kwargs)


def delete_coupon(request, id):
    get_object_or_404(Coupon, id=id).delete()
    return redirect('display_coupon')


def update_coupon(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            coupon = form.save()
            return redirect('display_coupon')
    else:
        form = CouponForm(instance = coupon)
    return render(request, 'custom_admin/update_coupon.html',{'form':form})




def display_orders(request):
    orders = Orders.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    totalpage = page_obj.paginator.num_pages
    return render(request, 'custom_admin/display_orders.html',{'orders':orders, 'page_number': page_number,
        'totalPageList':[n+1 for n in range(totalpage)],
        'total_pages': paginator.num_pages, 'products':page_obj})

def orders_detail(request, id):
    order = Orders.objects.get(id = id)
    orderitems = OrderedItems.objects.filter(order = id)
    
    context = {'orders': order, 'order_items': orderitems}
    return render(request, 'custom_admin/display_order_detail.html', context)

def order_item_detail(request, order_id, order_item_id):
    order = Orders.objects.get(id = order_id)
    user = order.customer
    
    order_item = get_object_or_404(OrderedItems, id=order_item_id, order = order)
    if request.method == 'POST':
        order_item.status = request.POST['status']
      
        order_item.save()
        if order_item.status == "Return Approved":
                wallet, created = Wallet.objects.get_or_create(user = user)
                if(wallet.balance is None):
                    wallet.balance = 0
                wallet.balance += order_item.get_total
                
               
                wallet.save()
        if (order_item.status == "Cancelled" and (order.payment.payment_mode == "PayPal" or order.payment.payment_mode == "RazorPay" or order.payment.payment_mode == "Wallet")):
                wallet, created = Wallet.objects.get_or_create(user = user)
                if(wallet.balance is None):
                    wallet.balance = 0
                wallet.balance += order_item.get_total
                wallet.save()
                print(order_item.status)
    
    return redirect(orders_detail, order_id)


def edit_order_status(request, id):
    order = Orders.objects.get(id = id)
    user = order.customer
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            orders = form.save()
            
            return redirect('display_orders')
    else:
        form = OrderForm(instance=order)
    context = {'form': form}
    return render(request, 'custom_admin/update_order.html', context)


def dashboard(request):
    return render(request, 'custom_admin/dashboard.html')

class OfferCreateView(CreateView):
    template_name = 'custom_admin/add_offer.html'
    form_class = OfferForm

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context
    
    def post(self, request, *args: str, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            offer = form.save()
            return redirect('display_offer')
        return super().post(request, *args, **kwargs)
    
class OfferDisplayView(ListView):
    model = Offer
    template_name = 'custom_admin/display_offer.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        offers = Offer.objects.all()
        context['offers'] = offers
        return context
    

class OfferUpdateView(UpdateView):
    model = Offer
    form_class = OfferForm
    template_name = 'custom_admin/update_offer.html'
    success_url = reverse_lazy('display_offer')
    

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        return obj
        

def delete_offer(request, id):
    get_object_or_404(Offer, id=id).delete()
    return redirect('display_offer')

class BannerDisplayView(ListView):
    model = Banner
    template_name = 'custom_admin/display_banner.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        banner = Banner.objects.all()
        context['banner'] = banner
        return context
    
class BannerCreateView(CreateView):
    
    form_class = BannerForm
    template_name = 'custom_admin/add_banner.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context
    
    def post(self, request, *args: str, **kwargs) :
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            return redirect('display_banner')
        return super().post(request, *args, **kwargs)

class BannerUpdateView(UpdateView):
    model = Banner
    template_name = 'custom_admin/update_banner.html'
    form_class = BannerForm
    success_url = reverse_lazy('display_banner')

    def get_object(self, queryset=None):
        obj =  super().get_object(queryset = queryset)
        return obj

def delete_banner(request, id):
    get_object_or_404(Banner, id = id).delete()
    return redirect('display_banner')

def sales_report(request):
    order =  Orders.objects.filter(status = "Completed").order_by('-created_at')
    total_sales = order.aggregate(total_sales=Sum('total_price')).get('total_sales', 0)
    
    return render(request, 'custom_admin/sales_report.html', {'order_items': order, 'total_sales':total_sales})


def sales(request):
    if request.method == "POST":
        start_time = request.POST.get('starting_date')
        end_time = request.POST.get('ending_date')
        if start_time and end_time:  # Check if start_date and end_date are provided in the POST request
                start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
                end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        else:  # Set default time to retrieve all orders
                start_time = datetime(1900, 1, 1)  # Replace with your desired default start time
                end_time = datetime.now()
        output_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
        output_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
        order = Orders.objects.filter(Q(created_at__gte=output_start_time) & Q(created_at__lte= output_end_time, status = "Completed" )).order_by('-created_at')
        total_sales = order.aggregate(total_sales=Sum('total_price')).get('total_sales', 0)
        t = render_to_string('custom_admin/sales_list.html', {'orders':order, 'total_sales':total_sales})
   
        return JsonResponse({'status': t, 'total':total_sales})
    
def sales_report_pdf(request):
    if request.method == "POST":
        print("in post method")
        if 'pdf_button' in request.POST:
            
            print("in sales report")
            
            # start_time = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%dT%H:%M')
            # end_time = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if start_date and end_date:  # Check if start_date and end_date are provided in the POST request
                start_time = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
                end_time = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
            else:  # Set default time to retrieve all orders
                start_time = datetime(1900, 1, 1)  # Replace with your desired default start time
                end_time = datetime.now()
            
            output_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
            output_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
            orders = Orders.objects.filter(Q(created_at__gte=output_start_time) & Q(created_at__lte= output_end_time), status = "Completed").order_by('-created_at')
            
            total_sales = orders.aggregate(total_sales=Sum('total_price')).get('total_sales', 0)
            if not orders:
                messages.info(request, "No orders in this date")
                return redirect(sales_report)
            else:
                template_path = 'pdf_convert/order_pdf.html'
                context = {'order_items': orders, 'total_sales': total_sales}
                response = HttpResponse(content_type = 'application/pdf')
                response['Content-Disposition'] = 'filename = "orders_report.pdf"'
                template = get_template(template_path)
                html = template.render(context)

                pisa_status = pisa.CreatePDF(html, dest=response)
                if pisa_status.err:
                    return HttpResponse("We has some errors <pre>"+html +'</pre>')
                return response

        elif 'excel_button' in request.POST:
    
            start_time = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%dT%H:%M')
            
            output_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
            output_end_time = end_time.strftime('%Y-%m-%d %H:%M:%S.%f+00:00')
            orders = Orders.objects.filter(Q(created_at__gte=output_start_time) & Q(created_at__lte= output_end_time)).order_by('-created_at')
            total_sales = orders.aggregate(total_sales=Sum('total_price')).get('total_sales', 0)

            # Pass the order data to the HTML template
            context = {'order_items': orders, 'total_sales':total_sales}

            # Render the HTML template with the order data
            html_string = render(request, 'pdf_convert/order_pdf.html', context).content.decode('utf-8')

            # Create a pandas dataframe from the HTML table
            df_list = pd.read_html(html_string)
            df = df_list[-1]

            # Create an Excel workbook and worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = 'Orders'

            # Add the pandas dataframe to the worksheet
            for row in dataframe_to_rows(df, index=False, header=True):
                ws.append(row)

            # Create the HTTP response with the Excel file
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
            wb.save(response)

            return response


def order_graph(request):
    print("hhhh")
    return JsonResponse({'status':'success'})




def get_data(request):
        selectedValue = request.POST.get('selectedValue')
        if(selectedValue == "Days"):
            today = datetime.now().date()
            first_day = today.replace(day=1)
            last_day = first_day.replace(month=first_day.month+1)-timedelta(days=1)
            labels = [(first_day+timedelta(days=i)).strftime('%Y-%m-%d') for i in range((last_day-first_day).days+1)]
            labels_days = [(first_day+timedelta(days=i)).strftime('%d') for i in range((last_day-first_day).days+1)]

            orders_created = Orders.objects.filter(created_at__range=[first_day, last_day])
            print(today, first_day, last_day, orders_created, labels)
            data = [orders_created.filter(created_at__date=date).count() for date in labels]
            print(data)
            return JsonResponse({'labels': labels_days, 'values': data,'name':"Days"})
        elif(selectedValue == "Month"):
            year = datetime.now().year
            start_date = datetime(year=year, month=1, day=1)
            end_date = datetime(year=year, month=12, day=31)

            orders = Orders.objects.filter(created_at__gte=start_date, created_at__lte=end_date) \
                                .annotate(month=TruncMonth('created_at')) \
                                .values('month') \
                                .annotate(count=Coalesce(Count('id'), 0)) \
                                .order_by('month')

            labels_orders = [start_date.strftime('%B %Y')]
            data_orders = [0]

            for order in orders:
                while order['month'].strftime('%B %Y') != labels_orders[-1]:
                    labels_orders.append((datetime.strptime(labels_orders[-1], '%B %Y') + timedelta(days=31)).strftime('%B %Y'))
                    data_orders.append(0)
                data_orders[-1] = order['count']
            print(labels_orders, data_orders)
            return JsonResponse({'labels': labels_orders, 'values': data_orders,'name':"Months"})
        
        else:
            five_years_ago = datetime.now() - timedelta(days=5*365)

            # Query the orders created in the last five years
            orders = Orders.objects.filter(created_at__gte=five_years_ago)

            # Group the orders by year
            orders_by_year = orders.annotate(year=TruncYear('created_at')).values('year').annotate(count=Count('id'))

            orders_dict = {o['year'].year: o['count'] for o in orders_by_year}

            # Create the labels and data for Chart.js
            labels = []
            data = []
            current_year = datetime.now().year
            for i in range(5):
                year = current_year - i
                labels.append(str(year))
                data.append(orders_dict.get(year, 0))

            return JsonResponse({'labels': labels, 'values': data,'name':"Years"})

def get_user_data(request):
        selectedValue = request.POST.get('selectedValue')
        if(selectedValue == "Days"):
            today = datetime.now().date()
            first_day = today.replace(day=1)
            last_day = first_day.replace(month=first_day.month+1)-timedelta(days=1)
            labels = [(first_day+timedelta(days=i)).strftime('%Y-%m-%d') for i in range((last_day-first_day).days+1)]
            labels_days = [(first_day+timedelta(days=i)).strftime('%d') for i in range((last_day-first_day).days+1)]

            orders_created = CustomUser.objects.filter(joined_on__range=[first_day, last_day])
            print(today, first_day, last_day, orders_created, labels)
            data = [orders_created.filter(joined_on__date=date).count() for date in labels]
            print(data)
            return JsonResponse({'labels': labels_days, 'values': data,'name':"Days"})
        elif(selectedValue == "Month"):
            year = datetime.now().year
            start_date = datetime(year=year, month=1, day=1)
            end_date = datetime(year=year, month=12, day=31)

            orders = CustomUser.objects.filter(joined_on__gte=start_date, joined_on__lte=end_date) \
                                .annotate(month=TruncMonth('joined_on')) \
                                .values('month') \
                                .annotate(count=Coalesce(Count('id'), 0)) \
                                .order_by('month')

            labels_orders = [start_date.strftime('%B %Y')]
            data_orders = [0]

            for order in orders:
                while order['month'].strftime('%B %Y') != labels_orders[-1]:
                    labels_orders.append((datetime.strptime(labels_orders[-1], '%B %Y') + timedelta(days=31)).strftime('%B %Y'))
                    data_orders.append(0)
                data_orders[-1] = order['count']
            print(labels_orders, data_orders)
            return JsonResponse({'labels': labels_orders, 'values': data_orders,'name':"Months"})
        
        else:
            five_years_ago = datetime.now() - timedelta(days=5*365)

            # Query the orders created in the last five years
            orders = CustomUser.objects.filter(joined_on__gte=five_years_ago)

            # Group the orders by year
            orders_by_year = orders.annotate(year=TruncYear('joined_on')).values('year').annotate(count=Count('id'))

            orders_dict = {o['year'].year: o['count'] for o in orders_by_year}

            # Create the labels and data for Chart.js
            labels = []
            data = []
            current_year = datetime.now().year
            for i in range(5):
                year = current_year - i
                labels.append(str(year))
                data.append(orders_dict.get(year, 0))

            return JsonResponse({'labels': labels, 'values': data,'name':"Years"})

