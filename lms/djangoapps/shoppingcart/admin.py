"""
Allows django admin site to add PaidCourseRegistrationAnnotations
"""
from ratelimitbackend import admin
from shoppingcart.models import Order, PaidCourseRegistrationAnnotation, PaidCourseRegistration, PaymentAprrovalRequest

admin.site.register(Order)
admin.site.register(PaidCourseRegistrationAnnotation)
admin.site.register(PaidCourseRegistration)
admin.site.register(PaymentAprrovalRequest)
