from django import forms
from .models import UserProfile, ParkingLot
from django.contrib.auth.models import User
class ParkingLotRegistrationForm(forms.ModelForm):
    # Monitor Configuration Fields
    monitor_name = forms.CharField(max_length=255)
    monitor_latitude = forms.DecimalField(max_digits=9, decimal_places=6)
    monitor_longitude = forms.DecimalField(max_digits=9, decimal_places=6)
    resolution = forms.CharField(max_length=20)
    ip_address = forms.GenericIPAddressField()
    installation_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    maintenance_due = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = ParkingLot
        fields = [
            'name', 'address', 'parking_spaces', 'latitude', 'longitude',
            'base_price_per_hour', 'image', 'hours'
        ]
        widgets = {
            'operating_hours': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.CheckboxSelectMultiple
        }

class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = [
            'name', 'address', 'latitude', 'longitude', 'parking_spaces', 
             'base_price_per_hour', 'image'
        ]
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
            'base_price_per_hour': forms.NumberInput(attrs={'step': 'any'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'user_type', 'phone_number', 'vehicle_type', 'license_plate', 'stripe_account_id']

class ParkingLotOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'user_type', 'phone_number', 'company_name', 'stripe_account_id']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone_number', 'company_name']

class RegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=15)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class UserDetailsForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'John'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'john@example.com'})
    )

