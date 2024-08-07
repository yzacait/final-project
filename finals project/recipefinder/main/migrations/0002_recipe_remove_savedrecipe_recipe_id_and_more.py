# Generated by Django 5.0.7 on 2024-07-16 02:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("difficulty", models.CharField(max_length=50)),
                ("cuisine", models.CharField(max_length=50)),
                ("vegetarian", models.BooleanField()),
                ("ingredients", models.TextField()),
                ("instructions", models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name="savedrecipe",
            name="recipe_id",
        ),
        migrations.AddField(
            model_name="savedrecipe",
            name="recipe",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="main.recipe"
            ),
        ),
    ]
