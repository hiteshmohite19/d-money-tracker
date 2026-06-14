# DMoneyTracker — API Documentation

**Base URL:** `http://localhost:8000/api`
**Authentication:** JWT Bearer Token (except public endpoints)
**Header:** `Authorization: Bearer <access_token>`

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [User Categories](#2-user-categories)
3. [Categories](#3-categories)
4. [Subcategories](#4-subcategories)
5. [Transactions](#5-transactions)
6. [Wishlist](#6-wishlist)

---

## 1. Authentication

**Base Path:** `/api/users/`

---

### 1.1 Register

**POST** `/api/users/register/`
**Auth:** Public

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "mobile": "+919999999999",
  "password": "secret123"
}
```

**Response `201`:**
```json
{
  "user": { "id": "uuid", "first_name": "John", "last_name": "Doe", "email": "john@example.com", "mobile": "+919999999999" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_categories": [ { "id": "uuid", "name": "Food & Dining" } ]
}
```

---

### 1.2 Login

**POST** `/api/users/login/`
**Auth:** Public

**Request Body:**
```json
{
  "mobile": "+918956047638"
}
```

**Response `200`:**
```json
{
  "user": { "id": "uuid", "first_name": "Hitesh", "mobile": "+918956047638" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_categories": [ { "id": "uuid", "name": "Food & Dining" } ]
}
```

**Error `404`:**
```json
{ "error": "User not found" }
```

---

### 1.3 Google Sign-In

**POST** `/api/users/signin/`
**Auth:** Public

**Request Body:**
```json
{
  "google_token": "<Google OAuth ID token>"
}
```

**Response `200` (existing user) / `201` (new user):**
```json
{
  "user": { "id": "uuid", "email": "john@gmail.com", "first_name": "John" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "created": false,
  "user_categories": [ { "id": "uuid", "name": "Salary" } ]
}
```

---

### 1.4 Verify OTP

**POST** `/api/users/verify-otp/`
**Auth:** Public

> OTP is hardcoded as `111111` for now.

**Request Body:**
```json
{
  "mobile": "+919999999999",
  "otp": "111111"
}
```

**Response `201` (new user — returns tokens):**
```json
{
  "message": "User created successfully",
  "user": { "id": "uuid", "mobile": "+919999999999" },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_categories": [],
  "user_exists": false
}
```

**Response `200` (existing user):**
```json
{
  "message": "Mobile number verified successfully",
  "user_exists": true
}
```

**Error `400` (invalid OTP):**
```json
{ "error": "Invalid OTP" }
```

---

### 1.5 Refresh Token

**POST** `/api/users/refresh-token/`
**Auth:** Public

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJ..."
}
```

**Error `401`:**
```json
{ "error": "Invalid or expired refresh token" }
```

---

### 1.6 Get Profile

**GET** `/api/users/profile/`
**Auth:** Required

**Response `200`:**
```json
{
  "id": "uuid",
  "first_name": "Hitesh",
  "last_name": "Mohite",
  "email": "hitesh@gmail.com",
  "mobile": "+918956047638",
  "is_active": true
}
```

---

### 1.7 Update User

**POST** `/api/users/update-user/`
**Auth:** Required

**Request Body (partial):**
```json
{
  "first_name": "Hitesh",
  "last_name": "Mohite",
  "email": "hitesh@gmail.com"
}
```

**Response `200`:** Updated user object.

---

### 1.8 Deactivate Account

**POST** `/api/users/deactivate/`
**Auth:** Required

**Response `200`:**
```json
{ "message": "User account deactivated successfully" }
```

---

## 2. User Categories

**Base Path:** `/api/users/`

---

### 2.1 List User Categories

**GET** `/api/users/user-categories/`
**Auth:** Required

**Response `200`:**
```json
[
  { "id": "uuid", "name": "Food & Dining", "is_deleted": false },
  { "id": "uuid", "name": "Salary", "is_deleted": false }
]
```

---

### 2.2 Create User Category

**POST** `/api/users/category/`
**Auth:** Required

**Request Body:**
```json
{
  "name": "Rent"
}
```

**Response `201`:** Full list of user categories after creation.

---

### 2.3 Update User Category

**POST** `/api/users/update-categories/<uuid:id>/`
**Auth:** Required

**Request Body (partial):**
```json
{
  "name": "Housing"
}
```

**Response `200`:** Updated category object.

---

### 2.4 Delete User Category

**GET** `/api/users/delete-category/?id=<uuid>`
**Auth:** Required

**Response `200`:**
```json
{ "message": "User category deleted successfully" }
```

---

## 3. Categories

**Base Path:** `/api/categories/`

---

### 3.1 Category Transactions Summary

**GET** `/api/categories/category-transactions/`
**Auth:** Required

Returns all user categories with their cumulative transaction amount. Amount is negative for debits and positive for credits. Categories with no transactions return `0.00`.

**Response `200`:**
```json
[
  { "category_id": "uuid", "amount": -250.00 },
  { "category_id": "uuid", "amount": 5000.00 },
  { "category_id": "uuid", "amount": 0.00 }
]
```

---

## 4. Subcategories

**Base Path:** `/api/subcategories/`

---

### 4.1 List Subcategories by User Category (with Transactions)

**GET** `/api/subcategories/<uuid:user_category_id>/sub-categories/`
**Auth:** Required

Returns all subcategories for the given user category. Each subcategory row is repeated per transaction (flat list). Subcategories with no transactions appear once with `null` transaction fields.

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "name": "Groceries",
    "transaction_type": "DEBIT",
    "transaction_with": "Walmart",
    "description": "Weekly groceries",
    "amount": 150.50
  },
  {
    "id": "uuid",
    "name": "Groceries",
    "transaction_type": "DEBIT",
    "transaction_with": "Costco",
    "description": "Monthly bulk",
    "amount": 200.00
  },
  {
    "id": "uuid",
    "name": "Restaurants",
    "transaction_type": null,
    "transaction_with": null,
    "description": null,
    "amount": null
  }
]
```

---

### 4.2 Create Subcategory

**POST** `/api/subcategories/sub-category/`
**Auth:** Required

**Request Body:**
```json
{
  "name": "Coffee Shops",
  "user_category": "<user_category_uuid>"
}
```

**Response `201`:** Full list of subcategories with transactions for the user category.

---

### 4.3 Update Subcategory

**POST** `/api/subcategories/sub-category/<uuid:id>/`
**Auth:** Required

**Request Body (partial):**
```json
{
  "name": "Cafes"
}
```

**Response `200`:** Updated subcategory object.

---

### 4.4 Delete Subcategory

**GET** `/api/subcategories/delete-sub-category/<uuid:id>/`
**Auth:** Required

**Response `200`:**
```json
{ "message": "Subcategory deleted successfully" }
```

---

## 5. Transactions

**Base Path:** `/api/transactions/`

---

### 5.1 List Transactions

**GET** `/api/transactions/transactions/`
**Auth:** Required

Returns all transactions for the authenticated user ordered by date descending.

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "user_category_id": "uuid",
    "category": "Food & Dining",
    "sub_category_id": "uuid",
    "sub_category": "Groceries",
    "sub_category_description": null,
    "transaction_type": "DEBIT",
    "transaction_with": "Walmart",
    "description": "Weekly groceries",
    "amount": 150.50,
    "date": "2026-03-01",
    "is_active": true,
    "is_deleted": false
  }
]
```

**Transaction Type Values:** `CREDIT` | `DEBIT` | `EMI`

---

### 5.2 Create Transaction

**POST** `/api/transactions/transaction/`
**Auth:** Required

**Request Body:**
```json
{
  "user_category": "<user_category_uuid>",
  "sub_category": "<sub_category_uuid>",
  "transaction_type": "DEBIT",
  "transaction_with": "Walmart",
  "description": "Weekly groceries",
  "amount": 150.50,
  "date": "2026-03-01"
}
```

**EMI Transaction (additional fields required):**
```json
{
  "user_category": "<user_category_uuid>",
  "sub_category": "<sub_category_uuid>",
  "transaction_type": "EMI",
  "transaction_with": "HDFC Bank",
  "amount": 50000.00,
  "date": "2026-03-01",
  "emi_frequency": "MONTHLY",
  "emi_period": 12,
  "emi_amount": 4500.00,
  "emi_start_date": "2026-04-01"
}
```

**EMI Frequency Values:** `DAILY` | `WEEKLY` | `MONTHLY` | `QUARTERLY` | `YEARLY`

**Response `201`:** Full list of all transactions for the user.

---

### 5.3 Update Transaction

**POST** `/api/transactions/transaction/<uuid:id>/`
**Auth:** Required

**Request Body (partial):**
```json
{
  "transaction_with": "Walmart Supercenter",
  "amount": 175.00
}
```

**Response `200`:** Updated transaction object.

---

### 5.4 Delete Transaction

**GET** `/api/transactions/delete-transaction/<uuid:id>/`
**Auth:** Required

**Response `200`:**
```json
{ "message": "Transaction deleted successfully" }
```

---

## 6. Wishlist

**Base Path:** `/api/wishlist/`

---

### 6.1 List Wishlist Items

**GET** `/api/wishlist/`
**Auth:** Required

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "item": "MacBook Pro",
    "price": 150000.00,
    "description": "Latest M3 chip",
    "expected_date": "2026-12-01"
  }
]
```

---

### 6.2 Create Wishlist Item

**POST** `/api/wishlist/create/`
**Auth:** Required

**Request Body:**
```json
{
  "item": "MacBook Pro",
  "price": 150000.00,
  "description": "Latest M3 chip",
  "expected_date": "2026-12-01"
}
```

**Response `201`:** Full list of wishlist items for the user.

---

### 6.3 Update Wishlist Item

**POST** `/api/wishlist/<uuid:id>/update/`
**Auth:** Required

**Request Body (partial):**
```json
{
  "price": 140000.00
}
```

**Response `200`:** Full list of wishlist items for the user.

---

### 6.4 Delete Wishlist Item

**GET** `/api/wishlist/delete/?id=<uuid>`
**Auth:** Required

**Response `200`:** Full list of remaining wishlist items for the user.

---

## Common Error Responses

| Status | Description |
|--------|-------------|
| `400` | Bad Request — missing or invalid fields |
| `401` | Unauthorized — missing or expired token |
| `403` | Forbidden — account deactivated |
| `404` | Not Found — resource does not exist |

---

## Notes

- All `id` fields are UUIDs.
- Soft deletes are used — deleted records remain in the database with `is_deleted: true` and are excluded from all list responses.
- `CategoryTransactions` amounts update automatically via Django signals when a transaction is created.
- Creating a new user (via `/register/`, `/verify-otp/`, or `/signin/`) automatically copies all active system categories into the user's account.
- Tokens: `access_token` expires in **24 hours**, `refresh_token` expires in **30 days**.
