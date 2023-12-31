# Generated by Django 4.2.5 on 2023-10-02 12:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0006_remove_cartitem_customers_c_product_b35338_idx_and_more"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="cart",
            new_name="cart_combined_idx",
            old_name="customers_c_purchas_a3854a_idx",
        ),
        migrations.RenameIndex(
            model_name="cart",
            new_name="cart_is_purchased_idx",
            old_name="customers_c_is_purc_9539b7_idx",
        ),
        migrations.RenameIndex(
            model_name="cart",
            new_name="cart_purchased_at_idx",
            old_name="customers_c_purchas_2608d4_idx",
        ),
        migrations.RenameIndex(
            model_name="cartitem",
            new_name="cartitem_cart_idx",
            old_name="customers_c_cart_id_0f23de_idx",
        ),
        migrations.RenameIndex(
            model_name="cartitem",
            new_name="cartitem_product_idx",
            old_name="customers_c_product_5e8d18_idx",
        ),
        migrations.AddIndex(
            model_name="cartitem",
            index=models.Index(fields=["quantity"], name="cartitem_quantity_idx"),
        ),
        migrations.AddIndex(
            model_name="cartitem",
            index=models.Index(fields=["cart", "product"], name="cartitem_cart_product_idx"),
        ),
        migrations.AddIndex(
            model_name="cartitem",
            index=models.Index(
                fields=["product", "quantity"], name="cartitem_product_quantity_idx"
            ),
        ),
    ]
