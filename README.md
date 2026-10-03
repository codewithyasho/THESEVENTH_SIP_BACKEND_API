# The Seventh Sip --- Backend API

A production-style REST API backend for **The Seventh Sip**, a cafe
ordering platform.

The API is built with **FastAPI + SQLModel + SQLite** and provides
complete backend functionality for:

- Menu management
- User registration and authentication
- Add-on management
- Order creation
- Order item customization
- Order add-ons
- Order history
- Order cancellation
- Admin order-status management
- User ownership protection
- Interactive Swagger/OpenAPI documentation

> **Current project status:** Core API functionality has been
> implemented and end-to-end tested successfully.

---

## 📌 Table of Contents

1.  [Project Overview](#-project-overview)
2.  [Features](#-features)
3.  [Tech Stack](#-tech-stack)
4.  [Project Architecture](#-project-architecture)
5.  [Database Design](#-database-design)
6.  [Authentication](#-authentication)
7.  [Environment Variables](#-environment-variables)
8.  [Installation](#-installation)
9.  [Running the API](#-running-the-api)
10. [Swagger Documentation](#-swagger-documentation)
11. [API Structure](#-api-structure)
12. [Menu APIs](#-menu-apis)
13. [User APIs](#-user-apis)
14. [Add-on APIs](#-add-on-apis)
15. [Order APIs](#-order-apis)
16. [Order Lifecycle](#-order-lifecycle)
17. [Order Calculation](#-order-calculation)
18. [Example Order](#-example-order)
19. [Validation and Error Handling](#-validation-and-error-handling)
20. [Security and Ownership](#-security-and-ownership)
21. [Database Behavior](#-database-behavior)
22. [Testing Checklist](#-testing-checklist)
23. [Example Test Data](#-example-test-data)
24. [Git Workflow](#-git-workflow)
25. [Future Improvements](#-future-improvements)
26. [Project Status](#-project-status)
27. [Author](#-author)

---

# 🍵 Project Overview

**The Seventh Sip** is a cafe ordering backend designed around a simple
workflow:

```text
Admin
  │
  ├── Manage Menu
  ├── Manage Add-ons
  ├── Manage Users
  └── Manage Order Status
          │
          ▼
       Customers
          │
          ├── Register / Login
          ├── Browse Menu
          ├── View Add-ons
          ├── Create Orders
          ├── Add Special Instructions
          ├── View Their Orders
          └── Cancel Pending Orders
```

The backend exposes RESTful endpoints that can be consumed by:

- A web frontend
- A mobile application
- Swagger UI
- Postman
- Any HTTP client

---

# 🚀 Features

## Menu Management

Admins can:

- Create a menu item
- Create multiple menu items in bulk
- Update menu items
- Delete menu items
- List all menu items

Users can:

- View menu items
- Filter menu by category
- View menu names
- View categories
- Sort/list menu by price
- Filter menu by price range

---

## User Management

Users can:

- Register an account
- Login
- Update their own details
- Authenticate using a user secret key

Admins can:

- List all users
- List usernames
- Get a user by ID
- Delete a user

---

## Add-on Management

Admins can:

- Create add-ons
- Update add-ons
- Delete add-ons

Users can:

- View add-ons available for a specific menu item

Examples:

```text
Classic Cold Coffee
├── Chocolate Crush
└── Extra Cream

Club Sandwich
├── Extra Cheese
└── Extra Sauce
```

---

## Order Management

Users can:

- Create an order
- Add multiple menu items
- Set quantities
- Select add-ons
- Add special instructions
- View all their orders
- View a specific order
- Cancel eligible orders

Admins can:

- Update order status

---

# 🛠 Tech Stack

Technology Purpose

---

Python Programming language
FastAPI REST API framework
SQLModel Database models + ORM layer
Pydantic Request/response validation
SQLite Development database
SQLAlchemy SQLModel's underlying database layer
Uvicorn ASGI server
python-dotenv Environment variable loading
Swagger / OpenAPI API documentation

---

# 📁 Project Architecture

A typical project structure is:

```text
THESEVENTH_SIP_BACKEND_API/
│
├── main.py
│
├── database.db
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── auth.py
│   └── database.py
│
├── models/
│   ├── __init__.py
│   ├── menu.py
│   ├── user.py
│   ├── addon.py
│   └── order.py
│
└── routes/
    ├── __init__.py
    ├── menu.py
    ├── user.py
    ├── addon.py
    └── order.py
```

The exact filenames can differ depending on the final project structure.

---

# 🗄 Database Design

The application currently uses SQLite.

The database contains these tables:

```text
menutable
usertable
addontable
ordertable
ordermenutable
orderaddontable
```

---

## 1. `menutable`

Stores available cafe menu items.

```text
menu_id
menu_name
menu_category
menu_price
```

Example:

```text
1 | Classic Cold Coffee | Cold Coffee | 29
13 | Club Sandwich       | Sandwich   | 120
```

---

## 2. `usertable`

Stores registered users.

```text
user_id
username
email
password
secret_key
```

> Password hashing is planned as a future security improvement. The
> current development version uses plain-text credentials.

---

## 3. `addontable`

Stores add-ons associated with menu items.

```text
addon_id
menu_id
name
price
```

Example:

```text
1 | 1  | Chocolate Crush | 7
2 | 1  | Extra Cream     | 10
3 | 13 | Extra Cheese    | 10
4 | 13 | Extra Sauce     | 5
```

---

## 4. `ordertable`

Stores the main order record.

```text
order_id
user_id
total_amount
status
created_at
```

---

## 5. `ordermenutable`

Stores individual menu items inside an order.

```text
id
order_id
menu_id
menu_name
quantity
price
special_instructions
```

The `menu_name` and `price` are stored as an **order snapshot**.

This is important because a menu item can change later.

For example:

```text
At order time:
Classic Cold Coffee = ₹29

Later:
Classic Cold Coffee = ₹35
```

The old order still records:

```text
Classic Cold Coffee
₹29
```

This preserves historical order information.

---

## 6. `orderaddontable`

Stores the add-ons selected for an order item.

```text
id
order_item_id
addon_id
addon_name
price
```

Like menu items, add-on name and price are stored as snapshots.

---

# 🔐 Authentication

The project currently uses two authentication mechanisms.

## Admin Authentication

Admin routes require:

```http
X-API-Key: YOUR_ADMIN_SECRET
```

The key is loaded from the environment.

Example:

```env
ADMIN_SECRET=your-admin-secret
```

The dependency verifies the incoming API key.

---

## User Authentication

Authenticated user routes use:

```http
X-User-Secret: YOUR_USER_SECRET
```

The secret key is generated when the user registers.

Example:

```http
X-User-Secret: kcDkhzoldBzy
```

The backend uses this key to find the corresponding user and inject the
authenticated user into the route.

Therefore, users do **not** need to send `user_id` when creating an
order.

The backend determines the user from:

```text
X-User-Secret
      ↓
get_current_user()
      ↓
UserTable
      ↓
user_id
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
ADMIN_SECRET=your-super-secret-admin-key
```

Example:

```env
ADMIN_SECRET=my-admin-secret-123
```

Do not commit `.env` to Git.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
database.db
```

For production, secrets should be stored using a proper
secret-management mechanism.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

Move into the project:

```bash
cd THESEVENTH_SIP_BACKEND_API
```

---

## 2. Create virtual environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the API

Run:

```bash
python main.py
```

The development server runs at:

```text
http://127.0.0.1:8000
```

---

# 📚 Swagger Documentation

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI allows you to:

- View every endpoint
- Enter request parameters
- Add authentication headers
- Send requests
- View responses
- Test validation
- Test error handling

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# 🧭 API Structure

The main API groups are:

```text
Menu
Users
Add-ons
Orders
```

---

# 🍽 Menu APIs

## Admin Menu Management

Method Endpoint Description

---

POST `/menu/admin/create` Create one menu item
POST `/menu/admin/create/bulk` Create multiple menu items
PATCH `/menu/admin/update/{menu_id}` Update menu item
DELETE `/menu/admin/delete/{menu_id}` Delete menu item

All admin menu-management routes require:

```http
X-API-Key
```

---

## User Menu APIs

Method Endpoint Description

---

GET `/menu/list` List menu items
GET `/menu/filter` Filter by category
GET `/menu/list/names` List menu names
GET `/menu/list/categories` List categories
GET `/menu/list/price` List menu items by price
GET `/menu/filter/price` Filter by price range

---

## Create Menu Item

```http
POST /menu/admin/create
```

Example:

```json
{
  "menu_name": "Classic Cold Coffee",
  "menu_category": "Cold Coffee",
  "menu_price": 29
}
```

Header:

```http
X-API-Key: YOUR_ADMIN_SECRET
```

---

## Bulk Menu Creation

```http
POST /menu/admin/create/bulk
```

Example:

```json
[
  {
    "menu_name": "Classic Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 29
  },
  {
    "menu_name": "Thick Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 29
  },
  {
    "menu_name": "Caramel Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 39
  },
  {
    "menu_name": "Oreo Shake",
    "menu_category": "Shakes",
    "menu_price": 39
  },
  {
    "menu_name": "Kitkat Shake",
    "menu_category": "Shakes",
    "menu_price": 45
  }
]
```

---

# 👤 User APIs

## User Routes

Method Endpoint Description

---

POST `/users/register` Register a user
POST `/users/login` Login
PATCH `/users/update` Update current user

---

## Admin User Routes

Method Endpoint Description

---

GET `/users/admin/list` List users
GET `/users/admin/list/usernames` List usernames
GET `/users/admin/{user_id}` Get user by ID
DELETE `/users/admin/delete/{user_id}` Delete user

Admin routes require:

```http
X-API-Key
```

---

## Register

```http
POST /users/register
```

Example:

```json
{
  "username": "rahul",
  "email": "rahul@example.com",
  "password": "test123456"
}
```

The response includes a generated user secret.

Example:

```json
{
  "status": "success",
  "message": "User registered successfully.",
  "user": {
    "user_id": 2,
    "username": "rahul",
    "email": "rahul@example.com"
  },
  "secret_key": "kcDkhzoldBzy"
}
```

Save the `secret_key`.

It is required for authenticated user operations.

---

## Login

```http
POST /users/login
```

Example:

```json
{
  "username": "rahul",
  "password": "test123456"
}
```

---

## Update Current User

```http
PATCH /users/update
```

Header:

```http
X-User-Secret: YOUR_USER_SECRET
```

Example:

```json
{
  "username": "rahul_dev"
}
```

The user does not send their own `user_id`.

---

# 🧩 Add-on APIs

## Admin

Method Endpoint Description

---

POST `/addons/admin/create` Create add-on
PATCH `/addons/admin/update/{addon_id}` Update add-on
DELETE `/addons/admin/delete/{addon_id}` Delete add-on

---

## User

Method Endpoint Description

---

GET `/addons/menu/{menu_id}` Get add-ons for a menu item

---

## Create Add-on

```http
POST /addons/admin/create
```

Header:

```http
X-API-Key: YOUR_ADMIN_SECRET
```

Example:

```json
{
  "menu_id": 1,
  "name": "Chocolate Crush",
  "price": 7
}
```

Another:

```json
{
  "menu_id": 13,
  "name": "Extra Cheese",
  "price": 10
}
```

---

## Get Menu Add-ons

```http
GET /addons/menu/1
```

Example response:

```json
[
  {
    "addon_id": 1,
    "menu_id": 1,
    "name": "Chocolate Crush",
    "price": 7
  },
  {
    "addon_id": 2,
    "menu_id": 1,
    "name": "Extra Cream",
    "price": 10
  }
]
```

---

# 🛒 Order APIs

## User Order Routes

Method Endpoint Description

---

POST `/orders/create` Create order
GET `/orders/my-orders` Get current user's orders
GET `/orders/{order_id}` Get a specific order
PATCH `/orders/{order_id}/cancel` Cancel an eligible order

User routes require:

```http
X-User-Secret
```

---

## Admin Order Route

Method Endpoint Description

---

PATCH `/orders/admin/{order_id}/status` Update order status

Admin order status updates require:

```http
X-API-Key
```

---

# 🛍 Create Order

```http
POST /orders/create
```

Header:

```http
X-User-Secret: YOUR_USER_SECRET
```

The request does **not** contain `user_id`.

Example:

```json
{
  "items": [
    {
      "menu_id": 1,
      "quantity": 1,
      "addon_ids": [1],
      "special_instructions": "Make it less sweet"
    }
  ]
}
```

---

# 📝 Order Item Fields

Each item can contain:

```text
menu_id
quantity
addon_ids
special_instructions
```

### `menu_id`

The ID of the menu item.

### `quantity`

Number of units.

Must be greater than zero.

### `addon_ids`

List of add-on IDs selected for that menu item.

### `special_instructions`

Optional free-text customization.

Examples:

```text
Make it less sweet
```

```text
Less ice
```

```text
Cut into two pieces
```

```text
Add extra chocolate
```

---

# 💰 Order Calculation

The backend calculates the total from the database.

For each item:

```text
(menu_price + selected_add-on_prices) × quantity
```

Then:

```text
order_total = sum(all item totals)
```

The client should not be trusted to provide the final price.

---

# 📦 Example Order

Request:

```json
{
  "items": [
    {
      "menu_id": 1,
      "quantity": 2,
      "addon_ids": [1, 2],
      "special_instructions": "Less ice"
    },
    {
      "menu_id": 13,
      "quantity": 1,
      "addon_ids": [3],
      "special_instructions": "Cut into two pieces"
    }
  ]
}
```

Assume:

```text
Classic Cold Coffee = ₹29
Chocolate Crush = ₹7
Extra Cream = ₹10

Club Sandwich = ₹120
Extra Cheese = ₹10
```

Calculation:

```text
Classic Cold Coffee:

(29 + 7 + 10) × 2
= 46 × 2
= ₹92
```

```text
Club Sandwich:

(120 + 10) × 1
= ₹130
```

Final:

```text
₹92 + ₹130
= ₹222
```

Response:

```json
{
  "order_id": 2,
  "user_id": 2,
  "total_amount": 222,
  "status": "pending",
  "items": [
    {
      "id": 2,
      "menu_id": 1,
      "menu_name": "Classic Cold Coffee",
      "quantity": 2,
      "price": 29,
      "special_instructions": "Less ice",
      "addons": [
        {
          "id": 2,
          "addon_id": 1,
          "addon_name": "Chocolate Crush",
          "price": 7
        },
        {
          "id": 3,
          "addon_id": 2,
          "addon_name": "Extra Cream",
          "price": 10
        }
      ],
      "item_total": 92
    },
    {
      "id": 3,
      "menu_id": 13,
      "menu_name": "Club Sandwich",
      "quantity": 1,
      "price": 120,
      "special_instructions": "Cut into two pieces",
      "addons": [
        {
          "id": 4,
          "addon_id": 3,
          "addon_name": "Extra Cheese",
          "price": 10
        }
      ],
      "item_total": 130
    }
  ]
}
```

---

# 📋 Get My Orders

```http
GET /orders/my-orders
```

Header:

```http
X-User-Secret: YOUR_USER_SECRET
```

This returns only orders belonging to the authenticated user.

Conceptually:

```text
X-User-Secret
      ↓
get_current_user()
      ↓
user_id
      ↓
WHERE order.user_id == current_user.user_id
```

---

# 🔎 Get Specific Order

```http
GET /orders/{order_id}
```

Example:

```http
GET /orders/2
```

Header:

```http
X-User-Secret: YOUR_USER_SECRET
```

Users can only access their own orders.

---

# ❌ Cancel Order

```http
PATCH /orders/{order_id}/cancel
```

Header:

```http
X-User-Secret: YOUR_USER_SECRET
```

An order is not deleted when canceled.

Instead:

```text
pending
   ↓
canceled
```

The order remains in the database for historical records.

---

# 🚦 Order Lifecycle

The supported statuses are:

```text
pending
confirmed
preparing
on_the_way
delivered
canceled
```

Typical order flow:

```text
pending
   ↓
confirmed
   ↓
preparing
   ↓
on_the_way
   ↓
delivered
```

Customer cancellation:

```text
pending
   ↓
canceled
```

---

# 👨‍💼 Admin Order Status

Endpoint:

```http
PATCH /orders/admin/{order_id}/status
```

Header:

```http
X-API-Key: YOUR_ADMIN_SECRET
```

Example:

```json
{
  "status": "confirmed"
}
```

Then:

```json
{
  "status": "preparing"
}
```

Then:

```json
{
  "status": "on_the_way"
}
```

Finally:

```json
{
  "status": "delivered"
}
```

---

# 🔒 Validation and Error Handling

The API validates incoming data using Pydantic/SQLModel models.

Examples of validation rules include:

```text
username → minimum length
password → minimum length
quantity → greater than 0
menu price → non-negative
add-on price → positive
order items → at least one item
```

---

## Common HTTP Status Codes

    Status Meaning

---

       200 Successful request
       201 Resource created, when configured by the endpoint
       400 Invalid request/business rule
       401 Authentication failure
       403 Authenticated but not authorized
       404 Resource not found
       409 Duplicate/conflicting resource
       422 Request validation error
       500 Unexpected server error

---

# 🔐 Security and Ownership

The order system prevents users from accessing other users' orders.

For example:

```text
User #2
   ↓
Order #1 belongs to User #2
   ↓
Access allowed
```

But:

```text
User #1
   ↓
tries GET /orders/1
   ↓
Order belongs to User #2
   ↓
403 Forbidden
```

This was explicitly tested during development.

---

# 🧪 Testing

The API has been tested end-to-end through Swagger UI.

The test flow included:

```text
Menu
├── Create
├── Bulk create
├── List
├── Filter
├── Names
├── Categories
├── Price
├── Price filter
├── Update
└── Delete

Users
├── Register
├── Login
├── List
├── List usernames
├── Get user
├── Update
└── Delete

Add-ons
├── Create
├── Get by menu
├── Update
└── Delete

Orders
├── Create
├── Multiple menu items
├── Quantities
├── Multiple add-ons
├── Special instructions
├── Price calculation
├── My orders
├── Single order
├── Ownership protection
├── Cancellation
└── Admin status updates
```

---

# 🧪 Example Test Data

## Menu

```json
[
  {
    "menu_name": "Classic Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 29
  },
  {
    "menu_name": "Thick Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 29
  },
  {
    "menu_name": "Caramel Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 39
  },
  {
    "menu_name": "Hazelnut Cold Coffee",
    "menu_category": "Cold Coffee",
    "menu_price": 39
  },
  {
    "menu_name": "Oreo Shake",
    "menu_category": "Shakes",
    "menu_price": 39
  },
  {
    "menu_name": "Kitkat Shake",
    "menu_category": "Shakes",
    "menu_price": 45
  },
  {
    "menu_name": "Chocolate Shake",
    "menu_category": "Shakes",
    "menu_price": 39
  },
  {
    "menu_name": "Cheese Chutney",
    "menu_category": "Sandwich",
    "menu_price": 60
  },
  {
    "menu_name": "Chipotle Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 80
  },
  {
    "menu_name": "Veg Tandoori Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 75
  },
  {
    "menu_name": "Zatka Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 70
  },
  {
    "menu_name": "Nutella Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 90
  },
  {
    "menu_name": "Club Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 120
  },
  {
    "menu_name": "Chilli Garlic Sandwich",
    "menu_category": "Sandwich",
    "menu_price": 80
  }
]
```

---

## Add-ons

```json
[
  {
    "menu_id": 1,
    "name": "Chocolate Crush",
    "price": 7
  },
  {
    "menu_id": 1,
    "name": "Extra Cream",
    "price": 10
  },
  {
    "menu_id": 13,
    "name": "Extra Cheese",
    "price": 10
  },
  {
    "menu_id": 13,
    "name": "Extra Sauce",
    "price": 5
  }
]
```

---

## User

```json
{
  "username": "rahul",
  "email": "rahul@example.com",
  "password": "test123456"
}
```

---

# 🧹 Database Behavior

On application startup, SQLModel creates missing tables using:

```python
SQLModel.metadata.create_all(engine)
```

This is useful during development.

Important:

`create_all()` creates missing tables but does **not** perform full
schema migrations on existing tables.

For production schema changes, use a migration tool such as Alembic.

---

# 💵 Money and Prices

The current implementation uses numeric price fields and calculates
totals on the backend.

For a production payment system, consider replacing floating-point
monetary calculations with:

- `Decimal`
- integer paise/cents
- or a dedicated money representation

For example:

```text
₹36
```

could internally be stored as:

```text
3600 paise
```

This avoids floating-point precision problems.

---

# 🛡 Current Security Notes

The current development version intentionally keeps authentication
simple.

Current:

```text
Admin → API key
User  → generated secret key
```

Passwords and user secret keys are currently stored directly in the
database.

For production, improve this by implementing:

```text
Password hashing
      ↓
bcrypt / Argon2

User authentication
      ↓
JWT / secure session token

Secrets
      ↓
Hash or securely rotate them

Admin authentication
      ↓
Strong secret + proper authorization
```

Never expose production secrets inside:

- Git repositories
- frontend source code
- screenshots
- README files
- public API documentation

---

# 🔮 Future Improvements

Possible next improvements:

## Authentication

- Password hashing with Argon2/bcrypt
- JWT authentication
- Refresh tokens
- Token expiration
- Logout/revocation
- Role-based authorization

## Database

- PostgreSQL for production
- Alembic migrations
- Better indexing
- Connection pooling

## Orders

- Order timestamps such as `updated_at`
- Delivery information
- Payment status
- Payment gateway integration
- Order receipts/invoices
- Order history filters
- Admin order listing
- Order search
- More detailed status-transition validation

## Menu

- Availability/out-of-stock status
- Images
- Descriptions
- Featured items
- Ratings/reviews

## Add-ons

- Add-on availability
- Maximum quantity
- Add-on categories
- Paid customization rules

## API

- Pagination everywhere
- Rate limiting
- CORS configuration
- Structured logging
- Better exception handling
- Automated tests with pytest
- CI/CD
- Docker
- Production deployment

---

# 🐳 Docker Deployment

A future production deployment can use:

```text
Docker
   ↓
FastAPI
   ↓
Uvicorn/Gunicorn
   ↓
PostgreSQL
   ↓
Nginx
```

A typical production architecture could be:

```text
Client
  ↓
Nginx
  ↓
FastAPI
  ↓
SQLModel
  ↓
PostgreSQL
```

---

# 📈 Production Scaling

For a larger application:

```text
                    Load Balancer
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
           FastAPI    FastAPI    FastAPI
              │          │          │
              └──────────┼──────────┘
                         ↓
                    PostgreSQL
```

Additional infrastructure can include:

- Redis
- Background workers
- Message queues
- CDN
- Object storage
- Monitoring
- Centralized logging

SQLite is excellent for development and small deployments, but a
production system with substantial concurrent traffic should generally
use a production database such as PostgreSQL.

---

# 🧪 Recommended Testing Order

When testing from a clean database:

```text
1. Start application
2. Create admin secret
3. Create menu items
4. Test menu GET endpoints
5. Register user
6. Login
7. Create add-ons
8. Verify add-ons
9. Create order
10. Verify database
11. Get my orders
12. Get specific order
13. Test user ownership
14. Cancel pending order
15. Create another order
16. Update order status
17. Test delivered-order cancellation
18. Test remaining CRUD endpoints
19. Perform final database check
```

---

# 📊 Example Successful Test State

A successful development test can result in:

```text
Menu items:
14 initially

Users:
2 test users

Add-ons:
4 initially

Orders:
Order #1 → ₹36 → canceled
Order #2 → ₹222 → delivered
```

The order system therefore demonstrates:

```text
Menu
  ↓
Add-on
  ↓
User
  ↓
Order
  ↓
Order Item
  ↓
Order Add-on
```

---

# 🧠 API Design Principles Used

The project follows several important backend principles.

### 1. Client does not decide the final price

The backend fetches:

```text
Menu price
Add-on price
```

from the database.

---

### 2. User ID is not trusted from the request

Instead:

```text
X-User-Secret
      ↓
authenticated user
      ↓
user_id
```

---

### 3. Orders are not deleted when canceled

Cancellation changes:

```text
pending → canceled
```

This preserves order history.

---

### 4. Historical prices are preserved

Order items store their own:

```text
menu_name
price
```

and order add-ons store:

```text
addon_name
price
```

This prevents future menu-price changes from altering historical orders.

---

### 5. Ownership is enforced

Users can only access orders belonging to themselves.

---

# 📌 API Quick Reference

```text
MENU
POST   /menu/admin/create
POST   /menu/admin/create/bulk
GET    /menu/list
GET    /menu/filter
GET    /menu/list/names
GET    /menu/list/categories
GET    /menu/list/price
GET    /menu/filter/price
PATCH  /menu/admin/update/{menu_id}
DELETE /menu/admin/delete/{menu_id}


USERS
POST   /users/register
POST   /users/login
PATCH  /users/update

ADMIN USERS
GET    /users/admin/list
GET    /users/admin/list/usernames
GET    /users/admin/{user_id}
DELETE /users/admin/delete/{user_id}


ADD-ONS
POST   /addons/admin/create
GET    /addons/menu/{menu_id}
PATCH  /addons/admin/update/{addon_id}
DELETE /addons/admin/delete/{addon_id}


ORDERS
POST   /orders/create
GET    /orders/my-orders
GET    /orders/{order_id}
PATCH  /orders/{order_id}/cancel

ADMIN ORDERS
PATCH  /orders/admin/{order_id}/status
```

---

# 🏁 Project Status

**The Seventh Sip Backend API --- Core Version**

```text
Backend API              ✅
FastAPI                  ✅
SQLModel                 ✅
SQLite                   ✅
Menu Management          ✅
User Management          ✅
Admin Authentication     ✅
User Authentication      ✅
Add-on Management        ✅
Order Creation           ✅
Order Customization      ✅
Order Add-ons            ✅
Price Calculation        ✅
Order History            ✅
Order Cancellation       ✅
Order Ownership          ✅
Order Status Management  ✅
Swagger Documentation    ✅
End-to-End Testing       ✅
```

---

# 👨‍💻 Author

**Yashodeep**

GitHub:

`https://github.com/codewithyasho`

Portfolio:

`https://yashodeep.me/`

---

## ⭐ If you find this project useful

Give the repository a star ⭐ and feel free to explore, fork, and
improve the project.

---

**The Seventh Sip --- Backend API**

Built with Python, FastAPI and SQLModel. ☕🚀
