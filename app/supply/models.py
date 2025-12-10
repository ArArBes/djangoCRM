from django.db import models


class Supplier(models.Model):
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    inn = models.CharField(max_length=12, unique=True)


class Supply(models.Model):
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)
    delivery_date = models.DateField()


class SupplyProduct(models.Model):
    supply = models.ForeignKey("Supply", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Product(models.Model):
    storage = models.ForeignKey("company.Storage", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    purchase_price = models.DecimalField(max_digits=20,decimal_places=2)
    sale_price = models.DecimalField(max_digits=20,decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

