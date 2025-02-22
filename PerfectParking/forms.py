from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'preferred_payment_method']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        } 