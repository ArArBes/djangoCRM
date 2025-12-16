from django.db import models

class Sale(models.Model):
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=200)
    sale_date = models.DateField()

    def __str__(self):
        return f"Продажа {self.company.title} от {self.sale_date}"

class ProductSale(models.Model):
    product = models.ForeignKey("supply.Product", on_delete=models.CASCADE)
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE, related_name='product_sales')
    quantity = models.IntegerField()

    def __str__(self):
        return f"Продукт {self.product.title} продажи"
