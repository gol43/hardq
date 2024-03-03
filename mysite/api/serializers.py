from rest_framework import serializers
from products.models import Product, Lesson, Group, UserProductAccess
from django.utils import timezone

class UserProductAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductAccess
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'video']


class ProductSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()
    code_access = serializers.CharField(write_only=True)
    start_date_status = serializers.SerializerMethodField()
    start_date_status_bool = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'author', 'lesson', 'code_access', 'start_date_status', 'start_date_status_bool']

    def get_lesson(self, obj):
        lessons = Lesson.objects.filter(product=obj)
        lesson_data = [{'name': lesson.name} for lesson in lessons]
        return {'count of lessons': len(lesson_data), 'lessons': lesson_data}

    def get_start_date_status(self, obj):
        now = timezone.now()

        if obj.start_date > now:
            start_date_formatted = obj.start_date.strftime("%Y-%m-%d, %H:%M")
            return f"Начнётся {start_date_formatted}"
        elif obj.start_date <= now:
            start_date_formatted = obj.start_date.strftime("%Y-%m-%d, %H:%M")
            return f"Уже началось {start_date_formatted}"

    def get_start_date_status_bool(self, obj):
        now = timezone.now()
        return obj.start_date > now

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['start_date_status_bool'] = instance.start_date_status_bool
        return data


class GroupSerialzer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'students']

    def get_students(self, obj):
        students_data = []
        for student in obj.students.all():
            student = {'id': student.id, 'name': student.username}
            students_data.append(student)
        return students_data
