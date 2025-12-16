from django.urls import path
from .views import SaleView, SaleIdView, SaleGetView, SalePatchView, AnalyticsProfitView, AnalyticsTopProductView

urlpatterns = [
    path('', SaleView.as_view(), name="sale"),
    path('get/', SaleGetView.as_view(), name="sale"),
    path('sale/<int:id>', SaleIdView.as_view(), name="sale"),
    path('patch/<int:id>', SalePatchView.as_view(), name="sale"),
    path('analytics/profit', AnalyticsProfitView.as_view(), name='analytics'),
    path('analytics/top-products/', AnalyticsTopProductView.as_view(), name='top-products'),
]