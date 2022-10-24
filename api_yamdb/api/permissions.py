from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    message = "У Вас нет доступа на изменение контента!"

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


class IsAuthorAdminModerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (obj.author == request.user
                    or (request.user.is_authenticated
                        and (request.user.is_moder
                             or request.user.is_admin))
                    )
                )


class UserMePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'PATCH' or 'GET':
                return True
        return False


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role == 'admin' or request.user.is_admin:
                return True
            elif request.method == 'GET' and request.user.role != 'admin':
                return False
            elif (request.method == 'GET' or 'PATCH'
                  and request.user.role == 'admin'):
                return True
            elif request.method == 'DELETE' and request.user.is_admin:
                return True
        return False
