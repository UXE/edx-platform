from django import forms
from django.forms import ModelForm
from .models import PaymentRquestUpload, PaymentOrderUpload

class PaymentRequestUploadForm(ModelForm):
	class Meta:
		model = PaymentRquestUpload
		fields = ['img', 'description']

class PaymentOrderUploadForm(ModelForm):
	class Meta:
		model = PaymentOrderUpload
		fields = ['img', 'description']
