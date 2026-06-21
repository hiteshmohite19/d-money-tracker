from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        (
            "subcategories",
            "0002_rename_subcategori_user_id_91f25e_idx_sub_categor_user_id_b5f1c9_idx_and_more",
        ),
        ("endusers", "0001_initial"),
    ]

    operations = [
        # Delete the existing table
        migrations.DeleteModel(
            name="SubCategory",
        ),
        # Recreate with new schema
        migrations.CreateModel(
            name="SubCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(help_text="Subcategory name", max_length=100)),
                ("user_id", models.UUIDField(help_text="User ID who owns this subcategory")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this subcategory is currently active"
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False, help_text="Soft delete flag")),
                (
                    "created_by",
                    models.UUIDField(
                        blank=True, help_text="User ID who created this subcategory", null=True
                    ),
                ),
                (
                    "updated_by",
                    models.UUIDField(
                        blank=True, help_text="User ID who last updated this subcategory", null=True
                    ),
                ),
                (
                    "user_category",
                    models.ForeignKey(
                        help_text="Parent user category",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subcategories",
                        to="endusers.usercategories",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subcategory",
                "verbose_name_plural": "Subcategories",
                "db_table": "sub_categories",
                "ordering": ["user_category", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="subcategory",
            index=models.Index(
                fields=["user_id", "user_category"], name="sub_categor_user_id_a9d52b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="subcategory",
            index=models.Index(fields=["is_active"], name="sub_categor_is_acti_4d8f6c_idx"),
        ),
        migrations.AddIndex(
            model_name="subcategory",
            index=models.Index(fields=["is_deleted"], name="sub_categor_is_dele_8e7a5b_idx"),
        ),
        migrations.AddConstraint(
            model_name="subcategory",
            constraint=models.UniqueConstraint(
                fields=("user_id", "user_category", "name"),
                name="unique_subcategory_per_user_category",
            ),
        ),
    ]
