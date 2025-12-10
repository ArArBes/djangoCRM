from rest_framework.permissions import BasePermission

class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_company_owner)

class IsCompanyEmployee(BasePermission):
    message = 'Вы не привязаны к компании'

    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.company is not None)