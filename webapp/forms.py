from django import forms

from webapp.models import UploadedImage


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
