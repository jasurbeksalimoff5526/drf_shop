from django.urls import path
from .views import CategoryListAPIView, CategoryDetailAPIView, ProductListAPIView, \
    ProductDetailAPIView, CartDetailView, CartItemDetailView, CartItemCreateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view()),
    path('categories/<slug:slug>/', CategoryDetailAPIView.as_view()),
    path('products/', ProductListAPIView.as_view()),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view()),
    path('cart/', CartDetailView.as_view()),
    path('cart/add/', CartItemCreateView.as_view()),
    path('cart/item/<int:pk>/', CartItemDetailView.as_view()),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
