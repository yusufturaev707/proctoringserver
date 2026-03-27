from django import forms
from apps.users.models import BarcodeUpload


class BarcodeUploadForm(forms.ModelForm):
    class Meta:
        model = BarcodeUpload
        fields = ['exam', 'exam_date', 'smena', 'image']

        widgets = {
            'exam': forms.Select(attrs={'class': 'form-control'}),
            'exam_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'smena': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

        labels = {
            'exam': 'Imtihon',
            'exam_date': 'Imtihon sanasi',
            'smena': 'Smena',
            'image': 'Barcode rasmi',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 20 * 1024 * 1024:
            raise forms.ValidationError("Rasm hajmi 20MB dan oshmasligi kerak.")
        return image
