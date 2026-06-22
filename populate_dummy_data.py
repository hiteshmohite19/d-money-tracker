"""
Script to populate the database with dummy data.

Usage:
    python manage.py shell < populate_dummy_data.py
    or
    python manage.py shell
    >>> exec(open('populate_dummy_data.py').read())
"""

from datetime import date, timedelta
from decimal import Decimal

from apps.categories.models import Category
from apps.endusers.models import EndUser, UserCategories
from apps.subcategories.models import SubCategory
from apps.transactions.models import Transaction, TransactionType

print("=" * 60)
print("Starting database population with dummy data...")
print("=" * 60)

# =============================================================================
# 1. Create System Categories (in Category table)
# =============================================================================
print("\n1. Creating system categories...")

categories_data = [
    {"name": "Food & Dining", "active": True},
    {"name": "Transportation", "active": True},
    {"name": "Shopping", "active": True},
    {"name": "Entertainment", "active": True},
    {"name": "Bills & Utilities", "active": True},
    {"name": "Healthcare", "active": True},
    {"name": "Education", "active": True},
    {"name": "Salary", "active": True},
    {"name": "Investment", "active": True},
]

created_categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data["name"],
        defaults={"active": cat_data["active"]},
    )
    if created:
        print(f"  ✓ Created category: {category.name}")
    else:
        print(f"  • Category already exists: {category.name}")
    created_categories.append(category)

# =============================================================================
# 2. Get Existing User
# =============================================================================
print("\n2. Getting existing user...")

try:
    user = EndUser.objects.get(mobile="+918956047638")
    print(f"  ✓ Found user: {user.full_name} ({user.email or 'No email'})")
    print(f"  User ID: {user.id}")
except EndUser.DoesNotExist:
    print("  ✗ Error: User with mobile +918956047638 not found!")
    print("  Please create the user first or update the mobile number in the script.")
    exit(1)

# =============================================================================
# 3. Create User Categories (copying from system categories)
# =============================================================================
print("\n3. Creating user categories...")

user_categories_map = {}
for category in created_categories:
    user_category, created = UserCategories.objects.get_or_create(
        user_id=user.id,
        name=category.name,
        defaults={
            "created_by": user.id,
            "updated_by": user.id,
        },
    )
    if created:
        print(f"  ✓ Created user category: {user_category.name}")
    else:
        print(f"  • User category already exists: {user_category.name}")
    user_categories_map[category.name] = user_category

# =============================================================================
# 4. Create Subcategories
# =============================================================================
print("\n4. Creating subcategories...")

subcategories_data = {
    "Food & Dining": ["Groceries", "Restaurants", "Fast Food", "Coffee Shops"],
    "Transportation": ["Fuel", "Public Transport", "Taxi/Uber", "Car Maintenance"],
    "Shopping": ["Clothing", "Electronics", "Home Goods", "Personal Care"],
    "Entertainment": ["Movies", "Games", "Subscriptions", "Events"],
    "Bills & Utilities": ["Electricity", "Water", "Internet", "Phone"],
    "Healthcare": ["Doctor Visits", "Medicines", "Insurance", "Gym"],
    "Education": ["Courses", "Books", "School Fees", "Tuition"],
    "Salary": ["Monthly Salary", "Bonus", "Freelance Income"],
    "Investment": ["Stocks", "Mutual Funds", "Fixed Deposits", "Crypto"],
}

created_subcategories = {}
for category_name, subcats in subcategories_data.items():
    if category_name in user_categories_map:
        user_category = user_categories_map[category_name]
        created_subcategories[category_name] = []

        for subcat_name in subcats:
            subcat, created = SubCategory.objects.get_or_create(
                user_id=user.id,
                user_category=user_category,
                name=subcat_name,
                defaults={
                    "is_active": True,
                    "created_by": user.id,
                    "updated_by": user.id,
                },
            )
            if created:
                print(f"  ✓ Created subcategory: {category_name} -> {subcat_name}")
            else:
                print(f"  • Subcategory already exists: {category_name} -> {subcat_name}")
            created_subcategories[category_name].append(subcat)

# =============================================================================
# 5. Create Transactions
# =============================================================================
print("\n5. Creating transactions...")


# Helper function to get a subcategory
def get_subcategory(category_name, subcat_index=0):
    if category_name in created_subcategories and created_subcategories[category_name]:
        return created_subcategories[category_name][subcat_index]
    return None


