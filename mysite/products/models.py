from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Product(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    cost = models.PositiveIntegerField()
    default_min_users = models.PositiveIntegerField(default=1)
    default_max_users = models.PositiveIntegerField(default=3)
    code_access = models.CharField(max_length=10, unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    start_date_status_bool = models.BooleanField(default=True)
    
    def clean(self):
        if self.start_date <= timezone.now():
            raise ValidationError("Дата и время старта должны быть в будущем.")
        
    def clean(self):
        if self.default_max_users <= self.default_min_users:
            raise ValidationError("Максимальное количество пользователей должно быть больше минимального.")

    def get_start_date_status_bool(self):
        now = timezone.now()
        return self.start_date > now

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    video = models.URLField()

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.TextField(unique=True)
    students = models.ManyToManyField(User, through='GroupStudents', related_name='unique_groups')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'product']


class GroupStudents(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    students = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_students')

    class Meta:
        unique_together = ['group', 'students']


class UserProductAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
