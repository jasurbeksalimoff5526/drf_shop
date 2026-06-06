from django.urls import path
from .views import CategoryListAPIView, CategoryDetailAPIView, ProductListAPIView, \
    ProductDetailAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view()),
    path('categories/<slug:slug>/', CategoryDetailAPIView.as_view()),
    path('', ProductListAPIView.as_view()),
    path('<slug:slug>/', ProductDetailAPIView.as_view()),

]

urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
