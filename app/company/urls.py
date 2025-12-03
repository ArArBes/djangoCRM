from django.urls import  path
from .views import CompanyViewSet,CompanyIdViewSet, CompanyOwnerViewSet,StorageViewSetGet, StorageViewSet, EmployeesViewSet, EmployeeViewSetDelete
from django.conf import settings


urlpatterns = [
    path('company/', CompanyViewSet.as_view(), name='company'),
    path('companies/<int:company_id>/', CompanyIdViewSet.as_view(), name='company_detail'),
    path('company/edit/', CompanyOwnerViewSet.as_view(), name='company_edit'),
    path('storage/', StorageViewSet.as_view(), name='storage_create_update_delete'),
    path('storage/detail/', StorageViewSetGet.as_view(), name='storage_detail'),
    path('employee/', EmployeesViewSet.as_view(), name='employee'),
    path('employee/<str:employee_id>/', EmployeeViewSetDelete.as_view(), name='delete_employee'),
]