from django.db import models

from django.utils import timezone

class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)  # Código único para identificar el producto
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Código de barras opcional
    nombre = models.CharField(max_length=255, unique=True)  # Nombre único del producto
    cantidad = models.PositiveIntegerField(default=0)  # Cantidad en inventario
    precio_interno = models.DecimalField(max_digits=10, decimal_places=2)  # Precio interno
    precio_publico = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta al público

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    

class HistorialVenta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.fecha_venta}"
