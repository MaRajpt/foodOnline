
from django import forms 
from .models import Vendor
from accounts.validators import allow_only_images_validator

class VendorForm(forms.ModelForm):
    # we used FileField not ImageField bcoz our custom validator wont work with imagefield
    vendor_license= forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
