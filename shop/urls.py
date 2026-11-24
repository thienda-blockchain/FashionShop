# shop/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # PHÂN HỆ KHÁCH HÀNG
    path('', views.product_list, name='product_list'),

    # ĐĂNG KÝ KHÁCH HÀNG
    path(
        'register/',
        views.register,
        name='register'
    ),

    # PHÂN HỆ QUẢN LÝ
    path(
        'store-manager/products/',
        views.manager_product_list,
        name='manager_products'
    ),

    path(
        'store-manager/products/add/',
        views.manager_add_product,
        name='manager_add_product'
    ),

    path(
        'store-manager/products/edit/<int:product_id>/',
        views.manager_edit_product,
        name='manager_edit_product'
    ),

    path(
    'store-manager/products/delete/<int:product_id>/',
    views.manager_delete_product,
    name='manager_delete_product'
    ),

    path(
    'product/<int:product_id>/',
    views.product_detail,
    name='product_detail'
    ),

    path(
    'cart/add/<int:product_id>/',
    views.add_to_cart,
    name='add_to_cart'
    ),

    path(
    'cart/',
    views.view_cart,
    name='view_cart'
    ),

    path(
    'cart/update/<int:product_id>/',
    views.update_cart,
    name='update_cart'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path('checkout/', views.checkout, name='checkout'),

    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    path(
        'store-manager/orders/',
        views.manager_order_list,
        name='manager_orders'
    ),

    path(
        'store-manager/orders/<int:order_id>/',
        views.manager_order_detail,
        name='manager_order_detail'
    ),

    path(
        'store-manager/orders/<int:order_id>/update-status/',
        views.update_order_status,
        name='update_order_status'
    ),

    path('my-orders/', views.customer_order_list, name='customer_orders'),
    path(
        'my-orders/<int:order_id>/',
        views.customer_order_detail,
        name='customer_order_detail'
    ),

]