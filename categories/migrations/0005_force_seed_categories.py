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
    ('categories', '0004_alter_category_name'), # Point to the very last file in your migrations folder
]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]