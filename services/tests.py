from django.test import TestCase
from django.contrib import admin

from .models import Service, ServiceStep, ServicePricePlan, ServiceOrder
from .admin import ServiceAdmin, ServiceStepAdmin, ServiceStepInline, ServicePricePlanAdmin
from .forms import ServiceOrderForm


class ServiceAdminTests(TestCase):
    def test_list_display_contains_combined_category_price_column(self):
        self.assertIn('category_price_display', ServiceAdmin.list_display)

    def test_admin_media_includes_custom_stylesheet(self):
        self.assertIn('services/css/services.css', ServiceAdmin.Media.css['all'])

    def test_servicestep_registered_in_admin(self):
        self.assertIn(ServiceStep, admin.site._registry)
        self.assertIsInstance(admin.site._registry[ServiceStep], ServiceStepAdmin)

    def test_servicestep_can_be_created_for_service(self):
        service = Service.objects.create(
            title="Тестовая услуга",
            slug="test-service",
            price_type="fixed",
            price_fixed=1000,
        )
        step = ServiceStep.objects.create(
            service=service,
            step_number=1,
            title="Этап 1: Аналитика",
            description="Проведение исследования",
            order=1,
        )
        self.assertEqual(step.service, service)
        self.assertEqual(str(step), "1. Этап 1: Аналитика")
        self.assertEqual(service.steps.count(), 1)

    def test_service_price_plan_can_be_ordered_property(self):
        service = Service.objects.create(
            title="Тестовая услуга с тарифом",
            slug="test-service-plan",
            price_type="fixed",
            price_fixed=5000,
            is_available_for_order=True
        )
        plan_active = ServicePricePlan.objects.create(
            service=service,
            title="Базовый",
            price=5000,
            is_available_for_order=True
        )
        plan_inactive = ServicePricePlan.objects.create(
            service=service,
            title="VIP",
            price=15000,
            is_available_for_order=False
        )

        self.assertTrue(plan_active.can_be_ordered)
        self.assertFalse(plan_inactive.can_be_ordered)

        # Отключаем заказ всей услуги
        service.is_available_for_order = False
        service.save()
        self.assertFalse(plan_active.can_be_ordered)

    def test_service_order_form_validation_for_disabled_plan(self):
        service = Service.objects.create(
            title="Услуга для заказа",
            slug="order-service",
            price_type="fixed",
            price_fixed=2000,
        )
        disabled_plan = ServicePricePlan.objects.create(
            service=service,
            title="Архивный тариф",
            price=1000,
            is_available_for_order=False
        )

        form_data = {
            'full_name': 'Тест Тестов',
            'phone': '+79991112233',
            'email': 'test@example.com',
            'selected_plan': disabled_plan.pk,
        }
        form = ServiceOrderForm(data=form_data)
        form.fields['selected_plan'].queryset = ServicePricePlan.objects.all()
        self.assertFalse(form.is_valid())
        self.assertIn('selected_plan', form.errors)

    def test_can_be_ordered_property_conditions(self):
        service = Service.objects.create(
            title="Доступная услуга",
            slug="avail-service",
            price_type="fixed",
            price_fixed=1000,
            is_active=True,
            is_available_for_order=True
        )
        self.assertTrue(service.can_be_ordered)

        # 1. Запрет заказа по флагу
        service.is_available_for_order = False
        service.save()
        self.assertFalse(service.can_be_ordered)

        # 2. Неактивная услуга
        service.is_available_for_order = True
        service.is_active = False
        service.save()
        self.assertFalse(service.can_be_ordered)

        # 3. Фиксированная цена не задана или <= 0
        service.is_active = True
        service.price_fixed = 0
        service.save()
        self.assertFalse(service.can_be_ordered)

    def test_service_order_view_blocks_unavailable_service(self):
        service = Service.objects.create(
            title="Заблокированная услуга",
            slug="blocked-service",
            price_type="fixed",
            price_fixed=3000,
            is_available_for_order=False
        )
        response = self.client.post(f"/services/order/{service.slug}/", {
            'full_name': 'Петр Петров',
            'phone': '+79990000000',
            'email': 'petr@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ServiceOrder.objects.filter(service=service).count(), 0)

