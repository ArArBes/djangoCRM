from rest_framework.views import APIView
from authenticate.models import User
from .models import Company, Storage
from .serializers import CompanySerializer,StorageSerializer, EmployeeSerializer
from .permissions import IsCompanyOwner, IsCompanyEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class CompanyViewSet(APIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_serializer = CompanySerializer(data=request.data)

        user = request.user
        if user.company is not None:
            company_title = user.company.title
            return Response({"detail": f"На вас уже зарегистрирована компания {company_title}."}, status=status.HTTP_400_BAD_REQUEST)

        if company_serializer.is_valid():
            company = company_serializer.save(owner=request.user)
            user.company = company
            user.is_company_owner = True
            user.save()
            return Response(company_serializer.data, status=status.HTTP_201_CREATED)

        return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.company is None:
            return Response({"detail": "У вас нет привязанных компаний."}, status=status.HTTP_400_BAD_REQUEST)

        company_serializer = CompanySerializer(user.company)
        return Response(company_serializer.data)

class CompanyIdViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"detail": "Компания с таким id не найдена."}, status=status.HTTP_404_NOT_FOUND)

        company_serializer = CompanySerializer(company)
        return Response(company_serializer.data)

class CompanyOwnerViewSet(APIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsCompanyOwner]

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, 'company') or user.company is None:
            return Response({"detail": "У вас нет привязанных компаний."}, status=status.HTTP_400_BAD_REQUEST)
        company_serializer = CompanySerializer(user.company, data=request.data, partial=True)
        if company_serializer.is_valid():
            company_serializer.save()
            return Response(company_serializer.data, status=status.HTTP_201_CREATED)
        return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        if not hasattr(user, 'company') or user.company is None:
            return Response({"detail": "У вас нет привязанных компаний."}, status=status.HTTP_400_BAD_REQUEST)

        company = user.company
        company_title = company.title
        company.delete()

        return Response({"detail": f"Компания {company_title} успешно удалена."}, status=status.HTTP_200_OK)



class StorageViewSetGet(APIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    permission_classes = [IsCompanyEmployee]

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.company:
            return Response({"detail": "У пользователя нет компании."}, status=status.HTTP_400_BAD_REQUEST)

        company = user.company

        if not hasattr(company, 'storage') or company.storage is None:
            return Response({"detail": "У компании нет ни одного склада."}, status=status.HTTP_400_BAD_REQUEST)

        storage_serializer = StorageSerializer(company.storage)
        storage_serializer.data.update({'company': company.title})

        return Response(storage_serializer.data)

class StorageViewSet(APIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer

    permission_classes = [IsCompanyOwner]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'company') or user.company is None:
            return Response({"detail": "У пользователя нет компании."}, status=status.HTTP_400_BAD_REQUEST)

        company = user.company

        if Storage.objects.filter(company=company).exists():
            return Response({"detail": "Компания уже имеет склад."},
                            status=status.HTTP_400_BAD_REQUEST)

        storage_serializer = StorageSerializer(data=request.data)

        if storage_serializer.is_valid():
            storage_serializer.save(company=company)
            return Response(storage_serializer.data, status=status.HTTP_201_CREATED)

        return Response(storage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.company:
            return Response({"detail": "У пользователя нет компании."}, status=status.HTTP_400_BAD_REQUEST)

        company = user.company
        if not hasattr(company, 'storage') or company.storage is None:
            return Response({"detail": "У компании нет ни одного склада."},
                            status=status.HTTP_400_BAD_REQUEST)
        storage = company.storage
        storage_serializer = StorageSerializer(storage, data=request.data, partial=True)

        if storage_serializer.is_valid():
            storage_serializer.save()
            return Response(storage_serializer.data, status=status.HTTP_200_OK)

        return Response(storage_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = self.request.user

        if not user.company:
            return Response({"detail": "У пользователя нет компании."}, status=status.HTTP_400_BAD_REQUEST)

        company = user.company

        if not company.storage:
            return Response({"detail": "У компании нет склада для удаления."}, status=status.HTTP_400_BAD_REQUEST)

        storage = company.storage
        storage_address = storage.address
        storage.delete()

        return Response({"detail": f"Склад по адресу {storage_address} успешно удален."}, status=status.HTTP_200_OK)



class EmployeesViewSet(APIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsCompanyOwner]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.company:
            return Response({"detail": "У пользователя нет привязанной компании."}, status=status.HTTP_400_BAD_REQUEST)

        employees = User.objects.filter(company=user.company)
        serializer = self.serializer_class(employees, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.company:
            return Response({"detail": "У пользователя нет привязанной компании."}, status=status.HTTP_400_BAD_REQUEST)

        employee_email = request.data.get('email')
        if not employee_email:
            return Response({"detail": "Не указан email сотрудника."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = User.objects.get(email=employee_email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if employee.company:
            return Response({"detail": "У сотрудника уже есть привязанная компания."},
                            status=status.HTTP_400_BAD_REQUEST)

        employee.company = user.company
        employee.is_company_owner = False
        employee.save()

        employee_serializer = EmployeeSerializer(employee)

        return Response(employee_serializer.data, status=status.HTTP_201_CREATED)

class EmployeeViewSetDelete(APIView):
    permission_classes = [IsCompanyOwner]
    serializer_class = EmployeeSerializer
    def delete(self, request, *args, **kwargs):
        user = request.user

        if not user.company:
            return Response({"detail": "У пользователя нет привязанной компании."}, status=status.HTTP_400_BAD_REQUEST)

        employee_id = kwargs.get('employee_id')

        if not employee_id:
            return Response({"detail": "Не указан ID сотрудника."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = User.objects.get(id=employee_id, company=user.company)
            employee_email = employee.email
            employee.company = None
            employee.save()
            return Response({"detail": f"Сотрудник {employee_email} успешно отвязан от компании."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "Сотрудник не найден или не является членом вашей компании."},
                            status=status.HTTP_400_BAD_REQUEST)
