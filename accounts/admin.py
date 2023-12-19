from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import *
from django.contrib.admin import ModelAdmin
# Register your models here.



class CatergoryAdmin(admin.ModelAdmin):
    list_display = ('name','image','description')

class PictureInline(admin.StackedInline):
    model = Picture

class ProductAdmin(admin.ModelAdmin):
    inlines = [PictureInline]

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'review_text', 'get_review_rating')



admin.site.register(Product, ProductAdmin)

admin.site.register(Offer)
admin.site.register(CustomUser)
admin.site.register(Category,CatergoryAdmin)
admin.site.register(Brand)
admin.site.register(ProductReview, ProductReviewAdmin)

