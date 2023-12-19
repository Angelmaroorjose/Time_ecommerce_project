from decimal import Decimal
from django.db import models
from accounts.models import *
from django.utils import timezone

# Create your models here.

class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null= True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null= True)
    total_price = models.FloatField(null=True)
    

    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        if total == None:
            return 0
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null= True)
    quantity = models.IntegerField(default=0,null=True, blank=True)
    price = models.FloatField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.selling_price * self.quantity
        return total 


class BillingAddress(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null= True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    district = models.CharField(max_length=200, null=True)
    pincode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(max_length=15, blank=True)
    email = models.EmailField(max_length=150, null= False)
    status = models.BooleanField(default=False)
    def __str__(self):
        return self.address
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null= True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    district = models.CharField(max_length=200, null=True)
    pincode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(max_length=15, blank=True)
    email = models.EmailField(max_length=150, null= False)
    def __str__(self):
        return self.address
    

class WishList(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class WishlistItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    wishlist = models.ForeignKey(WishList, on_delete=models.SET_NULL, blank=True, null= True)
    quantity = models.IntegerField(default=0,null=True, blank=True)
    price = models.FloatField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.selling_price * self.quantity
        return total 

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    min_price = models.FloatField(default=0)
    discount = models.FloatField()
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    active = models.BooleanField(null=True)


    def __str__(self):
        return self.code
    
class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    payment_id = models.CharField(max_length=100)
    payment_mode = models.CharField(max_length=100)
    total_amount = models.FloatField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    
class Orders(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    items = models.ManyToManyField(Product, through='OrderedItems')
    
    
    billing_address = models.ForeignKey(BillingAddress,on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.FloatField(null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL, null=True)
    orderstatuses = (
        ('Pending','Pending'),
        ('Out For Shipping','Out For Shipping'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Return','Return'),
        ('ReturnApproved','ReturnApproved'),
    )
    status = models.CharField(max_length=150, choices=orderstatuses, default='Pending')
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled = models.BooleanField(default=False)
    
    
    @property
    def get_discount(self):
        if self.coupon:
            return self.coupon.discount
        return Decimal('0')
    # def calculate_total_price(self):
    #     total_price = 0
    #     for item in self.items.all():
    #         total_price += item.price * item.quantity
    #     return total_price
    
    @property
    def get_order_total(self):
        orderitems = self.ordereditems_set.all()
        total = sum([item.get_total for item in orderitems])
        if total == None:
            return 0
        return total 

    @property
    def get_cart_items(self):
        orderitems = self.ordereditems_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def __str__(self):
        return str(self.id)

class OrderedItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    orderstatuses = (
        ('Pending','Pending'),
        ('Out For Shipping','Out For Shipping'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Return Requested','Return Requested'),
        ('Return Approved','Return Approved'),
    )
    status = models.CharField(max_length=150, choices=orderstatuses, default='Pending')

    @property
    def get_total(self):
        total = self.product.selling_price * self.quantity
        return total 
    
class Return(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(OrderedItems, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default="pending")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(null= True)
    status = models.CharField(max_length=20, null=True)

    def __str__(self) -> str:
        return f"{self.user}'s Wallet"
    

class MyModelManager(models.Manager):
    def new(self):
        print("A new function added to base manager")

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    objects = MyModelManager()


class Book(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    price = models.IntegerField()
