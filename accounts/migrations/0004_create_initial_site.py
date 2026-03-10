from django.db import migrations
from django.conf import settings

def create_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site_id = getattr(settings, "SITE_ID", 1)
    
    # Check if a site with this ID already exists
    if not Site.objects.filter(id=site_id).exists():
        Site.objects.create(
            id=site_id,
            domain="localhost:4234",
            name="DPIT-CMS"
        )

def remove_site(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_user_created_at"),
        ("sites", "0001_initial"), # Ensure sites is migrated before this
        ("sites", "0002_alter_domain_unique"), # The latest in Django 4.0+
    ]

    operations = [
        migrations.RunPython(create_site, remove_site),
    ]
