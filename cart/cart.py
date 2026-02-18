from decimal import Decimal
from django.conf import settings
from services.models import Service

class Cart:
    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # сохранить пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, service, quantity=1, override_quantity=False):
        """
        Добавить услугу в корзину или обновить ее количество.
        """
        service_id = str(service.id)
        if service_id not in self.cart:
            self.cart[service_id] = {'quantity': 0,
                                     'price': str(service.price_fixed or 0)}
        if override_quantity:
            self.cart[service_id]['quantity'] = quantity
        else:
            self.cart[service_id]['quantity'] += quantity
        self.save()

    def save(self):
        # пометить сессию как "измененную", чтобы обеспечить ее сохранение
        self.session.modified = True

    def remove(self, service):
        """
        Удаление услуги из корзины.
        """
        service_id = str(service.id)
        if service_id in self.cart:
            del self.cart[service_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение услуг из базы данных.
        """
        service_ids = self.cart.keys()
        # получение объектов услуг и добавление их в корзину
        services = Service.objects.filter(id__in=service_ids)
        cart = self.cart.copy()
        for service in services:
            cart[str(service.id)]['service'] = service

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.save()
