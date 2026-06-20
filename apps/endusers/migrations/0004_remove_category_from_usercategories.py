from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('endusers', '0003_add_soft_delete_to_user_categories'),
    ]

    operations = [
        # Remove the old unique_together constraint (user_id, category)
        migrations.AlterUniqueTogether(
            name='usercategories',
            unique_together=set(),
        ),
        # Remove the index that includes category
        migrations.RemoveIndex(
            model_name='usercategories',
            name='user_catego_user_id_e13647_idx',
        ),
        # Remove the category field (this will also remove the FK constraint)
        migrations.RemoveField(
            model_name='usercategories',
            name='category',
        ),
        # Add new unique constraint on user_id and name
        migrations.AddConstraint(
            model_name='usercategories',
            constraint=models.UniqueConstraint(
                fields=['user_id', 'name'],
                name='unique_user_category_per_user'
            ),
        ),
    ]
