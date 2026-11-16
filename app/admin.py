from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

# Extend the default admin site with a custom URL for the maintenance dashboard.

def get_custom_admin_urls(urls):
    def get_urls():
        custom_urls = [
            path('maintenance/', admin.site.admin_view(lambda request: redirect('maintenance:dashboard')), name='maintenance_dashboard'),
        ]
        return custom_urls + urls
    return get_urls

# Patch the admin site's get_urls method.
admin.site.get_urls = get_custom_admin_urls(admin.site.get_urls())
