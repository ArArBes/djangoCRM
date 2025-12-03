from django.contrib import admin
from .models import User
from company.models import Company, Storage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active', 'is_superuser')
    list_display_links = ('id', 'email')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'inn')

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'address')