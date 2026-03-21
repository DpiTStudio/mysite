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
            self.cart[cart_key] = {
                'item_type': item_type,
                'item_id': item_id,
                'quantity': 0,
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
        Рассчитывает цены "на лету", чтобы предотвратить рассинхрон с БД.
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
        for cart_key, item in list(cart.items()):
            item_type = item.get('item_type', 'service')
            item_id = int(item['item_id'])
            
            if item_type == 'service':
                obj = service_dict.get(item_id)
            elif item_type == 'portfolio':
                obj = portfolio_dict.get(item_id)
            else:
                obj = None
                
            # Пропускаем, если объект был удален из БД (и заодно очищаем из сессии)
            if not obj:
                if cart_key in self.cart:
                    del self.cart[cart_key]
                    self.save()
                continue
                
            item['item_obj'] = obj
            
            # Извлекаем актуальную цену из базы
            item['price_type'] = getattr(obj, 'price_type', 'fixed')
            
            try:
                price_val = getattr(obj, 'price_fixed', getattr(obj, 'price', 0))
                item['price'] = Decimal(str(price_val or 0))
            except Exception:
                item['price'] = Decimal('0')
                
            try:
                price_min = getattr(obj, 'price_min', 0)
                item['price_min'] = Decimal(str(price_min or 0))
            except Exception:
                item['price_min'] = Decimal('0')
                
            try:
                price_max = getattr(obj, 'price_max', 0)
                item['price_max'] = Decimal(str(price_max or 0))
            except Exception:
                item['price_max'] = Decimal('0')
                
            # Рассчитываем итоговую цену на основе количества
            quantity = item.get('quantity', 1)
            item['quantity'] = quantity
            
            if item['price_type'] == 'fixed':
                item['total_price'] = item['price'] * quantity
                item['price_display'] = f"{item['price'].normalize():g} ₽" if item['price'] else "0 ₽"
                item['total_price_display'] = f"{item['total_price'].normalize():g} ₽" if item['total_price'] else "0 ₽"
            elif item['price_type'] == 'range':
                item['total_price'] = Decimal('0')
                item['price_display'] = f"от {item['price_min'].normalize():g} до {item['price_max'].normalize():g} ₽"
                item['total_price_display'] = f"от {(item['price_min'] * quantity).normalize():g} до {(item['price_max'] * quantity).normalize():g} ₽"
            else:
                item['total_price'] = Decimal('0')
                item['price_display'] = "По договоренности"
                item['total_price_display'] = "По договоренности"
            
            item['has_flexible_price'] = item['price_type'] != 'fixed'
            
            yield item

    def get_items(self):
        """Кэширует итератор для использования внутри класса."""
        if not hasattr(self, '_items_cache'):
            self._items_cache = list(self.__iter__())
        return self._items_cache

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.get_items())

    def get_total_price(self):
        """
        Подсчет общей стоимости (только для фиксированных цен).
        """
        total = Decimal('0')
        for item in self.get_items():
            if item.get('price_type', 'fixed') == 'fixed':
                total += item.get('total_price', Decimal('0'))
        return total

    def has_flexible_prices(self):
        """
        Проверка наличия товаров с нефиксированной ценой.
        """
        return any(item.get('has_flexible_price', False) for item in self.get_items())

    def clear(self):
        # удаление корзины из сессии
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()
            
        if hasattr(self, '_items_cache'):
            del self._items_cache
