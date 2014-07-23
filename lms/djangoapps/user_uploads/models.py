from pyuploadcare.dj import ImageField

from django.db import models
from django.contrib.auth.models import User

from shoppingcart.models import PaidCourseRegistration, Order

class PaymentRquestUpload(models.Model):
    """
    This is the model for storing uploads related to payment request 'PaidCourseRegistration'.
    """
    user = models.ForeignKey(User, db_index=True)
    payment_request = models.ForeignKey(PaidCourseRegistration, related_name='uploads')
    img = ImageField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True, db_index=True)

class PaymentOrderUpload(models.Model):
    """
    This is the model for storing uploads related to 'shoppingcart.Order' instance.
    """
    user = models.ForeignKey(User, db_index=True)
    order = models.ForeignKey(Order, related_name='uploads')
    img = ImageField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True, db_index=True)
