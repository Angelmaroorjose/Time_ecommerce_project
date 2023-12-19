from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('user_login/', views.user_login, name="user_login"),
    path('user_logout', views.user_logout, name="user_logout"),
    path('user_signup',views.user_signup, name="user_signup"),
    path('', views.home,name="home"),
   
    path('product/<slug:slug>',views.product, name="product_detail"),
    path('phone_verify',views.phone_verify, name="phone_verify"),
    path('verify/', views.verify_code, name="verify"),
    path('save-review/<int:id>', views.save_review, name="save-review"),
    


    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),      
    path("password_reset", views.password_reset_request, name="password_reset"),

    path('about', views.about),
    path('contact',views.contact),
    

    path('user_edit', views.user_profile_edit, name="user_edit"),
    path('user_profile', views.user_profile, name="user_profile"),
    

    path('user_address_list', views.address_list, name="user_addresses"),
    path('user_address_delete/<int:id>', views.delete_address, name="delete_address"),
    path('activate-address', views.activate_address, name="activate_address"),

    path('add-to-cart', views.addtocart),
    
    
]
