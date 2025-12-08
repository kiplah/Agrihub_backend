from django.core.management.base import BaseCommand
from products.models import ProductCategory

class Command(BaseCommand):
    help = 'Seeds the database with initial categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding categories...')

        # Define Category Map
        categories = {
            "FARM PRODUCE": {
                "Cereals & Grains": ["Maize", "Beans", "Wheat", "Sorghum", "Millet", "Rice"],
                "Vegetables": ["Tomatoes", "Onions", "Cabbage", "Carrots", "Spinach", "Sukuma Wiki (Kale)", "Peppers"],
                "Fruits": ["Bananas", "Mangoes", "Avocados", "Oranges", "Watermelon", "Pineapples"],
                "Livestock": ["Poultry", "Chickens (Broilers / Layers)", "Ducks", "Turkeys", "Indigenous chicken (Kienyeji)", "Goats", "Dairy goats", "Meat goats", "Cattle", "Dairy cows", "Beef cattle", "Sheep", "Rabbits"],
                "Livestock Products": ["Eggs", "Milk", "Meat (Beef / Mutton / Pork / Chicken)", "Honey"]
            },
            "FARM INPUTS": {
                "Seeds": ["Maize seeds", "Vegetable seeds", "Fruit seedlings", "Tree seedlings"],
                "Fertilizers": ["Organic fertilizers", "Inorganic fertilizers", "Manure"],
                "Crop Protection": ["Pesticides", "Herbicides", "Fungicides"],
                "Animal Feeds": ["Poultry feeds", "Dairy meal", "Pig feeds", "Mineral supplements"],
                "Veterinary Products": ["Vaccines", "Antibiotics", "Dewormers"],
                "Machines & Equipment": ["Tractors", "Sprayers", "Irrigation pumps", "Incubators", "Chaff cutters", "Milking machines"],
                "Farm Tools": ["Hoes", "Pangas", "Rakes", "Watering cans", "Irrigation kits"]
            }
        }

        # Clear existing categories (Optional: depending on requirements, here I'm adding/getting)
        # ProductCategory.objects.all().delete() # Be careful with this

        for main_cat_name, sub_map in categories.items():
            main_cat, _ = ProductCategory.objects.get_or_create(name=main_cat_name, parent=None)
            self.stdout.write(f'Created/Found Main Category: {main_cat.name}')

            for sub_cat_name, children in sub_map.items():
                sub_cat, _ = ProductCategory.objects.get_or_create(name=sub_cat_name, parent=main_cat)
                
                # Check if children are just strings (leaf nodes) or if I need another level
                # The prompt implies: Main -> Sub (e.g. Farm Produce -> Cereals)
                # But "Maize" is listed under "Cereals".
                # So it's Main -> Sub -> Child
                # CreateProduct form was requested to have "Select Main Category", "Select Subcategory".
                # But then "Maize" is what user selects...
                # The prompt says: "Select Subcategory (e.g., Cereals -> Maize)"
                # This logic implies 3 levels? Or Subcategory IS "Cereals" and "Maize" is... specific product?
                # Prompt: "Select Subcategory (e.g., Cereals -> Maize)" might mean "Cereals" is the group, "Maize" is the selection.
                # Let's support 3 levels just in case, but structure the loop to handle it.
                
                # Actually, looking at the layout: "FARM PRODUCE -> A. Cereals & Grains -> Maize"
                # So "Maize" is a leaf category.
                # Let's add them as children of Subcategory.
                
                for child_name in children:
                    ProductCategory.objects.get_or_create(name=child_name, parent=sub_cat)

        self.stdout.write(self.style.SUCCESS('Successfully seeded categories'))
