# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('view/', views.view_cart, name='view_cart'),  # URL to view the cart
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # URL to add product to cart
    path('update/<int:cart_id>/', views.update_cart, name='update_cart'),  # URL to update cart item quantity
    path('remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),  # URL to remove product from cart
    path('view/', views.view_cart, name='view_cart'),
    path("checkouts/", views.some_view, name="some_view"),
    path('empty/', views.empty_cart, name='empty_cart'),
]
