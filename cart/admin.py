from django.contrib import admin
from .models import *
from custom_admin.models import *
# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(BillingAddress)
admin.site.register(WishList)
admin.site.register(WishlistItem)
admin.site.register(Orders)
admin.site.register(OrderedItems)
admin.site.register(Coupon)
admin.site.register(Banner)
admin.site.register(Wallet)
admin.site.register(Book)