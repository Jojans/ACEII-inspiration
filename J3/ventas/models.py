from django.db import models
from django.utils import timezone

class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=255)
    image = models.URLField()
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    stock = models.IntegerField(default=0)  # Campo para almacenar el stock del producto

    def __str__(self):
        return self.title
    
class Proveedor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    picture = models.URLField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra de {self.cantidad} {self.producto.title} de {self.proveedor.first_name} {self.proveedor.last_name}"

class Venta(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Venta de {self.producto.title} - {self.cantidad} unidades'