# Create various transactions
transactions_data = [
    # Credits (Income)
    {
        "category": "Salary",
        "subcat_index": 0,
        "type": TransactionType.CREDIT,
        "with": "ABC Company",
        "amount": Decimal("5000.00"),
        "date": date.today() - timedelta(days=30),
        "description": "Monthly salary",
    },
    {
        "category": "Salary",
        "subcat_index": 1,
        "type": TransactionType.CREDIT,
        "with": "ABC Company",
        "amount": Decimal("1000.00"),
        "date": date.today() - timedelta(days=25),
        "description": "Performance bonus",
    },
    {
        "category": "Salary",
        "subcat_index": 2,
        "type": TransactionType.CREDIT,
        "with": "Freelance Client",
        "amount": Decimal("800.00"),
        "date": date.today() - timedelta(days=20),
        "description": "Freelance project payment",
    },
    # Debits (Expenses)
    {
        "category": "Food & Dining",
        "subcat_index": 0,
        "type": TransactionType.DEBIT,
        "with": "Walmart",
        "amount": Decimal("150.50"),
        "date": date.today() - timedelta(days=28),
        "description": "Weekly groceries",
    },
    {
        "category": "Food & Dining",
        "subcat_index": 1,
        "type": TransactionType.DEBIT,
        "with": "Italian Restaurant",
        "amount": Decimal("65.00"),
        "date": date.today() - timedelta(days=26),
        "description": "Dinner with friends",
    },
    {
        "category": "Transportation",
        "subcat_index": 0,
        "type": TransactionType.DEBIT,
        "with": "Gas Station",
        "amount": Decimal("45.00"),
        "date": date.today() - timedelta(days=24),
        "description": "Fuel refill",
    },
    {
        "category": "Transportation",
        "subcat_index": 2,
        "type": TransactionType.DEBIT,
        "with": "Uber",
        "amount": Decimal("25.50"),
        "date": date.today() - timedelta(days=22),
        "description": "Ride to airport",
    },
    {
        "category": "Shopping",
        "subcat_index": 0,
        "type": TransactionType.DEBIT,
        "with": "Zara",
        "amount": Decimal("120.00"),
        "date": date.today() - timedelta(days=20),
        "description": "New shirt and pants",
    },
    {
        "category": "Shopping",
        "subcat_index": 1,
        "type": TransactionType.DEBIT,
        "with": "Best Buy",
        "amount": Decimal("350.00"),
        "date": date.today() - timedelta(days=18),
        "description": "Wireless headphones",
    },
    {
        "category": "Entertainment",
        "subcat_index": 2,
        "type": TransactionType.DEBIT,
        "with": "Netflix",
        "amount": Decimal("15.99"),
        "date": date.today() - timedelta(days=15),
        "description": "Monthly subscription",
    },
    {
        "category": "Bills & Utilities",
        "subcat_index": 0,
        "type": TransactionType.DEBIT,
        "with": "Electric Company",
        "amount": Decimal("85.00"),
        "date": date.today() - timedelta(days=10),
        "description": "Electricity bill",
    },
    {
        "category": "Bills & Utilities",
        "subcat_index": 2,
        "type": TransactionType.DEBIT,
        "with": "ISP Provider",
        "amount": Decimal("55.00"),
        "date": date.today() - timedelta(days=8),
        "description": "Internet bill",
    },
    {
        "category": "Healthcare",
        "subcat_index": 1,
        "type": TransactionType.DEBIT,
        "with": "Pharmacy",
        "amount": Decimal("30.00"),
        "date": date.today() - timedelta(days=5),
        "description": "Prescription medicines",
    },
    {
        "category": "Investment",
        "subcat_index": 1,
        "type": TransactionType.DEBIT,
        "with": "Investment Broker",
        "amount": Decimal("500.00"),
        "date": date.today() - timedelta(days=3),
        "description": "Mutual fund investment",
    },
]

transaction_count = 0
for trans_data in transactions_data:
    category_name = trans_data["category"]
    user_category = user_categories_map.get(category_name)
    subcategory = get_subcategory(category_name, trans_data["subcat_index"])

    if user_category and subcategory:
        transaction, created = Transaction.objects.get_or_create(
            user_id=user.id,
            user_category=user_category,
            sub_category=subcategory,
            transaction_type=trans_data["type"],
            date=trans_data["date"],
            amount=trans_data["amount"],
            defaults={
                "transaction_with": trans_data["with"],
                "is_active": True,
                "created_by": user.id,
                "updated_by": user.id,
            },
        )
        if created:
            transaction_count += 1
            print(
                f"  ✓ Created {trans_data['type']} transaction: ${trans_data['amount']} - {trans_data['with']}"
            )
        else:
            print(f"  • Transaction already exists: {trans_data['type']} - ${trans_data['amount']}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 60)
print("Database population completed!")
print("=" * 60)
print("\nSummary:")
print(f"  - Categories: {len(created_categories)}")
print(f"  - User: {user.full_name} (ID: {user.id})")
print(f"  - User Categories: {len(user_categories_map)}")
print(f"  - Subcategories: {sum(len(v) for v in created_subcategories.values())}")
print(f"  - Transactions: {transaction_count}")

print("\n" + "=" * 60)
print("You can now use the following credentials:")
print(f"  Mobile: {user.mobile}")
print(f"  Email: {user.email}")
print("=" * 60)
