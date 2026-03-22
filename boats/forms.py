from django import forms
from .models import Boat, BoatCategory


class BoatForm(forms.ModelForm):
    class Meta:
        model = Boat
        fields = ['name', 'category', 'boat_type', 'location', 'description', 'capacity', 'price_per_day', 'features', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'features': forms.TextInput(attrs={'placeholder': 'WiFi, Kitchen, AC, Life jackets...'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'price_per_day': forms.NumberInput(attrs={'min': 0}),
        }