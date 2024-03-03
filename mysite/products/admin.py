from django.contrib import admin
from .models import Product, Lesson, Group, GroupStudents, UserProductAccess

                # НАД АДМИНКОЙ Я ТОЛКОМ НЕ РАБОТАЛ

class GroupStudentsInline(admin.TabularInline):
    model = GroupStudents
    extra = 1
    min_num = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'pub_date','cost')
    search_fields = ('name', 'author')
    list_filter = ('pub_date',)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('product', 'name')


class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupStudentsInline, )


admin.site.register(Product, ProductAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(UserProductAccess)