# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Product, Group


# @receiver(post_save, sender=Product)
# def create_default_groups(sender, instance, created, **kwargs):
#     """Создание трех групп при создании нового продукта"""
#     if created:
#         for i in range(1, 2):
#             Group.objects.create(
#                 name=f"Группа {i}",
#                 product=instance,
#             )