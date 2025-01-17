import json
import os
import random
import qrcode
from datetime import datetime
from pathlib import Path
import uuid

from django.conf import settings
from yookassa import Configuration, Payment
import self_storage_site.settings
from storage_manager.models import (
    BoxPlace,
    BoxVolume,
    Box,
    RentalTime,
    CalculateCustomer
)


def read_from_json(filepath):
            with open(filepath, encoding='UTF-8', mode='r') as f:
                return json.loads(f.read())


def fill_database(filepath):
    storages = read_from_json(filepath)
    for item in storages:
        if item['type'] == 'box_volumes':
            for volume in item['box_volumes']:
                BoxVolume.objects.get_or_create(volume=volume)
        if item['type'] == 'rental_time':
            for time in item['rental_time']:
                RentalTime.objects.get_or_create(time_intervals=time)
        if item['type'] == 'box_places':
            for storage in item['box_places']:
                box_place = BoxPlace.objects.get_or_create(
                    name=storage['name'],
                    address=storage['address'],
                    boxes_quantity=storage['boxes_quantity'],
                    note=storage['note'],
                )
                box_sizes = storage['box_sizes']
                for box_size in box_sizes:
                    count_and_price = box_sizes[box_size]
                    for box in range(count_and_price[0]):
                        box_volume = BoxVolume.objects.get(volume=int(box_size))
                        Box.objects.create(
                            box_volume=box_volume,
                            boxes_place=box_place[0],
                            tariff=count_and_price[1]
                        )


def create_qrcode(code):
    qrcode_image = qrcode.make(code)
    qrcodes_path = os.path.join(
        self_storage_site.settings.BASE_DIR / 'qrcodes'
    )
    filename = f'qr{int(datetime.now().timestamp())}'
    suffix = '.jpg'
    Path(qrcodes_path).mkdir(exist_ok=True)
    image_path = str(Path(qrcodes_path, filename).with_suffix(suffix))
    qrcode_image.save(image_path)
    return image_path


def randomise_from_range(stop):
    return random.randrange(stop)


def get_email(request):
    customer_mail = request.GET.get('EMAIL1')
    CalculateCustomer.objects.get_or_create(
        customer_mail=customer_mail)


def get_boxes_sizes(all_values, min=0, max=9999999999):
    all_boxes_sizes = []
    min_rice_box = 9999999
    for value in all_values:
        if min > value.volume or max <= value.volume:
            continue
        box_details = {}
        value_boxes = value.boxes.all()
        for value_box in value_boxes:
            if value_box. in_use:
                continue
            if value_box.tariff < min_rice_box:
                min_rice_box = value_box.tariff
                box_details['id'] = value_box.pk
                box_details['value'] = value.volume
                box_details['price'] = value_box.tariff
            min_rice_box = 9999999
        if box_details:
            all_boxes_sizes.append(box_details)
    if all_boxes_sizes is None:
        return None
    return all_boxes_sizes


def create_payment(amount, return_url):
    Configuration.account_id = settings.SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_API_KEY

    payment = Payment.create({
        'amount': {
            'value': amount,
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': return_url
        },
        'capture': True,
        'description': 'Аренда бокса'
    }, uuid.uuid4())

    payment = json.loads(payment.json())

    return {
        'id': payment['id'],
        'url': payment['confirmation']['confirmation_url'],
        'status': payment['paid'],
    }


def check_payment(payment_id):
    Configuration.account_id = settings.SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_API_KEY

    payment = Payment.find_one(payment_id)
    payment = json.loads(payment.json())
    return payment['paid']
