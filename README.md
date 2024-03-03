# Тестовое Задание
Было сложно с алгоритмом решафла групп, но надеюсь я выполнил
1. Нужно зайти изначально в админ панель и создать продукт
2. Потом зайти в api
3. Чтобы пользователь получил доступ к продукту и потом к урокам, а после мог добавиться в группу нужно следующее:
    a. Нажать на кнопку OPTIONS
    b. Нажать на Extra Actions и там выбрать Access
    c. Ввести нужный code_access
4. Далее можете играться создавать новых пользователей и тд
5. Все остальные кнопки в Extra Actions
6. Эндпоинты:
        1. auth/
        2. admin/
        3. api/ ^product/$ [name='product-list']
        4. api/ ^product\.(?P<format>[a-z0-9]+)/?$ [name='product-list']
        5. api/ ^product/(?P<pk>[^/.]+)/$ [name='product-detail']
        6. api/ ^product/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='product-detail']
        7. api/ ^product/(?P<pk>[^/.]+)/access/$ [name='product-access']
        8. api/ ^product/(?P<pk>[^/.]+)/access\.(?P<format>[a-z0-9]+)/?$ [name='product-access']
        9. api/ ^product/(?P<pk>[^/.]+)/lessons/(?P<lesson_id>[^/.]+)/$ [name='product-get-lesson']
        10. api/ ^product/(?P<pk>[^/.]+)/lessons/(?P<lesson_id>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='product-get-lesson']
        11. api/ ^product/(?P<pk>[^/.]+)/lessons/$ [name='product-lessons']
        12. api/ ^product/(?P<pk>[^/.]+)/lessons\.(?P<format>[a-z0-9]+)/?$ [name='product-lessons']
        13. api/ ^product/(?P<pk>[^/.]+)/redistribute/$ [name='product-redistribute-groups']
        14. api/ ^product/(?P<pk>[^/.]+)/redistribute\.(?P<format>[a-z0-9]+)/?$ [name='product-redistribute-groups']
        15. api/ ^group/$ [name='group-list']
        16. api/ ^group\.(?P<format>[a-z0-9]+)/?$ [name='group-list']
        17. api/ ^group/(?P<pk>[^/.]+)/$ [name='group-detail']
        18. api/ ^group/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='group-detail']
        19. api/ ^$ [name='api-root']
        20. api/ ^\.(?P<format>[a-z0-9]+)/?$ [name='api-root']
        21. ^(?P<path>.*)$

Сайгушев Дамир 
https://github.com/gol43
