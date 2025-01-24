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
    path('obtener_producto/', views.obtener_producto, name='obtener_producto'),
    path('administrar-usuarios/', views.administrar_usuarios, name='administrar_usuarios'),
    path('historial-ventas/', views.historial_ventas, name='historial_ventas'),
    path('administrar-inventario/', views.administrar_inventario, name='administrar_inventario'),
    path('historial_ventas/', views.historial_ventas, name='historial_ventas'),
    path('generar_pdf/', views.generar_pdf, name='generar_pdf'),
    path('generar_excel/', views.generar_excel, name='generar_excel'),
    path('cerrar-caja/', views.cerrar_caja, name='cerrar_caja'),  # Ruta para cerrar la caja
    #path('detalle_venta/<int:id>/', views.ver_detalle_venta, name='ver_detalle_venta'),
    path('eliminar_venta/<int:id>/', views.eliminar_venta, name='eliminar_venta'),
]  

