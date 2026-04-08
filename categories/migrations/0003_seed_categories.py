from django.db import migrations

def create_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    
    # These match your CATEGORY_CHOICES exactly
    CATEGORIES = [
        ('mobiles', 'Mobiles'),
        ('laptops', 'Laptops'),
        ('fashion', 'Fashion'),
        ('camera', 'Camera'),
        ('home', 'Home'),
        ('cars', 'Cars'),
        ('gaming', 'Gaming'),
        ('audio', 'Audio'),
        ('bikes', 'Bikes'),
        ('watch', 'Watch'),
        ('books', 'Books'),
    ]

    for slug_val, name_val in CATEGORIES:
        # get_or_create ensures we don't crash if they already exist
        Category.objects.get_or_create(
            name=slug_val, 
            defaults={'slug': slug_val}
        )

def remove_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        # This tells Django to run after your 0002 migration
        ('categories', '0002_category_slug_alter_category_icon_and__more'), 
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]