from rest_framework import permissions

class HasCompanyPermission(permissions.BasePermission):
    message = 'У вас нет привязанных компаний.'

    def has_permission(self, request, view):
        return bool(getattr(request.user, 'company', None))

class HasStoragePermission(permissions.BasePermission):
    message = 'У компании нет склада.'

    def has_permission(self, request, view):
        company = getattr(request.user, 'company', None)
        return bool(getattr(company, 'storage', None))