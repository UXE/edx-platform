"""
Allows django admin site to add PaidCourseRegistrationAnnotations
"""
from ratelimitbackend import admin
from shoppingcart.models import PaidCourseRegistrationAnnotation, PaidCourseRegistration, Order, OrderItem

admin.site.register(Order)
# admin.site.register(OrderItem)
admin.site.register(PaidCourseRegistration)
admin.site.register(PaidCourseRegistrationAnnotation)
