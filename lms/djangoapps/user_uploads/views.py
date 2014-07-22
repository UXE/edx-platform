from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django_future.csrf import ensure_csrf_cookie
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response

from shoppingcart.models import PaidCourseRegistration
from user_uploads.forms import PaymentRequestUploadForm
from user_uploads.models import PaymentRquestUpload

@login_required
@require_POST
def upload_payment_verification(request):
	course_registration_id = request.POST.get('course_registration_id', None)
	if not course_registration_id:
		return HttpResponseBadRequest('no course_registration_id provided')

	course_registration = PaidCourseRegistration.objects.get(pk=course_registration_id)
	if course_registration.user != request.user:
		return HttpResponseBadRequest('You can only upload to the payment requests you own!')

	upload = PaymentRquestUpload(user=request.user, payment_request=course_registration, title='Upladed image by user')
	form = PaymentRequestUploadForm(request.POST, instance=upload)
	form.save()

	return redirect(reverse('dashboard'))