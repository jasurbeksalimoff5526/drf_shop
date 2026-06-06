from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Wishlist
from .models import Cart, Product, CartItem
from .seralizer import OrderSerializer, WishlistSerializer, CartSerializer, CartItemSerializer
from rest_framework.views import APIView


class CartDetailView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateView(CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class CartItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )



class OrderListCreateGenericView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {"error": "Buyurtma berishdan avval mahsulot qo'shing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


from shared.permissions import IsOwnerOrAdmin

class OrderDetailGenericView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    queryset = Order.objects.all()


class WishlistGenericView(RetrieveAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist


class WishlistToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        if product in wishlist.products.all():
            wishlist.products.remove(product)
            return Response({"message": "Wishlistdan olib tashlandi"}, status=status.HTTP_200_OK)
        else:
            wishlist.products.add(product)
            return Response({"message": "Wishlistga qo'shildi"}, status=status.HTTP_201_CREATED)

