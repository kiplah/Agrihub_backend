import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agromart.settings')
django.setup()

from products.models import Product

print(f"{'ID':<5} {'Name':<30} {'Category':<20} {'Location':<20} {'Image Path'}")
print("-" * 100)
for p in Product.objects.all():
    cat_name = p.category.name if p.category else "NULL"
    loc = p.location if p.location else "NULL"
    img = p.imagepath if p.imagepath else "NULL"
    print(f"{p.id:<5} {p.name[:28]:<30} {cat_name[:18]:<20} {loc[:18]:<20} {img}")
