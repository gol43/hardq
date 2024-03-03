from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from products.models import Product, UserProductAccess, Lesson, Group, GroupStudents, User
from .serializers import ProductSerializer, LessonSerializer, GroupSerialzer
from .permissions import IsAdminOrAuthorOrReadOnly, CanAccess, HasAccess
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.utils import timezone


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


    def list(self, request, *args, **kwargs):
        """Получение списка данных"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        """Проверка на то, прошёл ли юзер проверка по коду-продукта"""
        product = self.get_object()
        user_has_access = UserProductAccess.objects.filter(user=request.user, product=product).exists()
        if not user_has_access:
            return Response({"detail": "У вас нет доступа к этому контенту."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(product)
        return Response(serializer.data)


    def add_user_to_group(self, user, product):
        """Добавление юзера в группу"""
        # Самая красивая и логичная часть кода:)
        groups = Group.objects.filter(product=product)
        
        # Получаем автора продукта
        author = product.author

        if groups.exists(): 
            for group in groups:
                # Проверяем, что пользователь не является автором продукта
                if user != author and self.has_available_slots(group, product):
                    self.add_user_to_existing_group(user, group)
                    return
            # Если пользователь не был добавлен в существующую группу, создаем новую группу
            if user != author:
                self.create_group_and_add_user(user, product)
        else:
            # Если нет существующих групп, создаем новую группу
            self.create_group_and_add_user(user, product)


    def has_available_slots(self, group, product):
        """Проверка свободных мест"""
        students_count = GroupStudents.objects.filter(group=group).count()
        return students_count < product.default_max_users


    def add_user_to_existing_group(self, user, group):
        """Добавление юезра в существующую группу"""
        GroupStudents.objects.create(group=group, students=user)


    def create_group_and_add_user(self, user, product):
        """Создание названия группы и самой группы для продукта"""
        group_name = self.get_unique_group_name(product.name.replace(' ', '_').lower() + "_default_group", product)
        new_group = Group.objects.create(product=product, name=group_name)
        # Добавление юзера в новую группу
        GroupStudents.objects.create(group=new_group, students=user)


    def get_unique_group_name(self, base_name, product):
        """Составление уникального названия группы для продукта"""
        
        # Это нужно для уникального создания группы, иначе  студенты не добавляются
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")

        unique_identifier = f"{product.id}_{timestamp}"
        return f"{base_name}_{unique_identifier}"


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, HasAccess])
    def lessons(self, request, *args, **kwargs):
        """Получение списка уроков"""
        product = self.get_object()
        user_has_access = UserProductAccess.objects.filter(user=request.user, product=product).exists()
        if not user_has_access:
            return Response({"detail": "У вас не прав на это действие."}, status=status.HTTP_403_FORBIDDEN)
        lessons = Lesson.objects.filter(product=product)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['get'], url_path='lessons/(?P<lesson_id>[^/.]+)',
            permission_classes=[IsAuthenticated, HasAccess])
    def get_lesson(self, request, *args, **kwargs):
        """Поулчение конкретного урока"""
        product = self.get_object()
        lesson_id = kwargs.get('lesson_id')
        user_has_access = UserProductAccess.objects.filter(user=request.user, product=product).exists()
        if not user_has_access:
            return Response({"detail": "У вас не прав на это действие."}, status=status.HTTP_403_FORBIDDEN)
        lesson = get_object_or_404(Lesson, id=lesson_id, product=product)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)


    @action(detail=True, methods=['get'], url_path='redistribute',
            permission_classes=[IsAuthenticated, IsAdminOrAuthorOrReadOnly])
    def redistribute_groups(self, request, *args, **kwargs):
        product = self.get_object()
        user_has_access = UserProductAccess.objects.filter(user=request.user, product=product).exists()

        # Проверка наличия доступа у пользователя
        if not user_has_access:
            return Response({"detail": "У вас нет доступа к этому действию."}, status=status.HTTP_403_FORBIDDEN)

        # Проверка, что продукт еще не начался
        if not product.get_start_date_status_bool():
            return Response({"detail": "Перераспределение возможно только, если продукт ещё не начался."},
                            status=status.HTTP_400_BAD_REQUEST)

        groups = Group.objects.filter(product=product)
        students_count = GroupStudents.objects.filter(group__in=groups).count()

        # Проверка наличия достаточного количества студентов для перераспределения
        if students_count < product.default_min_users * groups.count():
            return Response({"detail": "Недостаточно студентов для перераспределения."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Получение информации о количестве студентов в каждой группе
        students_per_group = [GroupStudents.objects.filter(group=group).count() for group in groups]

        # Проверка, что все группы содержат хотя бы default_min_users студентов
        if all(GroupStudents.objects.filter(group=group).count() >= product.default_min_users for group in groups):
            # Проверка, что нет групп с одним человеком
            if any(GroupStudents.objects.filter(group=group).count() == 1 for group in groups):
                return Response({"detail": "Невозможно пересобрать группы. Есть группа с одним человеком."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Проверка, что нет группы с максимальным количеством пользователей
            if any(GroupStudents.objects.filter(group=group).count() == product.default_max_users for group in groups):
                return Response({"detail": "Невозможно пересобрать группы. Есть группа, содержащая максимальное количество пользователей."},
                                status=status.HTTP_400_BAD_REQUEST)

            target_students_per_group = students_count // groups.count()

            all_students = []   # Создается пустой список
            for group in groups:    # Проходимся по каждой группе
                # Теперь запрашываем данные из БД об определённых группах
                # values_list(Берём айдишники студенетов в списка, 
                # flat=True ОЧЕНЬ ПОЛЕЗНАЯ ВЕЩЬ, которая помогает с тем, чтобы не получить кортеж)
                # Можно наверное использовать extend, но append более приятен глазу
                student_id = GroupStudents.objects.filter(group=group).values_list('students', flat=True)
                all_students.append(student_id)
            # После получения нужных студентов-юзеров можем удалять студентов из групп
            for group in groups:
                GroupStudents.objects.filter(group=group).delete()
            # теперь будем занаво добавлять студентов во всех .count() групп
            for i in range(groups.count()):
                start_index = i * target_students_per_group # Вычисляем начальный айди студентов для текущей группы
                end_index = (i + 1) * target_students_per_group # Вычисляем конечный айди студентов для текущей группы.
                group_student_ids = all_students[start_index:end_index] # Вычисляем конечный срез айди студентов для текущей группы.
                group = groups[i] # Получаем текущую группу, к которой будут добавлены студенты
                for student in group_student_ids: # Проходим по каждому идентификатору студента в текущем диапазоне
                    student = User.objects.get(pk=student) # Получаем объект студента из БД
                    GroupStudents.objects.create(group=group, students=student) # Создаём

            return Response({"detail": "Группы пересобраны успешно."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Невозможно пересобрать группы."}, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAuthenticated, CanAccess])
    def access(self, request, *args, **kwargs):
        """Код-продукта"""
        product = self.get_object()
        # Проверяем наличие юзера в нужном БД для доступа
        user_has_access = UserProductAccess.objects.filter(user=request.user, product=product).exists()
        # Если есть в БД, тогда даём контент
        if user_has_access:
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        # Получаем сам код-продукта
        code_access = request.data.get('code_access', None)
        if product.code_access == code_access: # Если код-продукта правильный
            UserProductAccess.objects.create(user=request.user, product=product) # Заносим в БД для доступа

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.add_user_to_group(request.user, product) # Заносим в группу сразу
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Неправильнный ккод-продукта."}, status=status.HTTP_400_BAD_REQUEST)
    
# Это всё надо, чтобы только нужные юзры могли производить действия
    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrAuthorOrReadOnly]
        super().destroy(request, *args, **kwargs)
        return redirect('api:product-list')


    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrAuthorOrReadOnly]
        return super().update(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerialzer
    pagination_class = None