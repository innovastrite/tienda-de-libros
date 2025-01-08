from django.urls import path
from . import views

urlpatterns = [
    # Rutas de usuarios
    path('registro/', views.registro_usuario, name='registro'),
    path('autor/crear/', views.crear_autor, name='crear_autor'),
    path('autor/panel/', views.panel_autor, name='panel_autor'),

    # Rutas para libros
    path('', views.lista_libros, name='lista_libros'),
    path('libro/<int:id>/', views.detalle_libro, name='detalle_libro'),
    path('libro/<int:id>/venta/', views.registrar_venta, name='registrar_venta'),
    path('libro/<int:libro_id>/historial/', views.historial_ventas, name='historial_ventas'),
    path('libro/<int:libro_id>/borrar-historial/', views.borrar_historial, name='borrar_historial'),

    # Rutas para descargas
    path('libro/<int:libro_id>/solicitar-descarga/', views.solicitar_descarga, name='solicitar_descarga'),
    path('descargas/confirmar/<int:descarga_id>/', views.confirmar_descarga, name='confirmar_descarga'),
    path('descargar/<uuid:token>/', views.descargar_libro, name='descargar_libro'),

    # Rutas para compras
    path('libro/<int:libro_id>/comprar/', views.solicitar_compra, name='solicitar_compra'),
    path('compra/<int:venta_id>/', views.estado_compra, name='estado_compra'),

    # Rutas de administración
    path('admin/notificaciones/', views.admin_notificaciones, name='admin_notificaciones'),
    path('admin/ventas/', views.admin_ventas, name='admin_ventas'),
    path('admin/venta/<int:venta_id>/confirmar/', views.confirmar_venta, name='confirmar_venta'),
]
