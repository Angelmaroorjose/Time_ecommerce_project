from django import forms
from accounts.models import *
from cart.models import *
from custom_admin.models import Banner




class ProductForm(forms.ModelForm):
   
    category = forms.ModelChoiceField(queryset=Category.objects.all() ,widget=forms.Select(attrs={'class':'form-select'}))
    offer = forms.ModelChoiceField(required = False,queryset=Offer.objects.all() ,widget=forms.Select(attrs={'class':'form-select'}))
    brand = forms.ModelChoiceField(queryset=Brand.objects.all() ,widget=forms.Select(attrs={'class':'form-select'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'name'}))
   
    vendor = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'vendor'}))
    product_image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class':'form-control','id':'formFile'}),required=False)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','id':'quantity'}))
    
    selling_price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control','id':'selling_price'}))
    original_price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control','id':'original_price'}))
    

    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'description'}))
    status = forms.BooleanField(required=False)
    trending = forms.BooleanField(required=False)
    is_available = forms.BooleanField(required=False)
    
    
    class Meta:
        model = Product
        fields = ['category','brand','offer','name', 'vendor', 'product_image', 'quantity','original_price', 'selling_price', 'description','status', 'trending', 'is_available']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['image']
      

class CategoryForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'name'}))
    offer = forms.ModelChoiceField(required = False,queryset=Offer.objects.all() ,widget=forms.Select(attrs={'class':'form-select'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control','id':'formFile'}),required=False)
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'description'}))
    status = forms.BooleanField(required=False)

    class Meta:
        model = Category
        fields = ['name','offer','image', 'description','status']



class BrandForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'name'}))
    model = forms.CharField(required = False, widget=forms.TextInput(attrs={'class':'form-control','id':'name'}))
    
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'description'}))
    status = forms.BooleanField(required=False)

    class Meta:
        model = Brand
        fields = ['name','model', 'description','status']

class CouponForm(forms.ModelForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    discount = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    min_price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    active = forms.BooleanField(required=False)
    valid_from =forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ'],widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), # set the widget to display as datetime-local in HTML
                        label='Valid From')
    valid_to = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ'],widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), # set the widget to display as datetime-local in HTML
                        label='Valid TO')

    class Meta:
        model = Coupon
        fields = ['code', 'discount','min_price', 'active','valid_from', 'valid_to']

class OrderForm(forms.ModelForm):
    
    orderstatuses = (
        ('Pending','Pending'),
        ('Out For Shipping','Out For Shipping'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Return','Return'),
        ('ReturnApproved','ReturnApproved'),
    )
    
    status = forms.ChoiceField(required = False, choices=orderstatuses,widget=forms.Select(attrs={'class':'form-select'}))
    message = forms.CharField(required = False, widget=forms.TextInput(attrs={'class':'form-control','id':'description'}))
    tracking_no = forms.CharField(required = False, widget=forms.TextInput(attrs={'class':'form-control'}))
    
    
    
    class Meta:
        model = Orders
        fields = ['status', 'message', 'tracking_no','cancelled']

class OrderItemsForm(forms.ModelForm):
     orderstatuses = (
        ('Pending','Pending'),
        ('Out For Shipping','Out For Shipping'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Return','Return'),
        ('ReturnApproved','ReturnApproved'),
    )
     status = forms.ChoiceField(required = False, choices=orderstatuses,widget=forms.Select(attrs={'class':'form-select'}))

     class Meta:
         models = OrderedItems
         fields = ['status']

class OfferForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(required = False,widget=forms.TextInput(attrs={'class':'form-control'}))
    model = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    status = forms.BooleanField()
    valid_from = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ'],widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), # set the widget to display as datetime-local in HTML
                        label='Select a date and time')
    valid_to = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S.%fZ'],widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), # set the widget to display as datetime-local in HTML
                        label='Select a date and time')
    active = forms.BooleanField(required=False)
    discount_amount = forms.DecimalField(widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Offer
        fields = ['name','description', 'model', 'status', 'valid_from', 'valid_to', 'active', 'discount_amount']

class BannerForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    heading = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    image = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control'}))
    start_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%S.%fZ'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%S.%fZ'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    status = models.BooleanField()
    class Meta:
        model = Banner
        fields = ['name','heading','description','image','start_date', 'end_date', 'status']
