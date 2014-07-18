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

    return render_to_response('manager.html', context)

@require_POST
def upload(request):
    if not request.FILES:
                return HttpResponseBadRequest('Must upload a file')

    file = request.FILES[u'files[]']

    return JsonResponse({
                "name": file.name,
                "size": file.size,
                "type": file.content_type
                }
            )