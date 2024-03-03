from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, GroupViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'group', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]