from django.db import migrations

def seed_data(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    items = [
        ('mobiles', 'Mobiles'), ('laptops', 'Laptops'), ('fashion', 'Fashion'),
        ('camera', 'Camera'), ('home', 'Home'), ('cars', 'Cars'),
        ('gaming', 'Gaming'), ('audio', 'Audio'), ('bikes', 'Bikes'),
        ('watch', 'Watch'), ('books', 'Books'),
    ]
    for s, n in items:
        # This will either create it OR update it if it exists
        Category.objects.update_or_create(slug=s, defaults={'name': s})

class Migration(migrations.Migration):
    dependencies = [
        ('categories', '0001_initial'), # This is the safest dependency to use
    ]
    operations = [
        migrations.RunPython(seed_data),
    ]