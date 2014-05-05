from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns('shoppingcart.views',  # nopep8
    url(r'^postpay_callback/$', 'postpay_callback'),  # Both the ~accept and ~reject callback pages are handled here
    url(r'^receipt/(?P<ordernum>[0-9]*)/$', 'show_receipt'),
    url(r'^csv_report/$', 'csv_report', name='payment_csv_report'),
)

if settings.FEATURES['ENABLE_SHOPPING_CART']:
    urlpatterns += patterns(
        'shoppingcart.views',
        url(r'^$', 'show_cart', name='show_cart'),
        url(r'^clear/$', 'clear_cart'),
        url(r'^remove_item/$', 'remove_item'),
        url(r'^add/course/(?P<course_id>[^/]+/[^/]+/[^/]+)/$', 'add_course_to_cart', name='add_course_to_cart'),
        url(r'^bank_payments/new_payment_request/$', 'new_payment_request', name='new_payment_request'),
        url(r'^bank_payments/list/$', 'user_payment_requests', name='user_payment_requests'),
        url(r'^bank_payments/all/$', 'all_payment_requests', name='all_payment_requests'),
        url(r'^bank_payments/approve/$', 'approve_payment_request', name='approve_payment_request'),
        url(r'^bank_payments/update/$', 'update_payment_request', name='update_payment_request'),
    )

if settings.FEATURES.get('ENABLE_PAYMENT_FAKE'):
    from shoppingcart.tests.payment_fake import PaymentFakeView
    urlpatterns += patterns(
        'shoppingcart.tests.payment_fake',
        url(r'^payment_fake', PaymentFakeView.as_view()),
    )
