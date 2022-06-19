from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegisterForm, SaveProfileAvatarForm
from django.http import JsonResponse
from storage_manager.models import (
    Box, BoxPlace, CalculateCustomer, Order, BoxVolume)
from django.contrib.auth.models import User
from django.db.models import Min
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.files.base import ContentFile
from datetime import date
from django.db.models import Q
import phonenumbers
from PIL import Image
from io import BytesIO

from .utils import randomise_from_range, get_email, get_boxes_sizes


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse(form.errors)
    return JsonResponse({})


def sign_in(request):
    if request.method == "POST":
        context = {}
        email = request.POST['email']
        password = request.POST['password']

        account = authenticate(request, username=email, password=password)
        if account is None:
            context['message'] = 'Неверный логин или пароль'
            context['success'] = False
            return JsonResponse(context)

        elif account:
            login(request, account)
            context['message'] = 'Вы вошли в аккаунт!'
            context['success'] = True
            return JsonResponse(context)

        else:
            context['message'] = 'Неверный логин или пароль'
            context['success'] = False
            return JsonResponse(context)

    return JsonResponse({})


def index(request):
    if request.GET.get('EMAIL1'):
        get_email(request)
        return redirect('index')

    all_box_spaces = list(BoxPlace.objects.all().prefetch_related(
        'place_boxes').get_free_boxes().get_min_price())
    space_count = len(all_box_spaces)
    random_box_space_index = randomise_from_range(space_count)
    random_box_space = all_box_spaces[random_box_space_index]
    free_space = random_box_space.boxes_quantity - random_box_space.free_boxes

    min_box_price = Box.objects.all().aggregate(Min('tariff'))['tariff__min']
    context = {
        'min_box_price': min_box_price,
        'box_space': random_box_space,
        'free_space': free_space,
        'min_price': random_box_space.min_price,
    }
    return render(request, 'index.html', context)


@login_required
def personal_account(request):
    user_orders = Order.objects.filter(customer=request.user).select_related('box__boxes_place')
    for order in user_orders:
        order.expires_soon = 0 <= (order.end_date - date.today()).days < 14
        order.expired = order.end_date < date.today()
    if request.method == 'POST':
        print(request.POST)

    context = {
        'orders': user_orders
    }
    return render(request, 'personal_account.html', context)


@login_required
def change_user_profile(request):
    if request.method == 'POST':
        user = request.user
        context = {}
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        if request.FILES:
            try:
                img = Image.open(request.FILES['avatar'])
                img.thumbnail((180, 180))
                temp = BytesIO()
                img.save(temp, format=img.format)
            except Exception as exc:
                print(exc)
                context['message'] = 'С изображением что-то не так, попробуйте снова'
                context['success'] = False
                return JsonResponse(context)
            user.profile.avatar = ContentFile(temp.getvalue(), f'{user.username}_avatar.{img.format}')
        if email and email != user.email and email != user.username:
            if User.objects.filter(Q(email=email)|Q(username=email)).exists():
                context['message'] = 'E-mail адрес уже используется'
                context['success'] = False
                return JsonResponse(context)
            user.email = email
            user.username = email
        if phone_number:
            try:
                parsed_phone_number = phonenumbers.parse(
                    phone_number,
                    'RU'
                )
                if not phonenumbers.is_valid_number(parsed_phone_number):
                    context['message'] = 'Некорректный номер телефона'
                normalized_phone_number = phonenumbers.format_number(
                    parsed_phone_number,
                    phonenumbers.PhoneNumberFormat.E164
                )
                user.profile.phone_number = normalized_phone_number
            except phonenumbers.NumberParseException:
                context['message'] = 'Некорректный номер телефона'
            if context.get('message'):
                context['success'] = False
                return JsonResponse(context)
        if first_name:
            user.profile.first_name = first_name
        if last_name:
            user.profile.last_name = last_name
        if password:
            if len(password) < 8:
                context['message'] = 'Слишком короткий пароль'
                context['success'] = False
                return JsonResponse(context)
            user.set_password(password)
        user.save()
        update_session_auth_hash(request, user)
        context['success'] = True
        return JsonResponse(context)
    return JsonResponse({})


def boxes(request):
    if request.GET.get('EMAIL1'):
        get_email(request)
        return redirect('boxes')

    all_values = BoxVolume.objects.all()
    all_places = BoxPlace.objects.all().prefetch_related(
        'place_boxes').get_free_boxes().get_min_price()

    all_box_sizes = get_boxes_sizes(all_values)
    less_3_box_sizes = get_boxes_sizes(all_values, 0, 3)
    less_10_box_sizes = get_boxes_sizes(all_values, 0, 10)
    more_10_box_sizes = get_boxes_sizes(all_values, 10)

    context = {
        'all_places': all_places,
        'all_box_sizes': all_box_sizes,
        'less_3_box_sizes': less_3_box_sizes,
        'less_10_box_sizes': less_10_box_sizes,
        'more_10_box_sizes': more_10_box_sizes,
    }
    return render(request, 'boxes.html', context)
