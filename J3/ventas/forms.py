from django import forms
from ventas.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock']  # Solo el campo stock