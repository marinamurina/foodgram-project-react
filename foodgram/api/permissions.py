from rest_framework import permissions


class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    """Класс для предоставления прав доступа на изменение контента
    для его владельцев и администраторов.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Класс для органичения прав на создание
    только администраторами.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_admin
            )
        else:
            return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_admin
            )
        else:
            return request.method in permissions.SAFE_METHODS
