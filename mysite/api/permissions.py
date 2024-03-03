from rest_framework.permissions import BasePermission
from products.models import UserProductAccess


class IsAdminOrAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Разрешить только чтение для всех юзеров
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Проверить, является ли пользователь администратором или автором продукта
        user = request.user
        product = view.get_object()
        return user.is_staff or product.author == user

    def has_object_permission(self, request, view, obj):
        # Разрешить только автору изменять или удалять объект(Плохо работает!!!Проверить)
        user = request.user
        return obj.author == user


class CanAccess(BasePermission):
    def has_permission(self, request, view):
        # Все пользователи теперь могут писать код-продукта
        return request.method in ['GET', 'POST']

class HasAccess(BasePermission):
    def has_permission(self, request, view):
        # Чтение для юезров, который уже правильно вводили код-продукта
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Провекра доступа к проудкту(Повтор в views.py!!!Исправить)
        return UserProductAccess.objects.filter(user=request.user, product=view.get_object()).exists()
