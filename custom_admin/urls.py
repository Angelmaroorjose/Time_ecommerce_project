from django.urls import path
from . import views


urlpatterns = [
    path('admin_login', views.admin_login, name="admin_login"),
    path('admin_dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('admin_logout',views.admin_logout, name="admin_logout"),


    path('display_user',views.display_user, name="display_user"),
    path('block_user/<int:id>',views.block_user, name="block_user"),
    path('unblock_user/<int:id>',views.unblock_user, name="unblock_user"),
    path('add_user',views.add_user,name="add_user"),

    path("add_category", views.add_category),
    path('display_category',views.display_category, name="display_category"),
    path('update_category/<str:id>',views.update_category, name="update_category"),
    path('delete_category/<str:id>',views.delete_category, name="delete_category"),

    path("add_brand", views.add_brand, name="add_brand"),
    path("display_brand", views.display_brand, name="display_brand"),
    path('delete_brand/<str:id>',views.delete_brand, name="delete_brand"),
    path('update_brand/<str:id>',views.update_brand, name="update_brand"),

    path('add_product', views.add_product),
    path('display_product',views.display_product, name="display_product"),
    path('update_product/<int:id>',views.update_product, name="update_product"),
    path('delete_product/<int:id>', views.delete_product, name="delete_product"),


    path('display_coupon', views.CouponListView.as_view(), name="display_coupon"),
    path('add_coupon', views.CouponCreateView.as_view(), name="add_coupon"),
    path('delete/<int:id>', views.delete_coupon, name='delete_coupon'), 
    path('update/<int:id>', views.update_coupon, name='update_coupon'), 

    path('display_orders/', views.display_orders, name="display_orders"),
    path('orders/<int:id>', views.orders_detail, name="order_specific"), 
    path('edit_orders/<int:id>', views.edit_order_status, name="edit_order_specific"), 
    path('edit_orderedItems/<int:order_id>/<int:order_item_id>', views.order_item_detail, name="edit_orderitem"), 

    path('display_offer', views.OfferDisplayView.as_view(), name="display_offer"),
    path('add_offer', views.OfferCreateView.as_view(), name="add_offer"),
    path('update_offer/<int:pk>', views.OfferUpdateView.as_view(), name="update_offer"),
    path('delete_offer/<int:id>', views.delete_offer, name="delete_offer"), 

    path('display_banner', views.BannerDisplayView.as_view(), name = 'display_banner'),
    path('add_banner', views.BannerCreateView.as_view(), name='add_banner'),
    path('update_banner/<int:pk>', views.BannerUpdateView.as_view(), name="update_banner"),
    path('delete_banner/<int:id>', views.delete_banner, name="delete_banner"),

    path('sales_report', views.sales_report, name="sales_report"),
    path('sales-report', views.sales),
    path('sales_report_pdf', views.sales_report_pdf,name="sales_report_pdf"),

    path('order-chart-data',views.get_data, name ="order_graph"), 
    path('user-chart-data',views.get_user_data, name ="user_graph"), 

    path('dashboard', views.dashboard)

]
