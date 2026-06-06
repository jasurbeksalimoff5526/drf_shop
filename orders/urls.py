from django.urls import path
from .views import (
    OrderListCreateGenericView, OrderDetailGenericView, WishlistGenericView, \
    WishlistToggleAPIView,  CartDetailView, CartItemDetailView, CartItemCreateView)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('orders/', OrderListCreateGenericView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailGenericView.as_view(), name='order-detail'),
    path('wishlist/', WishlistGenericView.as_view(), name='wishlist-detail'),
    path('wishlist/toggle/<int:product_id>/', WishlistToggleAPIView.as_view(), name='wishlist-toggle'),
    path('cart/', CartDetailView.as_view()),
    path('cart/add/', CartItemCreateView.as_view()),
    path('cart/item/<int:pk>/', CartItemDetailView.as_view()),

]

urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)