import logging
import datetime
import pytz
from django.conf import settings
from django.contrib.auth.models import Group
from django.http import (HttpResponse, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponseForbidden, Http404)
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django_future.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from edxmako.shortcuts import render_to_response
from shoppingcart.reports import RefundReport, ItemizedPurchaseReport, UniversityRevenueShareReport, CertificateStatusReport
from student.models import CourseEnrollment
from .exceptions import ItemAlreadyInCartException, AlreadyEnrolledInCourseException, CourseDoesNotExistException, ReportTypeDoesNotExistException
from .models import Order, PaidCourseRegistration, OrderItem, PaymentAprrovalRequest
from .processors import process_postpay_callback, render_purchase_form_html

log = logging.getLogger("shoppingcart")

EVENT_NAME_USER_UPGRADED = 'edx.course.enrollment.upgrade.succeeded'

REPORT_TYPES = [
    ("refund_report", RefundReport),
    ("itemized_purchase_report", ItemizedPurchaseReport),
    ("university_revenue_share", UniversityRevenueShareReport),
    ("certificate_status", CertificateStatusReport),
]


def initialize_report(report_type, start_date, end_date, start_letter=None, end_letter=None):
    """
    Creates the appropriate type of Report object based on the string report_type.
    """
    for item in REPORT_TYPES:
        if report_type in item:
            return item[1](start_date, end_date, start_letter, end_letter)
    raise ReportTypeDoesNotExistException

@require_POST
def add_course_to_cart(request, course_id):
    """
    Adds course specified by course_id to the cart.  The model function add_to_order does all the
    heavy lifting (logging, error checking, etc)
    """
    if not request.user.is_authenticated():
        log.info("Anon user trying to add course {} to cart".format(course_id))
        return HttpResponseForbidden(_('You must be logged-in to add to a shopping cart'))
    cart = Order.get_cart_for_user(request.user)
    # All logging from here handled by the model
    try:
        PaidCourseRegistration.add_to_order(cart, course_id)
    except CourseDoesNotExistException:
        return HttpResponseNotFound(_('The course you requested does not exist.'))
    except ItemAlreadyInCartException:
        return HttpResponseBadRequest(_('The course {0} is already in your cart.'.format(course_id)))
    except AlreadyEnrolledInCourseException:
        return HttpResponseBadRequest(_('You are already registered in course {0}.'.format(course_id)))
    return HttpResponse(_("Course added to cart."))


@login_required
def show_cart(request):
    cart = Order.get_cart_for_user(request.user)
    total_cost = cart.total_cost
    cart_items = cart.orderitem_set.all()
    form_html = render_purchase_form_html(cart)
    return render_to_response("shoppingcart/list.html",
                              {'shoppingcart_items': cart_items,
                               'amount': total_cost,
                               'form_html': form_html,
                               })


@login_required
def clear_cart(request):
    cart = Order.get_cart_for_user(request.user)
    cart.clear()
    return HttpResponse('Cleared')


@login_required
def remove_item(request):
    item_id = request.REQUEST.get('id', '-1')
    try:
        item = OrderItem.objects.get(id=item_id, status='cart')
        if item.user == request.user:
            item.delete()
    except OrderItem.DoesNotExist:
        log.exception('Cannot remove cart OrderItem id={0}. DoesNotExist or item is already purchased'.format(item_id))
    return HttpResponse('OK')


# @csrf_exempt
@require_POST
@login_required
@ensure_csrf_cookie
def postpay_callback(request):
    """
    Receives the POST-back from processor.
    Mainly this calls the processor-specific code to check if the payment was accepted, and to record the order
    if it was, and to generate an error page.
    If successful this function should have the side effect of changing the "cart" into a full "order" in the DB.
    The cart can then render a success page which links to receipt pages.
    If unsuccessful the order will be left untouched and HTML messages giving more detailed error info will be
    returned.
    """
    params = request.POST.dict()
    result = process_postpay_callback(params)
    if result['success']:
        return HttpResponseRedirect(reverse('shoppingcart.views.show_receipt', args=[result['order'].id]))
    else:
        return render_to_response('shoppingcart/error.html', {'order': result['order'],
                                                              'error_html': result['error_html']})

