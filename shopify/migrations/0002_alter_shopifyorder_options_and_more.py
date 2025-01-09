# Generated by Django 5.0 on 2025-01-09 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopify", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shopifyorder",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="shopifyorder",
            name="order_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddIndex(
            model_name="paymentattempt",
            index=models.Index(fields=["status"], name="shopify_pay_status_d26b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="paymentattempt",
            index=models.Index(
                fields=["payment_method"], name="shopify_pay_payment_ef9ee4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentattempt",
            index=models.Index(
                fields=["created_at"], name="shopify_pay_created_a2b0f9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="shopifyorder",
            index=models.Index(
                fields=["order_reference"], name="shopify_sho_order_r_2e9d91_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="shopifyorder",
            index=models.Index(fields=["status"], name="shopify_sho_status_8c119e_idx"),
        ),
        migrations.AddIndex(
            model_name="shopifyorder",
            index=models.Index(
                fields=["created_at"], name="shopify_sho_created_02d106_idx"
            ),
        ),
    ]
