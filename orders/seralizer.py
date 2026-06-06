from rest_framework import serializers
from .models import Order, OrderItem, Wishlist, Cart, CartItem
from products.serializer import ProductSerializer
from rest_framework.exceptions import ValidationError



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']

    def validate(self, attrs):
        product = attrs.get(
            "product",
            getattr(self.instance, "product", None)
        )

        quantity = attrs.get(
            "quantity",
            getattr(self.instance, "quantity", None)
        )

        if product is None:
            raise ValidationError(
                {"product": "Mahsulot tanlanishi kerak"}
            )

        if quantity is None:
            raise ValidationError(
                {"quantity": "Miqdor kiritilishi kerak"}
            )

        if quantity > product.stock:
            raise ValidationError(
                {"quantity": "Maxsulot soni yetarli emas"}
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        cart, _ = Cart.objects.get_or_create(user=user)

        product = validated_data["product"]
        quantity = validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        new_quantity = (
            cart_item.quantity + quantity
            if not created
            else quantity
        )

        if new_quantity > product.stock:
            raise ValidationError({
                "quantity": "Mahsulot soni yetarli emas."
            })

        cart_item.quantity = new_quantity
        cart_item.save()

        return cart_item

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='total')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']
        read_only_fields = [
            "user",
            "items",
            "total_price"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'address', 'phone', 'note', 'items']
        read_only_fields = ['status', 'total']


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']