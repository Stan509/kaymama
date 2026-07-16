import os
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import User
from apps.restaurant.models import RestaurantSettings, OpeningHours
from apps.menu.models import Category, Dish, DishVariant
from apps.cms.models import PageSection, SEOPageMeta
from apps.blog.models import BlogPost
from apps.gallery.models import PhotoAlbum, Photo
from apps.reservations.models import Reservation
from apps.orders.models import Order, OrderItem

class Command(BaseCommand):
    help = 'Seeds the database with authentic Kay Mama Creole restaurant data and sample analytics.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")
        
        # 1. Accounts / Users
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@kaymama.com',
                password='AdminSecretPassword123',
                role=User.ROLE_SUPER_ADMIN,
                phone_number='694 08 12 80'
            )
            self.stdout.write("Created default superuser: admin / AdminSecretPassword123")
        else:
            admin_user = User.objects.filter(is_superuser=True).first()

        # Seed staff roles if they don't exist
        staff_roles = [
            ('chef', 'chef@kaymama.com', User.ROLE_KITCHEN, 'Cuisine'),
            ('caissier', 'caissier@kaymama.com', User.ROLE_CASHIER, 'Caisse'),
            ('livreur', 'livreur@kaymama.com', User.ROLE_DELIVERY, 'Livraison'),
            ('manager', 'manager@kaymama.com', User.ROLE_MANAGER, 'Gérant'),
        ]
        for username, email, role, label in staff_roles:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password='Password123',
                    role=role,
                    first_name=label
                )

        # Create mock customer
        customer_user, _ = User.objects.get_or_create(
            username='client',
            defaults={
                'email': 'client@example.com',
                'password': 'Password123',
                'role': User.ROLE_CUSTOMER,
                'phone_number': '0694 12 34 56',
                'address': '12 Rue des Flamboyants, Cayenne 97300'
            }
        )

        # 2. Restaurant Settings
        settings_obj, created = RestaurantSettings.objects.get_or_create(id=1)
        if created:
            self.stdout.write("Created default restaurant settings")

        # Opening hours (Mon - Sat open, Sun closed)
        for i in range(7):
            is_closed = (i == 6) # Sunday closed
            oh, created = OpeningHours.objects.get_or_create(
                day_of_week=i,
                defaults={
                    'opening_time': time(11, 30) if not is_closed else None,
                    'closing_time': time(22, 0) if not is_closed else None,
                    'is_closed': is_closed
                }
            )

        # 3. Categories (from flyer)
        categories_data = [
            ("Spécialités Créoles", "Nos plats signatures cuisinés avec amour et tradition.", 0),
            ("Plats Principaux", "Accompagnés de riz blanc ou riz djondjon, haricots rouges ou lentilles.", 1),
            ("Entrées", "Des mises en bouche savoureuses pour éveiller vos papilles.", 2),
            ("Accompagnements", "Pour compléter votre repas selon vos envies.", 3),
            ("Desserts", "La touche sucrée typiquement antillaise.", 4),
            ("Boissons", "Jus frais maison et rafraîchissements locaux.", 5),
        ]
        
        cats = {}
        for name, desc, order in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'order_index': order}
            )
            cats[name] = cat

        # 4. Dishes (from flyer)
        dishes_data = {
            "Entrées": [
                ("Salade Créole", "Mélange frais de laitue, tomate, concombre et carotte râpée.", 5.00, False),
                ("Accras de morue (x5)", "Beignets de morue croustillants et parfumés aux piments végétariens.", 6.00, False),
                ("Boudin créole (x2)", "Boudins antillais traditionnels, légèrement épicés.", 6.00, False),
                ("Samoussa de bœuf (x3)", "Feuilletés croustillants garnis de viande de bœuf assaisonnée.", 6.00, False),
                ("Salade de fruits frais", "Morceaux de fruits de saison locaux (ananas, mangue, maracuja...).", 5.00, False),
            ],
            "Plats Principaux": [
                ("Poulet boucané", "Poulet mariné puis fumé au bois de canne à sucre traditionnel.", 15.00, False),
                ("Poulet colombo", "Poulet mijoté dans un mélange d'épices colombo et légumes.", 15.00, False),
                ("Poulet yassa", "Poulet mariné au citron vert et aux oignons caramélisés.", 15.00, False),
                ("Bœuf bourguignon créole", "Bœuf mijoté à la créole avec carottes, bananes jaunes et herbes pays.", 16.00, False),
                ("Cabri massalé", "Morceaux de cabri (chèvre) fondants mijotés au massalé.", 18.00, False),
                ("Poisson grillé (selon arrivage)", "Poisson frais du jour mariné et grillé, servi avec sa sauce chien.", 18.00, False),
                ("Dinde sauce créole", "Émincé de dinde mijoté dans une sauce tomate épicée.", 16.00, False),
                ("Légumes pays", "Assortiment de légumes locaux cuits à la vapeur et rôtis (manioc, igname, banane jaune).", 13.00, False),
                ("Gratin de macaroni", "Le classique gratin antillais, crémeux et gratiné à souhait.", 13.00, False),
                ("Lasagnes créoles", "Lasagnes revisitées avec une farce de viande assaisonnée à la créole.", 14.00, False),
            ],
            "Spécialités Créoles": [
                ("Bouillon de bœuf", "Bœuf tendre mijoté avec des légumes pays, manioc, chouchou (christophine), maïs et persil.", 15.00, True),
                ("Calaloux Combos", "Pâtes de calalou (feuilles de madère, patates douces, manioc, banane), morue boucanée, légumes pays, sauce créole.", 16.00, True),
                ("Lalo", "Feuilles de madère mijotées longuement avec viande de bœuf, crabe, lardons et épices créoles.", 16.00, True),
            ],
            "Accompagnements": [
                ("Riz blanc", "Riz blanc parfumé cuit à la perfection.", 3.00, False),
                ("Riz djondjon", "Riz noir traditionnel haïtien préparé avec des champignons djondjon locaux.", 3.00, False),
                ("Riz collé avec haricots", "Riz cuit avec des haricots rouges et des épices créoles.", 4.00, False),
                ("Haricots rouges", "Haricots rouges mijotés et épicés.", 3.00, False),
                ("Lentilles", "Lentilles cuisinées à la créole.", 3.00, False),
                ("Légumes pays (supplément)", "Assortiment de manioc, patate douce, banane jaune.", 4.00, False),
                ("Frites / Banane pesée", "Bananes pesées frites croustillantes et salées.", 4.00, False),
                ("Sauce pimentée maison", "Sauce pimentée typique faite maison (attention, ça pique !).", 1.00, False),
            ],
            "Desserts": [
                ("Gâteau Créole", "Gâteau traditionnel fourré à la confiture de coco ou d'ananas.", 5.00, False),
                ("Tartelette sucrée", "Pâte sablée croustillante garnie de compote de goyave ou passion.", 5.00, False),
                ("Cupcakes", "Cupcakes moelleux parfumés au rhum vieux et coco.", 5.00, False),
                ("Mousse au chocolat créole", "Mousse au chocolat noir parfumée au zeste de citron vert et cannelle.", 5.00, False),
            ],
            "Boissons": [
                ("Jus de fruits locaux (bissap)", "Jus de fleur d'hibiscus fait maison, parfumé à la menthe et gingembre.", 3.50, False),
                ("Jus de fruits locaux (maracuja)", "Jus de fruits de la passion frais et acidulé.", 3.50, False),
                ("Jus de fruits locaux (corossol)", "Jus de corossol doux, crémeux et parfumé.", 3.50, False),
                ("Eau plate", "Bouteille d'eau de source locale (50cl).", 1.50, False),
                ("Sodas", "Coca-Cola, Fanta, Orangina (33cl).", 2.50, False),
                ("Eau gazeuse", "Bouteille d'eau gazeuse (50cl).", 2.00, False),
            ]
        }

        created_dishes = []
        for cat_name, dishes in dishes_data.items():
            category = cats[cat_name]
            for name, desc, price, is_special in dishes:
                dish, _ = Dish.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'description': desc,
                        'price': price,
                        'is_specialty': is_special,
                        'stock_level': random.randint(15, 60),
                        'is_available': True
                    }
                )
                created_dishes.append(dish)

        # 5. Dish Variants
        riz_djondjon = Dish.objects.filter(name="Riz djondjon").first()
        if riz_djondjon:
            DishVariant.objects.get_or_create(dish=riz_djondjon, name="Double portion", additional_price=2.00)

        poulet_boucane = Dish.objects.filter(name="Poulet boucané").first()
        if poulet_boucane:
            DishVariant.objects.get_or_create(dish=poulet_boucane, name="Sauce Chien Extra", additional_price=1.00)

        # 6. CMS Page Sections
        cms_sections = [
            ('HOME', 'hero_title', "L'AUTHENTICITÉ CRÉOLE à chaque bouchée", "Découvrez les saveurs uniques de la Guyane et d'Haïti chez Kay Mama.", None, "Réserver une Table", "/reservations/"),
            ('HOME', 'about_title', "Fait maison avec des produits locaux", "Parce que chaque moment mérite le meilleur ! Kay Mama Cuisine Créole est bien plus qu'un repas, c'est une expérience culinaire authentique, faite de saveurs locales, d'amour et de tradition.", None, "Notre Histoire", "/about/"),
            ('HOME', 'chef_name', "Chef Mama", "Une cuisine généreuse et chaleureuse, portée par des décennies de savoir-faire traditionnel antillais.", None, "Découvrir le Menu", "/menu/"),
            ('ABOUT', 'history', "Notre Histoire", "Kay Mama est née de la passion de partager la richesse de la cuisine créole traditionnelle. Depuis notre restaurant à Cayenne, nous cuisinons chaque matin des ingrédients frais achetés directement au marché local. Nos spécialités comme le Bouillon de Bœuf, le Lalo ou le Griot racontent l'histoire et la convivialité de nos îles.", None, "", ""),
        ]
        for page, key, title, content, img, b_text, b_link in cms_sections:
            PageSection.objects.get_or_create(
                section_key=key,
                defaults={
                    'page': page,
                    'title': title,
                    'content': content,
                    'button_text': b_text,
                    'button_link': b_link
                }
            )

        # SEO settings
        SEOPageMeta.objects.get_or_create(path='/', defaults={'meta_title': "Kay Mama - Restaurant Cuisine Créole à Cayenne", 'meta_description': "L'authenticité créole à chaque bouchée. Commandes en ligne à Cayenne, Guyane Française. Livraison et plats à emporter."})
        SEOPageMeta.objects.get_or_create(path='/menu/', defaults={'meta_title': "Menu - Kay Mama Cuisine Créole", 'meta_description': "Découvrez notre menu traditionnel créole : Poulet boucané, Lalo, Griot, Bouillon de Boeuf, Riz djondjon à emporter ou en livraison."})
        SEOPageMeta.objects.get_or_create(path='/reservations/', defaults={'meta_title': "Réservation de Table - Kay Mama", 'meta_description': "Réservez votre table en ligne chez Kay Mama Cuisine Créole à Cayenne."})

        # 7. Blog Posts
        post1, _ = BlogPost.objects.get_or_create(
            title="Le Secret du Riz Djondjon Haïtien",
            defaults={
                'author': admin_user,
                'summary': "Découvrez l'origine et la préparation de ce riz noir traditionnel si apprécié dans les Caraïbes.",
                'content': "Le riz djondjon is le plat national festif de la cuisine haïtienne. Sa couleur noire caractéristique provient des champignons séchés appelés 'djondjon' qui poussent principalement dans le nord d'Haïti. Pour extraire la couleur et l'arôme unique, on infuse ces champignons dans de l'eau bouillante avant de filtrer le liquide pour y cuire le riz, souvent accompagné de pois et de crevettes...",
                'meta_title': "Le Secret du Riz Djondjon Haïtien - Recette Kay Mama",
                'meta_description': "Découvrez l'origine et les secrets de cuisson du riz noir djondjon antillais."
            }
        )
        post2, _ = BlogPost.objects.get_or_create(
            title="Le Poulet Boucané : Technique & Traditions",
            defaults={
                'author': admin_user,
                'summary': "Plongez dans l'histoire de la fumaison traditionnelle créole et comment nous préparons notre poulet boucané.",
                'content': "Le boucanage est une méthode de conservation et de cuisson héritée des Amérindiens Caraïbes. Le poulet est mariné longuement avec du citron vert, de l'ail, du piment et des herbes pays, puis placé dans un boucanier (baril fumoir métallique) où il cuit lentement à la fumée de bagasse de canne à sucre. Cette cuisson basse température confère une texture extrêmement juteuse et un parfum fumé incomparable.",
                'meta_title': "Le Poulet Boucané Traditionnel - Kay Mama Cayenne",
                'meta_description': "Tout savoir sur la technique du boucanage du poulet en Guyane."
            }
        )

        # 8. Photo Albums
        album, _ = PhotoAlbum.objects.get_or_create(name="Nos Plats Signature", defaults={'description': "Les créations de notre cuisine."})

        # 9. Mock Reservation Data (for Analytics)
        today = date.today()
        if not Reservation.objects.exists():
            self.stdout.write("Seeding mock reservations for analytics...")
            # Seed 30 reservations in the last 15 days and next 5 days
            for i in range(-15, 6):
                res_date = today + timedelta(days=i)
                # Avoid Sundays (since oh day 6 is closed)
                if res_date.weekday() == 6:
                    continue
                
                # 1-3 reservations per day
                for _ in range(random.randint(1, 3)):
                    first_names = ['Jean', 'Marie', 'Pierre', 'Katy', 'Lucien', 'Chantal', 'Marc', 'Cynthia', 'Alix', 'Sébastien']
                    last_names = ['Dorival', 'Cyprien', 'Baptiste', 'Bélizaire', 'Metellus', 'Augustin', 'Jean-Gilles', 'Désir']
                    status_choices = [Reservation.STATUS_APPROVED] * 5 + [Reservation.STATUS_PENDING] + [Reservation.STATUS_REJECTED]
                    
                    Reservation.objects.create(
                        first_name=random.choice(first_names),
                        last_name=random.choice(last_names),
                        email=f"client.{random.randint(10,99)}@example.com",
                        phone="0694 " + "".join(str(random.randint(0,9)) for _ in range(6)),
                        date=res_date,
                        time_slot=time(random.choice([12, 13, 19, 20]), random.choice([0, 30])),
                        guest_count=random.choice([2, 4, 6, 8]),
                        occasion=random.choice([Reservation.OCCASION_FAMILY, Reservation.OCCASION_BIRTHDAY, Reservation.OCCASION_BUSINESS, Reservation.OCCASION_OTHER]),
                        notes="Besoin d'une chaise haute" if random.random() > 0.8 else "",
                        status=random.choice(status_choices) if i <= 0 else Reservation.STATUS_PENDING
                    )
        else:
            self.stdout.write("Reservations table not empty, skipping mock reservations seeding.")

        # 10. Mock Orders Data (for Analytics)
        if not Order.objects.exists():
            self.stdout.write("Seeding mock orders for analytics...")
            # Create 50 orders over the past 30 days to build nice revenue metrics
            dishes_pool = list(Dish.objects.all())
            if dishes_pool:
                for i in range(-30, 1):
                    order_date = timezone.now() + timedelta(days=i)
                    # Skip Sundays
                    if order_date.weekday() == 6:
                        continue
                    
                    # 1 to 4 orders per day
                    for _ in range(random.randint(1, 4)):
                        cust_first = random.choice(['Rodrigue', 'Evelyne', 'Dimitri', 'Widline', 'Ludovic', 'Carine'])
                        cust_last = random.choice(['Saint-Eloi', 'Joseph', 'Lafleur', 'Victor', 'Mercier'])
                        
                        method = random.choice([Order.DELIVERY_PICKUP, Order.DELIVERY_HOME])
                        status = Order.STATUS_COMPLETED if i < -1 else random.choice([Order.STATUS_COMPLETED, Order.STATUS_READY, Order.STATUS_PREPARING])
                        
                        order = Order.objects.create(
                            user=customer_user if random.random() > 0.5 else None,
                            first_name=cust_first,
                            last_name=cust_last,
                            email=f"{cust_first.lower()}@example.com",
                            phone="0694 " + "".join(str(random.randint(0,9)) for _ in range(6)),
                            delivery_method=method,
                            delivery_address="Cayenne, Guyane Française" if method == Order.DELIVERY_HOME else "",
                            delivery_time=order_date + timedelta(hours=random.choice([1, 2])),
                            status=status,
                            payment_status=Order.PAY_STATUS_PAID if status == Order.STATUS_COMPLETED else Order.PAY_STATUS_PENDING,
                            payment_method=random.choice([Order.PAY_METHOD_CARD, Order.PAY_METHOD_CASH]),
                            total_price=Decimal('0.00'), # Will calculate
                        )
                        
                        # Force creation timestamp to mock past dates
                        order.created_at = order_date
                        order.save()
                        
                        subtotal = Decimal('0.00')
                        # Add 1 to 4 dishes
                        for _ in range(random.randint(1, 4)):
                            dish = random.choice(dishes_pool)
                            qty = random.randint(1, 3)
                            price = dish.price
                            OrderItem.objects.create(
                                order=order,
                                dish=dish,
                                quantity=qty,
                                price=price
                            )
                            subtotal += price * qty
                        
                        if method == Order.DELIVERY_HOME:
                            subtotal += Decimal('5.00') # Delivery fee
                        
                        order.total_price = subtotal
                        order.save()
        else:
            self.stdout.write("Orders table not empty, skipping mock orders seeding.")
                    
        self.stdout.write(self.style.SUCCESS("Database seeded successfully with menu and analytics data!"))

