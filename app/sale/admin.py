from django.contrib import admin
from .models import Sale, ProductSale


class ProductSaleAdmin(admin.TabularInline):
    model = ProductSale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["id", "company", "buyer_name", "sale_date"]
    inlines = [ProductSaleAdmin]
