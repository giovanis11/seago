from django import forms
from .models import Boat, BoatCategory


class BoatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["luxury_subcategory"].required = False
        self.fields["luxury_subcategory"].help_text = (
            "Only use this if the boat belongs to the Luxury category."
        )

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        luxury_subcategory = cleaned_data.get("luxury_subcategory")

        if category and category.name.lower() == "luxury" and not luxury_subcategory:
            self.add_error(
                "luxury_subcategory",
                "Please choose a luxury sub-category for Luxury boats.",
            )

        if category and category.name.lower() != "luxury":
            cleaned_data["luxury_subcategory"] = ""

        return cleaned_data

    class Meta:
        model = Boat
        fields = ['name', 'category', 'luxury_subcategory', 'boat_type', 'location', 'description', 'capacity', 'price_per_day', 'features', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'features': forms.TextInput(attrs={'placeholder': 'WiFi, Kitchen, AC, Life jackets...'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'price_per_day': forms.NumberInput(attrs={'min': 0}),
        }
