from django.urls import path, include
from . import views
from .views import user_login, user_logout

urlpatterns = [
    path('', views.lobby, name = 'lobby'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('lobby/', views.lobby, name='lobby'),
    
    path('administrar-sistema/', views.administrar_sistema, name='administrar_sistema'),
    path('ventas/', views.ventas, name='ventas'),
]  