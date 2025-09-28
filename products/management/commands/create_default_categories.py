from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'sets up basic product categories so vendors can start adding stuff'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Electronics',
                'description': 'Computers, phones, tablets, accessories and electronic gadgets'
            },
            {
                'name': 'Clothing & Fashion',
                'description': 'Men\'s, women\'s and children\'s clothing, shoes and accessories'
            },
            {
                'name': 'Home & Garden',
                'description': 'Furniture, home decor, garden tools and household items'
            },
            {
                'name': 'Sports & Outdoors',
                'description': 'Exercise equipment, outdoor gear, sporting goods'
            },
            {
                'name': 'Books & Media',
                'description': 'Books, movies, music, games and educational materials'
            },
            {
                'name': 'Health & Beauty',
                'description': 'Skincare, makeup, health supplements and wellness products'
            },
            {
                'name': 'Automotive',
                'description': 'Car parts, accessories, tools and automotive supplies'
            },
            {
                'name': 'Toys & Games',
                'description': 'Children\'s toys, board games, puzzles and educational toys'
            },
            {
                'name': 'Jewelry & Watches',
                'description': 'Fine jewelry, fashion jewelry, watches and accessories'
            },
            {
                'name': 'Food & Beverages',
                'description': 'Gourmet foods, beverages, snacks and cooking ingredients'
            },
            {
                'name': 'Art & Crafts',
                'description': 'Art supplies, craft materials, handmade items and collectibles'
            },
            {
                'name': 'Office Supplies',
                'description': 'Office equipment, stationery, business supplies and furniture'
            }
        ]

        created_count = 0
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} new categories!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No new categories were created. All categories already exist.')
            )