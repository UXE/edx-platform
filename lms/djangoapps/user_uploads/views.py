from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django_future.csrf import ensure_csrf_cookie
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response

from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponseForbidden, Http404
)

from shoppingcart.models import PaidCourseRegistration, Order
from user_uploads.forms import PaymentRequestUploadForm, PaymentOrderUploadForm
from user_uploads.models import PaymentRquestUpload, PaymentOrderUpload

from manager import unicodecsv as csv

# @login_required
# @require_POST
# def upload_payment_verification(request):
# 	course_registration_id = request.POST.get('course_registration_id', None)
# 	if not course_registration_id:
# 		return HttpResponseBadRequest('No course_registration_id provided')

# 	try:
# 		course_registration = PaidCourseRegistration.objects.get(pk=course_registration_id)
# 	except PaidCourseRegistration.DoesNotExist:
# 		return HttpResponseBadRequest('No course registration found with this data')

# 	if course_registration.user != request.user:
# 		return HttpResponseBadRequest('You can only upload to the payment requests you own!')

# 	upload = PaymentRquestUpload(user=request.user, payment_request=course_registration)
# 	form = PaymentRequestUploadForm(request.POST, instance=upload)
# 	form.save()

# 	return redirect(reverse('dashboard'))

@login_required
@require_POST
def upload_payment_verification(request):@login_required
    """
    download all users data needed to migrate them
    """
    users = User.objects.all()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    field_names = ['username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'name', 'level_of_education', 'gender', 'mailing_address', 'city', 'country', 'goals', 'year_of_birth']
    writer = csv.DictWriter(response, fieldnames=field_names)
    # writer.writeheader()
    for user in users:
        writer.writerow({'username': user.username, 'email': user.email, 'password': user.password, 'is_active': user.is_active, 'is_staff': user.is_staff, 'is_superuser': user.is_superuser, 'name': user.profile.name, 'level_of_education': user.profile.level_of_education, 'gender': user.profile.gender, 'mailing_address': user.profile.mailing_address, 'city': user.profile.city, 'country':user.profile.country, 'goals': user.profile.goals, 'year_of_birth': user.profile.year_of_birth})

    return response

@login_required
@require_POST
def upload_order_verification(request):
	order_id = request.POST.get('order_id', None)
	if not order_id:
		return HttpResponseBadRequest('no order_id provided')

	try:
		order = Order.objects.get(pk=order_id)
	except Order.DoesNotExist:
		return HttpResponseBadRequest('No order found with this data')

	if order.user != request.user:
		return HttpResponseBadRequest('You can only upload to the order requests you own!')

	upload = PaymentOrderUpload(user=request.user, order=order)
	form = PaymentOrderUploadForm(request.POST, instance=upload)
	
	try:
		# check for returned error, as it raise exception when choosing some file types like svg
		form.save()
	except Exception, e:
		raise e

	return redirect(reverse('dashboard'))