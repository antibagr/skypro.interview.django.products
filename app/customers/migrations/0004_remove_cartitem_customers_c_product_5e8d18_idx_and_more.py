# Generated by Django 4.2.5 on 2023-10-02 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0003_cart_customers_c_is_purc_9539b7_idx"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="cartitem",
            name="customers_c_product_5e8d18_idx",
        ),
        migrations.AddIndex(
            model_name="cartitem",
            index=models.Index(fields=["product", "cart"], name="customers_c_product_b35338_idx"),
        ),
    ]