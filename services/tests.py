from django.test import TestCase
from django.contrib import admin

from .models import Service, ServiceStep
from .admin import ServiceAdmin, ServiceStepAdmin, ServiceStepInline


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