@login_required
def show_receipt(request, ordernum):
    """
    Displays a receipt for a particular order.
    404 if order is not yet purchased or request.user != order.user
    """
    try:
        order = Order.objects.get(id=ordernum)
    except Order.DoesNotExist:
        raise Http404('Order not found!')

    if order.user != request.user or order.status != 'purchased':
        raise Http404('Order not found!')

    order_items = OrderItem.objects.filter(order=order).select_subclasses()
    any_refunds = any(i.status == "refunded" for i in order_items)
    receipt_template = 'shoppingcart/receipt.html'
    __, instructions = order.generate_receipt_instructions()
    # we want to have the ability to override the default receipt page when
    # there is only one item in the order
    context = {
        'order': order,
        'order_items': order_items,
        'any_refunds': any_refunds,
        'instructions': instructions,
    }

    if order_items.count() == 1:
        receipt_template = order_items[0].single_item_receipt_template
        context.update(order_items[0].single_item_receipt_context)

    # Only orders where order_items.count() == 1 might be attempting to upgrade
    attempting_upgrade = request.session.get('attempting_upgrade', False)
    if attempting_upgrade:
        course_enrollment = CourseEnrollment.get_or_create_enrollment(request.user, order_items[0].course_id)
        course_enrollment.emit_event(EVENT_NAME_USER_UPGRADED)
        request.session['attempting_upgrade'] = False

    return render_to_response(receipt_template, context)


def _can_download_report(user):
    """
    Tests if the user can download the payments report, based on membership in a group whose name is determined
     in settings.  If the group does not exist, denies all access
    """
    try:
        access_group = Group.objects.get(name=settings.PAYMENT_REPORT_GENERATOR_GROUP)
    except Group.DoesNotExist:
        return False
    return access_group in user.groups.all()


def _get_date_from_str(date_input):
    """
    Gets date from the date input string.  Lets the ValueError raised by invalid strings be processed by the caller
    """
    return datetime.datetime.strptime(date_input.strip(), "%Y-%m-%d").replace(tzinfo=pytz.UTC)


def _render_report_form(start_str, end_str, start_letter, end_letter, report_type, total_count_error=False, date_fmt_error=False):
    """
    Helper function that renders the purchase form.  Reduces repetition
    """
    context = {
        'total_count_error': total_count_error,
        'date_fmt_error': date_fmt_error,
        'start_date': start_str,
        'end_date': end_str,
        'start_letter': start_letter,
        'end_letter': end_letter,
        'requested_report': report_type,
    }
    return render_to_response('shoppingcart/download_report.html', context)


@login_required
def csv_report(request):
    """
    Downloads csv reporting of orderitems
    """
    if not _can_download_report(request.user):
        return HttpResponseForbidden(_('You do not have permission to view this page.'))

    if request.method == 'POST':
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        start_letter = request.POST.get('start_letter', '')
        end_letter = request.POST.get('end_letter', '')
        report_type = request.POST.get('requested_report', '')
        try:
            start_date = _get_date_from_str(start_date) + datetime.timedelta(days=0)
            end_date = _get_date_from_str(end_date) + datetime.timedelta(days=1)
        except ValueError:
            # Error case: there was a badly formatted user-input date string
            return _render_report_form(start_date, end_date, start_letter, end_letter, report_type, date_fmt_error=True)

        report = initialize_report(report_type, start_date, end_date, start_letter, end_letter)
        items = report.rows()

        response = HttpResponse(mimetype='text/csv')
        filename = "purchases_report_{}.csv".format(datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d-%H-%M-%S"))
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        report.write_csv(response)
        return response

    elif request.method == 'GET':
        end_date = datetime.datetime.now(pytz.UTC)
        start_date = end_date - datetime.timedelta(days=30)
        start_letter = ""
        end_letter = ""
        return _render_report_form(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), start_letter, end_letter, report_type="")

    else:
        return HttpResponseBadRequest("HTTP Method Not Supported")


# bank payments views

@require_POST
@login_required
@ensure_csrf_cookie
def new_payment_request(request):
    """
    create new bank payments request
    """
    user = request.user
    if not user.is_authenticated():
        log.warning('you are not allowed to do  so!')
        return HttpResponseForbidden('you are not allowed to do  so!')

    cart = Order.get_cart_for_user(request.user)
    # by the way this will allawys be false, but will leave it to figure out what to do
    if not user == cart.user:
        log.warning('Trying to manipulate other users cart!')
        return HttpResponseForbidden('Trying to manipulate other users cart!')

    ## use cart.orderitem_set.all().select_subclasses('paidcourseregistration') to return the approperiate type
    cart_items = cart.orderitem_set.all().select_subclasses("paidcourseregistration") 
    if len(cart_items) == 0:
        log.warning('Trying to submit empty cart!')
        return HttpResponseForbidden('Trying to submit empty cart!')

    request_details = request.POST.get('payment_request_details', '')

    payment_request = PaymentAprrovalRequest(cart=cart, user=user, request_details=request_details, message='Waiting approval')
    payment_request.save()

    for item in cart_items:
        payment_request.paid_course_registrations.add(item)

    payment_request.save()


    log.warning(""" 
      _        __      
     (_)      / _|     
      _ _ __ | |_ ___  
     | | '_ \|  _/ _ \ 
     | | | | | || (_) |
     |_|_| |_|_| \___/ 
                   
    {0}
    """.format(payment_request.paid_course_registrations.all()))

    return HttpResponseRedirect('http://127.0.0.1:8000/shoppingcart/bank_payments/list/')
    # return HttpResponseRedirect(reverse('user_payment_requests')
    # return HttpResponse(_("Payment request added to cart."))
    # HttpResponseRedirect(reverse('shoppingcart.views.show_cart')

