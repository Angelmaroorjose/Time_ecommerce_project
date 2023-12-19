from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
import datetime
import os
from django.utils.text import slugify



def getFileName(request, filename):
    now_time = datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename = "%s%s"%(now_time, filename)
    return os.path.join('uploads/',new_filename)


class CustomUser(AbstractUser, models.Model):
    username = models.CharField(null=True, blank=True, max_length=100, unique=True)
    phone_number = PhoneNumberField(max_length=15, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=255, unique=True)
    joined_on = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default= True)
    is_active = models.BooleanField(default= True)
    is_guest = models.BooleanField(default=False)
    guest_token = models.CharField(max_length=255, null=True, blank=True)





class Brand(models.Model):
    name = models.CharField(max_length=100, null= False, blank=False)
    description = models.TextField(max_length=150, null=True, blank=True)
    model = models.CharField(max_length=150, null=True, blank=True)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden",blank=True)

    def __str__(self):
        return self.name

class Offer(models.Model):
    name = models.CharField(max_length=100, null= False, blank=False)
    description = models.TextField(max_length=150, null=True, blank=True)
    offer_choice = (("Product","Product"),("Category","Category"))
    type = models.CharField(max_length = 100,choices=offer_choice, null=True, blank=True)
        
    model = models.CharField(max_length=150, null=True, blank=True)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden",blank=True)
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    active = models.BooleanField(null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=getFileName,null=True,blank=True)
    description = models.TextField(max_length=150, null=False, blank=False)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    vendor = models.CharField(max_length=100, null=False, blank=False)
    product_image = models.ImageField(upload_to='product/',null=False,blank=False)
    quantity = models.PositiveIntegerField(default=0)
    original_price = models.FloatField(null=False,blank=False)
    selling_price = models.FloatField(null=False,blank=False)
    offer_price = models.FloatField(null=True, blank=True)
    description = models.TextField(max_length=350, null=False, blank=False)
    status = models.BooleanField(default=False,help_text="0-show,1-Hidden",blank=True)
    trending = models.BooleanField(default=False,help_text="0-default,1-Trending",blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    offer_status = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class Picture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_pictures")
    image = models.ImageField(upload_to='product/', blank=True)

    def __str__(self):
        return self.image.url

RATING = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)
class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_rating = models.IntegerField(choices=RATING)
    
    def get_review_rating(self):
        return self.review_rating

    def __str__(self):
        return f"Rating: {self.review_rating}, Review: {self.review_text}"