from .models import Product

def low_stock_alert(request):
    # IDs de los productos específicos para mostrar alerta
    productos_ids_bajos = [9, 10, 11, 12, 13, 14]

    # Filtramos los productos electrónicos con stock bajo y que tienen una ID en la lista especificada
    productos_bajo_stock = Product.objects.filter(
        id__in=productos_ids_bajos,
        stock__lt=5,
        category="electronics"
    )

    return {'productos_bajo_stock': productos_bajo_stock}