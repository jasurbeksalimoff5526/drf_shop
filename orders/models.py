from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shared.models import BaseModel
from accounts.models import CustomUser
from products.models import Product
from django.db.models import Sum, F
from decimal import Decimal



class Cart(BaseModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"{self.user.username} savati"


    @property
    def total(self):
        return sum(
            (item.subtotal for item in self.items.all()),
            Decimal("0.00")
        )


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            )
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.product.price





PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED = (
    "pending", "processing", "shipped", "delivered", "cancelled"
)


class Order(BaseModel):
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (PROCESSING, PROCESSING),
        (SHIPPED, SHIPPED),
        (DELIVERED, DELIVERED),
        (CANCELLED, CANCELLED),
    )

    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=13)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.status}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.price

    def update_order_total(self):
        total_sum = self.order.items.aggregate(
            total_sum=Sum(F('price') * F('quantity'))
        )['total_sum'] or 0

        self.order.total = total_sum
        self.order.save(update_fields=['total'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_order_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)

        total_sum = order.items.aggregate(
            total_sum=Sum(F("price") * F("quantity"))
        )["total_sum"] or 0

        order.total = total_sum
        order.save(update_fields=["total"])


class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews")
    content = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review"
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.product.name}"


class Wishlist(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"{self.user.username} sevimlilar"