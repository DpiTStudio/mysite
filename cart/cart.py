from decimal import Decimal
from django.conf import settings
from services.models import Service
from portfolio.models import Portfolio

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

    def add(self, item, item_type='service', quantity=1, override_quantity=False):
        """
        Добавить товар/услугу в корзину или обновить ее количество.
        """
        item_id = str(item.id)
        cart_key = f"{item_type}_{item_id}"
        
        if cart_key not in self.cart:
            if item_type == 'service':
                price = str(item.price_fixed or 0)
            else:
                price = str(item.price or 0)
                
            self.cart[cart_key] = {
                'item_type': item_type,
                'item_id': item_id,
                'quantity': 0,
                'price': price
            }
            
        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        self.save()

    def save(self):
        # пометить сессию как "измененную", чтобы обеспечить ее сохранение
        self.session.modified = True

    def remove(self, item_type, item_id):
        """
        Удаление услуги из корзины.
        """
        cart_key = f"{item_type}_{item_id}"
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение услуг из базы данных.
        """
        # Сбор ID для каждого типа
        service_ids = [int(v['item_id']) for k, v in self.cart.items() if v.get('item_type') == 'service']
        portfolio_ids = [int(v['item_id']) for k, v in self.cart.items() if v.get('item_type') == 'portfolio']
        
        # Получение объектов из БД
        services = Service.objects.filter(id__in=service_ids)
        portfolios = Portfolio.objects.filter(id__in=portfolio_ids)
        
        # Создание словарей для быстрого доступа
        service_dict = {s.id: s for s in services}
        portfolio_dict = {p.id: p for p in portfolios}

        import copy
        cart = copy.deepcopy(self.cart)
        
        # Заполнение данными объекта из БД
        for key, item in cart.items():
            item_type = item.get('item_type', 'service')
            item_id = int(item['item_id'])
            
            if item_type == 'service':
                item['item_obj'] = service_dict.get(item_id)
            elif item_type == 'portfolio':
                item['item_obj'] = portfolio_dict.get(item_id)
                
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            
            # Пропускаем, если объект был удален из БД
            if item.get('item_obj'):
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
