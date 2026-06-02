from .models import Product, Category, Cart, CartItem
from rest_framework.exceptions import ValidationError
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise ValidationError(
                "Category name is required."
            )
        if len(value) < 3:
            raise ValidationError(
                "Category name must be at least 3 characters."
            )

        return value


class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'category_name', 'price', 'stock', 'image', 'seller'
        ]
        read_only_fields = ['slug', 'seller']


    def validate_stock(self, value):
        if value < 0:
            raise ValidationError(
                "Maxsulot soni manfiy bo'lishi mumkin emas."
            )
        return value

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise ValidationError(
                "Mahsulot nomi kiritilishi shart."
            )

        return value

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

