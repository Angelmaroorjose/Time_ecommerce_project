# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, ProductReview
from phonenumber_field.formfields import PhoneNumberField
from captcha.fields import CaptchaField

    
class CustomUserCreationForm(UserCreationForm):
    captcha_field = CaptchaField()
    phone_number = PhoneNumberField(region="IN",max_length=15, required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone Number'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')
        
    #def save(self, commit = True):
        #user = super().save(commit=False)
       # user.password = self.cleaned_data["password1"]
        #if commit:
           # user.save()
        #return user

class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(required = False, widget=forms.TextInput(attrs={"placeholder":"First Name", "onfocus":"this.placeholder = ''" ,"onblur":"this.placeholder = 'First Name'" , "class":"single-input"}))
    last_name = forms.CharField(required = False, widget=forms.TextInput(attrs={"placeholder":"Last Name", "onfocus":"this.placeholder = ''" ,"onblur":"this.placeholder = 'Last Name'" , "class":"single-input"}))
    phone_number = PhoneNumberField(region="IN",max_length=15, required=True, widget=forms.TextInput(attrs={"placeholder":"Phone Number", "onfocus":"this.placeholder = ''" ,"onblur":"this.placeholder = 'Phone Number'" , "class":"single-input"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username", "onfocus":"this.placeholder = ''" ,"onblur":"this.placeholder = 'Username'" , "class":"single-input"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder":"Email", "onfocus":"this.placeholder = ''" ,"onblur":"this.placeholder = 'Email'" , "class":"single-input"}))
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number')    
        

class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Code'}))



class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ('review_text', 'review_rating')