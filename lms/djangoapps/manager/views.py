from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django_future.csrf import ensure_csrf_cookie
from util.json_request import JsonResponse
from django.core.urlresolvers import reverse
from edxmako.shortcuts import render_to_response


import shoppingcart


@login_required
@ensure_csrf_cookie
def index(request):
    user = request.user

    if not user.is_staff:
    	raise Http404()

    # get all waiting orders
    all_waiting_orders = shoppingcart.models.Order.get_orders_with_items_for_status(status='waiting_approval')
    print all_waiting_orders
   
    context = {
        'all_waiting_orders': all_waiting_orders,
        'user': user,
        'logout_url': reverse('logout'),
        'platform_name': settings.PLATFORM_NAME,
    }

    from user_uploads import forms

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.PaymentRequestUploadForm(request.POST)
    else:
        form = forms.PaymentRequestUploadForm()
        context['form'] = form

    return render_to_response('manager.html', context)