from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Sum, Avg, Count
from datetime import date

from supply.permissions import HasCompanyPermission, HasStoragePermission
from .models import Sale, ProductSale
from supply.models import Product
from .serializers import SaleSerializer, ProductSaleSerializer, SalePatchSerializer, AnalyticsSerializer


class SaleGetView(ListAPIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]
    pagination_class = PageNumberPagination
    serializer_class = SaleSerializer

    def get_queryset(self):
        company = self.request.user.company
        return Sale.objects.filter(company=company).prefetch_related('product_sales')


class SalePatchView(APIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]
    serializer_class = SalePatchSerializer

    def patch(self, request, *args, **kwargs):
        company = request.user.company
        id = kwargs.get('id')

        try:
            sale = Sale.objects.get(id=id, company=company)
            serializer = SalePatchSerializer(sale, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Sale.DoesNotExist:
            return Response({"detail": f"Продажа с id {id} не найдена"},
                            status=status.HTTP_404_NOT_FOUND)


class SaleView(APIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]
    serializer_class = SaleSerializer

    def post(self, request, *args, **kwargs):
        company = request.user.company
        storage = company.storage
        data = request.data
        try:
            sale = Sale.objects.create(company=company, buyer_name=data['buyer_name'], sale_date=date.today())

            for product in data["product_sales"]:
                product_id = product["product_id"]
                quantity = product["quantity"]

                storage_product = Product.objects.get(id=product_id)
                if storage_product.quantity < quantity:
                    sale.delete()
                    res = f'Количество продукта {storage_product.title}(id:{product_id}) меньше указанного. Максимальное количество {storage_product.quantity}'
                    return Response({"detail": res}, status=status.HTTP_400_BAD_REQUEST)

            for product in data["product_sales"]:
                product_id = product["product_id"]
                quantity = product["quantity"]
                storage_product = Product.objects.get(id=product_id)
                storage_product.quantity -= quantity
                storage_product.save()
                ProductSale.objects.create(product=storage_product, sale=sale, quantity=quantity)

        except Product.DoesNotExist:
            if sale: sale.delete()
            return Response({"detail": f'Товар с индексом {product_id} не найден'})

        return Response(
            {"ditail": f'Покупка id{sale.id} от {sale.sale_date} реализована. Покупатель {sale.buyer_name}'},
            status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        company = request.user.company
        sales = Sale.objects.filter(company=company)
        deleted_ids = list(sales.values_list('id', flat=True))
        product_sales = ProductSale.objects.filter(sale__in=sales).values('product_id', 'quantity')
        for product_sale in product_sales:
            Product.objects.filter(id=product_sale['product_id']).update(
                quantity=F('quantity') + product_sale['quantity'])

        sales.delete()
        return Response({"ditail": f'Поставки удалены id:{deleted_ids}'},
                        status=status.HTTP_200_OK)


class SaleIdView(APIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]
    serializer_class = SaleSerializer

    def get(self, request, *args, **kwargs):
        id = kwargs.get('id')
        company = request.user.company
        try:
            sale = Sale.objects.get(id=id, company=company)
            serializer = SaleSerializer(sale)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Sale.DoesNotExist:
            return Response({"detail": f'Покупка с id:{id} не найдена'},
                            status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('id')
        company = request.user.company

        try:
            sale = Sale.objects.get(id=id, company=company)
        except Sale.DoesNotExist:
            return Response({"detail": f'Покупка с id:{id} не найдена'},
                            status=status.HTTP_404_NOT_FOUND)

        product_sales = ProductSale.objects.filter(sale=sale).select_related('product')
        products_id = []
        for ps in product_sales:
            products_id.append(str(ps.product.id))
            ps.product.quantity += ps.quantity
            ps.product.save()
        sale_serializer = SaleSerializer(sale).data
        sale.delete()
        products_id = ','.join(products_id)
        return Response({
            "detail": f"Удалена поставка {sale_serializer['id']} от {sale_serializer['sale_date']}. Продукты: {products_id}"},
            status=status.HTTP_200_OK)


from drf_spectacular.utils import extend_schema, OpenApiParameter


class AnalyticsProfitView(APIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]
    serializer_class = AnalyticsSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter('period', type=str, enum=['day', 'week', 'month', 'year'], default='day'),
            OpenApiParameter('date_end', type=str, required=False),
            OpenApiParameter('date_start', type=str, required=False),
        ]
    )
    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        company = request.user.company
        data = serializer.validated_data

        period = data.get('period', 'day')
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)

        sales = self.get_sales_queryset(company, period, start_date, end_date)
        profit_stats = self.get_profit_stats(sales)

        if start_date or end_date:
            period = f'{start_date} - {end_date}'

        return Response({
            'period': period,
            'profit': profit_stats
        })

    def get_sales_queryset(self, company, period, start_date, end_date):
        today = date.today()

        if start_date and end_date:
            return Sale.objects.filter(
                company=company,
                sale_date__range=[start_date, end_date]
            )
        elif period == 'day':
            return Sale.objects.filter(company=company, sale_date=today)
        elif period == 'week':
            week = today - timedelta(days=7)
            return Sale.objects.filter(company=company, sale_date__gte=week)
        elif period == 'month':
            month = today.replace(day=1)
            return Sale.objects.filter(company=company, sale_date__gte=month)
        elif period == 'year':
            year = today.replace(month=1, day=1)
            return Sale.objects.filter(company=company, sale_date__gte=year)
        else:
            return Sale.objects.filter(company=company)

    def get_profit_stats(self, sales):
        product_sales = ProductSale.objects.filter(sale__in=sales)

        total_profit = product_sales.aggregate(total=Sum(F('quantity') * F('product__sale_price')))
        total_profit = total_profit['total'] or Decimal('0')

        net_profit = product_sales.aggregate(
            net=Sum(F('quantity') * (
                    F('product__sale_price') - F('product__purchase_price')
            ))
        )
        net_profit = net_profit['net'] or Decimal('0')

        sales_count = sales.count()
        product_sales_count = product_sales.count()

        return {
            'total_profit': float(total_profit),
            'net_profit': float(net_profit),
            'sales_count': sales_count,
            'product_count': product_sales_count
        }


class AnalyticsTopProductView(APIView):
    permission_classes = [HasCompanyPermission, HasStoragePermission]

    def get(self, request):
        company = request.user.company
        sales = Sale.objects.filter(company=company)

        top_products = self.get_top_products(sales)
        top_profit_products = self.get_top_profit_products(sales)

        return Response({
            'top_products': top_products[:10],
            'top_profit_products': top_profit_products[:10],
        })

    def get_top_products(self, sales):
        return ProductSale.objects.filter(sale__in=sales).values(
            'product__title',
            'product__id'
        ).annotate(
            total_quantity=Sum('quantity'),
            sales_count=Count('id')
        ).order_by('-total_quantity')

    def get_top_profit_products(self, sales):
        return ProductSale.objects.filter(sale__in=sales).values(
            'product__title',
            'product__id'
        ).annotate(
            net_profit=Sum(F('quantity') * (
                    F('product__sale_price') - F('product__purchase_price')
            ))
        ).order_by('-net_profit')
