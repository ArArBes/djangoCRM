from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Supply, Supplier, SupplyProduct, Product
from .serializers import SupplySerializer, SupplierSerializer, SupplyProductSerializer, ProductSerializer, \
    SupplyCreateSerializer
from company.permissions import IsCompanyEmployee
from .permissions import HasCompanyPermission, HasStoragePermission

from decimal import Decimal


class SuplierIdView(APIView):
    permission_classes = [IsCompanyEmployee, HasCompanyPermission]
    serializer_class = SupplierSerializer

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')
        if pk is None:
            return Response({"detail": 'Вы не указали индекс'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        company = user.company

        try:
            supplier = Supplier.objects.get(pk=pk, company=company)
        except Supplier.DoesNotExist:
            return Response(
                {"detail": f"Поставщик с индексом {pk} не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        supplier_serializer = self.serializer_class(supplier)
        return Response(supplier_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk is None:
            return Response({"detail": 'Вы не указали индекс'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        company = user.company
        try:
            supplier = Supplier.objects.get(pk=pk, company=company)
        except Supplier.DoesNotExist:
            return Response(
                {"detail": f"Поставщик с индексом {pk} не найден"},
                status=status.HTTP_404_BAD_REQUEST
            )

        suplier_serializer = self.serializer_class(supplier, data=request.data, partial=True)
        if suplier_serializer.is_valid():
            suplier = suplier_serializer.save()
            return Response(suplier_serializer.data, status=status.HTTP_201_CREATED)

        return Response(suplier_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk is None:
            return Response({"detail": 'Вы не указали индекс'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        company = user.company
        try:
            supplier = Supplier.objects.get(pk=pk, company=company)
        except Supplier.DoesNotExist:
            return Response(
                {"detail": f"Поставщик с индексом {pk} не найден"},
                status=status.HTTP_404_BAD_REQUEST
            )

        title = supplier.title
        supplier.delete()

        return Response(
            {"detail": f"Удален поставщик {title}"},
            status=status.HTTP_200_OK
        )


class SuplierView(APIView):
    permission_classes = [IsCompanyEmployee, HasCompanyPermission]
    serializer_class = SupplierSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        company = user.company

        suppliers = Supplier.objects.filter(company=company)
        suppliers_serializer = self.serializer_class(suppliers, many=True)
        if not len(suppliers):
            return Response(
                {"detail": f"У компании нет поставщиков"},
                status=status.HTTP_200_OK
            )
        return Response(suppliers_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        company = user.company
        suplier_serializer = self.serializer_class(data=request.data)
        if suplier_serializer.is_valid():
            suplier = suplier_serializer.save(company=company)
            return Response(suplier_serializer.data, status=status.HTTP_201_CREATED)

        return Response(suplier_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        deleted_count, _ = Supplier.objects.all().delete()

        return Response(
            {"detail": f"Удалено компаний: {deleted_count}"},
            status=status.HTTP_200_OK
        )


class SupplyView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission, HasStoragePermission]
    serializer_class = SupplySerializer

    def get(self, request, *args, **kwargs):
        company = self.request.user.company
        supplies = Supply.objects.filter(
            supplier__company=company
        ).select_related(
            'supplier'
        ).prefetch_related(
            'supplyproduct_set__product'
        ).order_by('-delivery_date')

        serializer = SupplySerializer(supplies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    permission_classes = [IsCompanyEmployee]


class SupplyCreateView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission, HasStoragePermission]
    serializer_class = SupplyCreateSerializer

    def post(self, request, *args, **kwargs):
        company = request.user.company
        data = request.data
        supply = None

        try:
            supplier = Supplier.objects.get(id=data['supplier_id'], company=company)
            supply = Supply.objects.create(
                supplier=supplier,
                delivery_date=data['delivery_date']
            )
            storage = company.storage
            for product_data in data['products']:
                product = Product.objects.get(id=product_data['product_id'], storage=storage)
                if product_data['quantity'] <= 0:
                    return Response({"detail": f"Указано отрицательное количество товара {product.title}"},
                                    status=status.HTTP_400_BAD_REQUEST)
                product.quantity += product_data['quantity']
                product.purchase_price = product_data['purchase_price']
                product.sale_price = Decimal(product_data['purchase_price']) * Decimal('1.33')
                product.save()
                SupplyProduct.objects.create(
                    supply=supply,
                    product=product,
                    quantity=product_data['quantity']
                )
            return Response(SupplyCreateSerializer(supply).data, status=201)
        except Supplier.DoesNotExist:
            return Response({"detail": "Поставщик не найден"}, status=status.HTTP_400_BAD_REQUEST
                            )

        except Product.DoesNotExist:
            if supply: supply.delete()
            return Response({"detail": f"Товар {product_data['product_id']} не найден"},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        except KeyError:
            return Response({"detail": 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)


class ProductIdView(APIView):
    permission_classes = [IsCompanyEmployee, HasCompanyPermission, HasStoragePermission]
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        storage = request.user.company.storage

        pk = kwargs.get('pk')

        if pk is None:
            return Response({"detail": 'Вы не указали индекс'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=pk, storage=storage)
        except Product.DoesNotExist:
            return Response({"detail": f'Продукт с индексом {pk} не найден'}, status=status.HTTP_400_BAD_REQUEST)

        product_serializer = ProductSerializer(product)
        return Response(product_serializer.data)

    def patch(self, request, *args, **kwargs):
        storage = request.user.company.storage

        pk = kwargs.get('pk')
        if not pk:
            return Response({"detail": "Не указан pk"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=pk, storage=storage)
        except Product.DoesNotExist:
            return Response({"detail": f'Продукт с индексом {pk} не найден'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['quantity'] = product.quantity
        data['storage'] = storage.id

        product_serializer = self.serializer_class(product, data=data, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()
            return Response(product_serializer.data)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        storage = request.user.company.storage

        pk = kwargs.get('pk')
        if not pk:
            return Response({"detail": "Не указан pk"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(pk=pk, storage=storage)
        except Product.DoesNotExist:
            return Response({"detail": f"Товар с индексом {pk} не найден"}, status=status.HTTP_400_BAD_REQUEST)

        title = product.title
        product.delete()
        return Response({"detail": f"Товар '{title}' удален"}, status=status.HTTP_200_OK)


class ProductView(APIView):
    permission_classes = [IsCompanyEmployee, HasCompanyPermission, HasStoragePermission]
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        storage = request.user.company.storage
        products = Product.objects.filter(storage=storage)
        serializer = self.serializer_class(products, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        storage = request.user.company.storage
        try:
            float(request.data.get('sale_price'))
        except ValueError:
            return Response({"detail": "Поле sale_price указано в неверном формате, испоользуйте точку"},
                            status=status.HTTP_400_BAD_REQUEST)
        product = Product.objects.create(
            storage=storage,
            title=request.data.get('title'),
            purchase_price=0,
            sale_price=request.data.get('sale_price'),
            quantity=0
        )

        product_serializer = self.serializer_class(product)
        return Response(product_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        storage = request.user.company.storage

        products = Product.objects.filter(storage=storage)
        deleted_count, _ = products.delete()
        return Response({
            "detail": f"Удалено товаров: {deleted_count}"
        }, status=status.HTTP_200_OK)
