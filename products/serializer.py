from .models import Product, Category
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


