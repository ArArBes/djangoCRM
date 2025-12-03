from rest_framework import serializers
from .models import Company, Storage
from authenticate.models import User

class StorageSerializer(serializers.ModelSerializer):
    company_title = serializers.ReadOnlyField(source='company.title')
    # address = serializers.CharField(required=False, default=None)
    class Meta:
        model = Storage
        fields = ['id', 'address','company_title']
        read_only_fields = ['company_title']


class CompanySerializer(serializers.ModelSerializer):
    storage = StorageSerializer(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Company
        fields = ['id', 'title', 'inn', 'owner', 'storage']
        read_only_fields = ['owner']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'is_company_owner', 'company']
        read_only_fields = ['company']