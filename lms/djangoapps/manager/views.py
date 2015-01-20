from django.http import Http404, HttpResponse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django_future.csrf import ensure_csrf_cookie
from util.json_request import JsonResponse
from django.core.urlresolvers import reverse
from edxmako.shortcuts import render_to_response

from django.contrib.auth.models import User
from . import unicodecsv as csv
import shoppingcart


@login_required
@ensure_csrf_cookie
def index(request):
    user = request.user

    if not user.is_superuser:
    	raise Http404()

    # get all waiting orders
    all_waiting_orders = shoppingcart.models.Order.get_orders_with_items_for_status(status='waiting_approval')
   
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

@login_required
def dump_all_users(request):
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