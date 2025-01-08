from django import forms
from .models import Libro

# Formulario para agregar o editar un libro
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'titulo', 
            'autor', 
            'precio', 
            'pdf', 
            'resumen', 
            'categoria', 
            'clasificacion_edad'
        ]
        widgets = {
            'resumen': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'precio': forms.NumberInput(attrs={'step': 0.01}),
        }
