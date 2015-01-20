from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponseForbidden, Http404
)
from daress_theme import unicodecsv as csv
from django.contrib.auth.models import User
from django.conf import settings
from django_future.csrf import ensure_csrf_cookie
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response
from django.utils import translation
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from student.views import _do_create_account, AccountValidationError
from util.json_request import JsonResponse, expect_json


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

# @login_required
# def upload_all_users(request):
#     """
#     upload csv file with all users data, and insert into the system
#     """

#     if request.method == 'POST':
#         attachment = request.FILES.get('attachment', None)
#         if attachment:
#             field_names = ['username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'name', 'level_of_education', 'gender', 'mailing_address', 'city', 'country', 'goals', 'year_of_birth']
#             reader = csv.DictReader(attachment, fieldnames=field_names)
#             for row in reader:
#                 post_vars = {
#                 'username': row['username'], 
#                 'email': row['email'], 
#                 'password': row['password'], 
#                 'is_active': row['is_active'], 
#                 'is_staff': row['is_staff'], 
#                 'is_superuser': row['is_superuser'], 
#                 'name': row['name'], 
#                 'level_of_education': row['level_of_education'], 
#                 'gender': row['gender'], 
#                 'mailing_address': row['mailing_address'], 
#                 'city': row['city'], 
#                 'country':row['country'], 
#                 'goals': row['goals'], 
#                 'year_of_birth': row['year_of_birth']
#                 }

#                 print post_vars
#                 # django.utils.translation.get_language() will be used to set the new
#                 # user's preferred language.  This line ensures that the result will
#                 # match this installation's default locale.  Otherwise, inside a
#                 # management command, it will always return "en-us".
#                 translation.activate(settings.LANGUAGE_CODE)
#                 try:
#                     user, profile, reg = _do_create_account(post_vars)
#                     if post_vars['is_active'] == 'True':
#                         user.is_staff = True
#                     if post_vars['is_staff'] == 'True':
#                         user.is_staff = True
#                     if post_vars['is_superuser'] == 'True':
#                         user.is_staff = True

#                     user.save()
#                     reg.activate()
#                     reg.save()
#                     create_comments_service_user(user)
#                 except AccountValidationError as e:
#                     print e.message
#                     user = User.objects.get(email=row['email'])
#                 translation.deactivate()

#             return redirect('dashboard')
        
#         return JsonResponse({'msg':'No files attached'}, status=400)
    
#     return JsonResponse({'msg':'Bad Request'}, status=400)
