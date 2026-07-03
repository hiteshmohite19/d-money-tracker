from datetime import date

from apps.categories.models import Category

from .models import UserCategories, UserMonthlyBudget


def create_user_categories(user):
    active_categories = Category.objects.filter(active=True)
    user_categories_to_create = [
        UserCategories(
            user_id=user.id,
            name=category.name,
            created_by=user.id,
            updated_by=user.id,
        )
        for category in active_categories
    ]
    if user_categories_to_create:
        UserCategories.objects.bulk_create(user_categories_to_create)


def sync_monthly_budget(user):
    today = date.today()
    income = str(user.income or "0")
    expense = str(user.estimated_expense or "0")

    last = (
        UserMonthlyBudget.objects.filter(user_id=user, active=True).order_by("-created_at").first()
    )

    if last and last.income == income and last.expense == expense:
        return

    UserMonthlyBudget.objects.filter(user_id=user).update(active=False)

    UserMonthlyBudget.objects.create(
        user_id=user,
        income=income,
        expense=expense,
        month=today.strftime("%B"),
        year=str(today.year),
        active=True,
    )
