from rest_framework import serializers
from .models import Supply, Supplier, SupplyProduct, Product


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'company', 'title', 'inn']
        read_only_fields = ['company']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'storage', 'title', 'purchase_price', 'sale_price', 'quantity']
        read_only_fields = ['storage', 'quantity', 'purchase_price']


class SupplyProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    purchase_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )

    class Meta:
        model = SupplyProduct
        fields = ['product_id', 'quantity', 'purchase_price']


class SupplyProductGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyProduct
        fields = ['product', 'quantity']


class SupplySerializer(serializers.ModelSerializer):
    supplier_id = serializers.IntegerField(source='supplier.id', read_only=True)
    products = SupplyProductGetSerializer(source='supplyproduct_set', many=True, read_only=True)

    class Meta:
        model = Supply
        fields = ['id', 'supplier_id', 'delivery_date', 'products']


class SupplyCreateSerializer(serializers.ModelSerializer):
    supplier_id = serializers.IntegerField(write_only=True)
    products = SupplyProductSerializer(many=True, write_only=True)

    class Meta:
        model = Supply
        fields = ['supplier_id', 'delivery_date', 'products']

    def create(self, validated_data):
        supplier = Supplier.objects.get(
            id=validated_data.pop('supplier_id'),
            company=self.context['request'].user.company
        )
        validated_data['supplier'] = supplier
        return super().create(validated_data)
