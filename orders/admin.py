from django.contrib import admin
from .models import Order, OrderItem, Wishlist, Review, Cart, CartItem


admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(Wishlist)