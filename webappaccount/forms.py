from django import forms
from mobileappaccount.models import UploadedImage


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
