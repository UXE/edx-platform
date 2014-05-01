"""
Allows django admin site to add PaidCourseRegistrationAnnotations
"""
from ratelimitbackend import admin
from shoppingcart.models import PaidCourseRegistrationAnnotation, PaymentAprrovalRequest

admin.site.register(PaidCourseRegistrationAnnotation)
admin.site.register(PaymentAprrovalRequest)
