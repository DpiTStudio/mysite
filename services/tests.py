from django.test import TestCase

from .admin import ServiceAdmin


class ServiceAdminTests(TestCase):
    def test_list_display_contains_combined_category_price_column(self):
        self.assertIn('category_price_display', ServiceAdmin.list_display)

    def test_admin_media_includes_custom_stylesheet(self):
        self.assertIn('services/css/services.css', ServiceAdmin.Media.css['all'])
