"""
Модуль urls.py приложения accounts

Этот файл определяет маршруты URL для приложения accounts.
Маршруты связывают URL-адреса с представлениями (views), которые обрабатывают запросы.

Все URL приложения accounts имеют префикс "/accounts/" в главном файле urls.py проекта.
"""

# Импорт функции path для создания маршрутов URL
from django.urls import path
# Импорт представлений (views) приложения
from . import views

# Пространство имен приложения для использования в шаблонах и других местах
# Позволяет обращаться к маршрутам как "accounts:register" вместо полного пути
app_name = "accounts"

# Список маршрутов URL приложения
urlpatterns = [
    # Маршрут для страницы регистрации
    # URL: /accounts/register/
    # Обработчик: функция register_view из views.py
    # Имя маршрута: "register" (используется как accounts:register)
    path("register/", views.register_view, name="register"),
    
    # Маршрут для страницы входа в систему
    # URL: /accounts/login/
    # Обработчик: функция login_view из views.py
    # Имя маршрута: "login" (используется как accounts:login)
    path("login/", views.login_view, name="login"),
    
    # Маршрут для выхода из системы
    # URL: /accounts/logout/
    # Обработчик: функция logout_view из views.py
    # Имя маршрута: "logout" (используется как accounts:logout)
    # Требует авторизации (декоратор @login_required в views.py)
    path("logout/", views.logout_view, name="logout"),
    
    # Маршрут для страницы личного кабинета (профиля)
    # URL: /accounts/profile/
    # Обработчик: функция profile_view из views.py
    # Имя маршрута: "profile" (используется как accounts:profile)
    # Требует авторизации (декоратор @login_required в views.py)
    path("profile/", views.profile_view, name="profile"),
]

