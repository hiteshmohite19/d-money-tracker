from apps.core.date_services import dateformat_ymd
from apps.subcategories.models import SubCategory


class SubCategoriesService:

    @staticmethod
    def getSubCategoryTransactions(user, user_category_id):
        subcategories = SubCategory.objects.filter(
            user_id=user.id,
            user_category_id=user_category_id,
            is_deleted=False,
        ).prefetch_related("transactions")

        response_data = []
        for subcategory in subcategories:
            transactions = subcategory.transactions.filter(
                is_deleted=False, user_id=user.id
            ).order_by("-date", "-created_at")
            if transactions.exists():
                for transaction in transactions:
                    response_data.append(
                        {
                            "id": subcategory.id,
                            "name": subcategory.name,
                            "transaction_type": transaction.transaction_type,
                            "transaction_with": transaction.transaction_with,
                            "description": transaction.description,
                            "amount": float(transaction.amount),
                            "date": dateformat_ymd(transaction.created_at),
                        }
                    )
            else:
                response_data.append(
                    {
                        "id": subcategory.id,
                        "name": subcategory.name,
                        "transaction_type": None,
                        "transaction_with": None,
                        "description": None,
                        "amount": None,
                        "date": None,
                    }
                )
        return response_data