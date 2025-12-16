from rest_framework import serializers
from .models import Sale, ProductSale
from datetime import date


class ProductSaleSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')

    class Meta:
        model = ProductSale
        fields = ["product_id", "quantity"]


class SaleSerializer(serializers.ModelSerializer):
    product_sales = ProductSaleSerializer(many=True)

    class Meta:
        model = Sale
        fields = ["id", "company", "buyer_name", "sale_date", "product_sales"]
        read_only_fields = ["company", "sale_date"]


class SalePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ["buyer_name", "sale_date"]

    def validate_sale_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Дата продажи не может быть в будущем")
        return value

class AnalyticsSerializer(serializers.Serializer):
    period = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'year'],
        default='day'
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

