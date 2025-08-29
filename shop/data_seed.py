import os
import django
import random
from faker import Faker


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')


django.setup()


from shop.models import Product, Order


fake = Faker()


def seed(n_products=100, n_orders=1000):
    products = []
    for i in range(n_products):
        p = Product.objects.create(
        name=fake.unique.word() + str(i),
        price=round(random.uniform(5, 500), 2),
        stock_qty=random.randint(50, 1000)
        )
        products.append(p)


    for i in range(n_orders):
        p = random.choice(products)
        qty = random.randint(1, 5)
        if p.stock_qty >= qty:
            p.stock_qty -= qty
            p.save()
            Order.objects.create(product=p, quantity=qty, total_price=p.price * qty)


if __name__ == '__main__':
    seed()
    print('Seeding done')