@login_required
def user_payment_requests(request):
    """
    user will be redirected to this page, and review all his past requset even the approved ones
    """

    try:
        payment_requests = PaymentAprrovalRequest.objects.filter(user=request.user)
        return render_to_response('shoppingcart/payment_requests.html', 
                                    {'payment_requests': payment_requests})
    except PaymentAprrovalRequest.DoesNotExist:
        raise
    
@login_required
def all_payment_requests(request):
    """
    list all Payment approval requests in the system
    """

    if not request.user.is_superuser:
        log.warning("normal user is trying to access payment requests page")
        return HttpResponseForbidden(_('You must be admin to do this task'))
    # we should check to restrict this view to specific users such as admins or a member of i.e. 'payments group'
    try:
        payment_requests = PaymentAprrovalRequest.objects.all()
        return render_to_response('shoppingcart/all_payment_requests.html', 
                                    {'payment_requests': payment_requests})
    except PaymentAprrovalRequest.DoesNotExist:
        raise

def course_payment_requests(request):
    """
    list of Payment requests in a specific course
    """
    pass

@require_POST
@login_required
@ensure_csrf_cookie
def approve_payment_request(request):
    """
    approve Payment request and call the logic of purchase items and send emails and so on
    """

    # we should check to restrict this view to specific users such as admins or a member of i.e. 'payments group'
    
    payment_request_id = int(request.POST.get('payment_request_id', ''))
    try:
        payment_request = PaymentAprrovalRequest.objects.get(pk=payment_request_id)
        if not request.user.is_superuser:
            log.warning("normal user is trying to approve {} to cart".format(payment_request))
            return HttpResponseForbidden(_('You must be admin to do this task'))
        cart = payment_request.cart
        items_in_cart = cart.orderitem_set.all().select_subclasses()
        items_in_request = payment_request.paid_course_registrations.all()

        if len(items_in_cart) > len(items_in_request): # if user added courses after sending payment request, we must approve those in request and remove them from cart
            pass # will implement it later
        else: # this is the case where items in items_in_cart <= items_in_request so user may removed a course from his cart
            # simply we will call the purchase method of the cart
            processor_reply_dump=u'this courses were manully approved by "{0}" using payment request mechanism'.format(request.user)
            cart.purchase(processor_reply_dump=processor_reply_dump)
            payment_request.is_approved = True
            payment_request.approved_by = request.user
            payment_request.save()

        log.warning(""" 
      _        __      
     (_)      / _|     
      _ _ __ | |_ ___  
     | | '_ \|  _/ _ \ 
     | | | | | || (_) |
     |_|_| |_|_| \___/ 
                   
    payment_request:{0}, cart:{1}, payment_request.items:{2}
    """.format(payment_request, cart, payment_request.paid_course_registrations.all()))

        return HttpResponseRedirect('http://127.0.0.1:8000/shoppingcart/bank_payments/all/')
        # return HttpResponse(_("Payment approved."))
    except PaymentAprrovalRequest.DoesNotExist:
        log.warning('Trying to approve payment_request that DoesNotExist!')
        raise

@require_POST
@login_required
@ensure_csrf_cookie
def update_payment_request(request):
    """
    can be used to change the status message and send the user an email of changes
    """
    payment_request_id = int(request.POST.get('payment_request_id', ''))
    
    try:
        payment_request = PaymentAprrovalRequest.objects.get(pk=payment_request_id)
        if not request.user.is_superuser:
            log.warning("normal user is trying to approve {} to cart".format(payment_request))
            return HttpResponseForbidden(_('You must be admin to do this task'))

        message = request.POST.get('payment_request_status', '')
        payment_request.message = message
        payment_request.save()
        return HttpResponseRedirect('http://127.0.0.1:8000/shoppingcart/bank_payments/all/')
    except PaymentAprrovalRequest.DoesNotExist:
        log.warning('Trying to update payment_request that DoesNotExist!')
        raise