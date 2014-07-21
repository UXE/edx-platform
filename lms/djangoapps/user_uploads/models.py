from pyuploadcare.dj import ImageField

from django.db import models
from django.contrib.auth.models import User

from shoppingcart.models import PaidCourseRegistration

class PaymentRquestUpload(models.Model):
    """
    This is the model for storing uploads related to payment request.
    """
    user = models.ForeignKey(User, db_index=True)
    payment_request = models.ForeignKey(PaidCourseRegistration)
    title = models.CharField(blank=True, null=True, max_length=255)
    img = ImageField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
