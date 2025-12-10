from django.urls import path
from .views import ProductView, ProductIdView, SuplierView, SuplierIdView, SupplyView, SupplyCreateView

urlpatterns = [
    path('products/', ProductView.as_view(), name='products'),
    path('product/<int:pk>/', ProductIdView.as_view(), name='product'),
    path('suppliers/', SuplierView.as_view(), name='suppliers'),
    path('supplier/<int:pk>/', SuplierIdView.as_view(), name='supplier'),
    path('supplies/', SupplyView.as_view(), name='supply'),
    path('supply/', SupplyCreateView.as_view(), name='supply-create'),
]
