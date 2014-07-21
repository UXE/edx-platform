from django import forms
from django.forms import ModelForm
from .models import PaymentRquestUpload

class PaymentRequestUploadForm(ModelForm):
	class Meta:
		model = PaymentRquestUpload
		fields = ['img', 'description']
