from django.shortcuts import (render, get_object_or_404, HttpResponse,
                              reverse, redirect)
from django.conf import settings
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from lessons.models import Lesson
from purchases.models import Purchase
from django.contrib.auth.decorators import login_required
import json
import stripe


@login_required
def checkout(request, lesson_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    current_site = Site.objects.get_current()
    domain = current_site.domain
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    line_items = [{
            "name": lesson.topic,
            "amount": int(lesson.price * 100),
            "quantity": 1,
            "currency": "usd"
        }]
    session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                client_reference_id=request.user.id,
                mode='payment',
                line_items=line_items,
                success_url=domain + reverse('checkout_success_route'),
                cancel_url=domain + reverse('checkout_cancelled_route'),
                metadata={
                    "data": json.dumps({
                        'lesson_id': lesson.id
                    })
                }
            )
    return render(request, 'purchases/checkout.template.html', {
        'session_id': session.id,
        'public_key': stripe_publishable_key,
    })


@login_required
def checkout_success(request):
    return redirect(reverse("all_lesson_route"))


@login_required
def checkout_cancelled(request):
    return redirect(reverse("all_lesson_route"))


@login_required
@csrf_exempt
def payment_completed(request):
    payload = request.body
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # invalid payload
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_payment(session)

    return HttpResponse(status=200)


@login_required
def handle_payment(session):
    user = get_object_or_404(User, pk=session["client_reference_id"])
    metadata = json.loads(session['metadata']['data'])
    lesson = get_object_or_404(Lesson, pk=metadata['lesson_id'])
    purchase = Purchase()
    purchase.lesson_purchased = lesson
    purchase.student = user
    purchase.price = lesson.price
    purchase.save()
