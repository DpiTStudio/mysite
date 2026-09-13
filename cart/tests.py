from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from services.models import Service, ServiceCategory, ServicePricePlan
from cart.models import Order, OrderItem

class CartTariffPlanTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(name="Разработка", slug="razrabotka")
        self.service = Service.objects.create(
            title="Создание Сайта",
            slug="sozdanie-sayta",
            category=self.category,
            price_type="fixed",
            price_fixed=Decimal("50000.00"),
            is_available_for_order=True
        )
        self.plan1 = ServicePricePlan.objects.create(
            service=self.service,
            title="Базовый",
            price=Decimal("50000.00"),
            is_available_for_order=True
        )
        self.plan2 = ServicePricePlan.objects.create(
            service=self.service,
            title="Продвинутый",
            price=Decimal("90000.00"),
            is_available_for_order=True
        )

    def test_add_to_cart_and_update_plans(self):
        # Добавляем услугу в корзину
        response = self.client.post(reverse('cart:cart_add', args=['service', self.service.id]))
        self.assertEqual(response.status_code, 302)

        # Проверяем отображение корзины
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Базовый")
        self.assertContains(response, "Продвинутый")

        # Выбираем тарифные планы через AJAX endpoint
        response = self.client.post(
            reverse('cart:cart_update_plans', args=['service', self.service.id]),
            data={'plan_ids': [self.plan1.id, self.plan2.id]},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['selected_plan_ids'], [self.plan1.id, self.plan2.id])
        self.assertEqual(data['cart_total_price_display'], "140 000 ₽")

        # Оформляем заказ
        order_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'phone': '+79998887766',
            'comment': 'Тестовый заказ',
        }
        response = self.client.post(reverse('cart:order_create'), data=order_data)
        self.assertEqual(response.status_code, 302)

        # Проверяем сохраненный заказ
        order = Order.objects.get(email='ivan@example.com')
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.service, self.service)
        self.assertEqual(set(item.selected_plans.all()), {self.plan1, self.plan2})

