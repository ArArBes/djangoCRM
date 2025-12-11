from django.contrib import admin
from .models import Supply,Supplier,Product, SupplyProduct


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id','supplier','delivery_date')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id','title','inn')

@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('id','supply','product', 'quantity')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','storage','title','purchase_price', 'sale_price', 'quantity')
