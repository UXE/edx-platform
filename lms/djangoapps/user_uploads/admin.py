from ratelimitbackend import admin
from user_uploads.models import PaymentRquestUpload, PaymentOrderUpload

admin.site.register(PaymentRquestUpload)
admin.site.register(PaymentOrderUpload)