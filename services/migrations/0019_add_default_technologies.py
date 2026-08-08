from django.db import migrations

def add_technologies(apps, schema_editor):
    Technology = apps.get_model('services', 'Technology')
    tech_names = [
        'HTML',
        'CSS',
        'JavaScript',
        'Bootstrap',
        'Tailwind CSS',
        'Django',
        'React',
        'Vue.js',
        'Angular',
        'Node.js',
        'Webpack',
        'Gulp',
        'Sass',
        'Less',
        'jQuery',
        'TypeScript',
        'Git',
        'GitHub',
        'GitLab',
        'Docker',
        'Kubernetes',
        'Nginx',
        'Apache',
        'PostgreSQL',
        'MySQL',
        'SQLite',
        'MongoDB',
        'Redis',
        'Celery',
        'REST API',
        'GraphQL',
        'JSON',
        'XML',
        'AWS',
        'Google Cloud',
        'Azure',
        'CI/CD',
        'Jenkins',
        'GitHub Actions',
    ]
    for name in tech_names:
        Technology.objects.get_or_create(name=name)

def remove_technologies(apps, schema_editor):
    Technology = apps.get_model('services', 'Technology')
    tech_names = [
        'HTML',
        'CSS',
        'JavaScript',
        'Bootstrap',
        'Tailwind CSS',
        'Django',
        'React',
        'Vue.js',
        'Angular',
        'Node.js',
        'Webpack',
        'Gulp',
        'Sass',
        'Less',
        'jQuery',
        'TypeScript',
        'Git',
        'GitHub',
        'GitLab',
        'Docker',
        'Kubernetes',
        'Nginx',
        'Apache',
        'PostgreSQL',
        'MySQL',
        'SQLite',
        'MongoDB',
        'Redis',
        'Celery',
        'REST API',
        'GraphQL',
        'JSON',
        'XML',
        'AWS',
        'Google Cloud',
        'Azure',
        'CI/CD',
        'Jenkins',
        'GitHub Actions',
    ]
    Technology.objects.filter(name__in=tech_names).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('services', '0018_alter_servicecategory_description'),
    ]
    operations = [
        migrations.RunPython(add_technologies, remove_technologies),
    ]
