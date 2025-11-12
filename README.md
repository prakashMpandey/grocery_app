# Grocery App Backend

This is the **backend service** for the Grocery App, built using **FastAPI**.  
It handles:

- User authentication with role-based access (Manager / Customer)
- Product management
- Wishlists
- Cart management
- Sales reports (for managers)
- A simple discount system
 - The backend is **deployed on Render**:  
[https://grocery-app-k42u.onrender.com](https://grocery-app-k42u.onrender.com)

> **Note:** The above link can be used to access the APIs directly.

---

## Tech Stack

- **Python** – Main programming language  
- **FastAPI** – Web framework  
- **PostgreSQL** – Database  

---

## Database Diagram

![Database Diagram](./db_diagram.png)

---

## Features

### 1. User Authentication

- **Signup**
  - Users can signup using email, username, role (manager or customer), and password.
  - Passwords are hashed using **HS256** before storing in the database.
  - Customers can browse products, manage wishlists, and use the cart.
  - Managers can do everything a customer can plus manage products and view sales reports.

- **Login**
  - Users can login using email/username and password.
  - Validations are performed using **pwdlib** and **JWT**.
  - A JWT access token is generated and sent as a cookie.

- **Logout**
  - Verifies if the user is logged in.
  - Clears the JWT access token from the cookies.

---

### 2. Product Management

#### Customer Access
- **Get all products (Login required)**
  - Browse products with pagination.
  - Apply filters:
    - **Category:** e.g., dairy, grains.
    - **Most popular:** Returns the most popular products in the category (if specified).

- **Get single product (Login required)**
  - Retrieve product details by `product_id`.

#### Manager Access
- **Add product**
  - Add product details: `name`, `category`, `product_image`, `stock_count`, `unit_price`.
  - Product images are uploaded to **Cloudinary**, and URLs are stored in the database.

- **Delete product**
  - Delete product by `product_id`.

- **Update product**
  - Update product details by `product_id`.

---

### 3. Wishlist

- **Create/Delete Wishlist**
  - Users can create multiple wishlists with unique names.
  - Delete a wishlist using `wishlist_id`.
  - Retrieve all wishlists for the user.

- **Add/Delete Wishlist Items**
  - Add products to any wishlist using `wishlist_id`.
  - Remove products by `wishlist_item_id`.

---

### 4. Cart

- Each user has a single cart.
- **Add to Cart**
  - Requires `product_id` and `quantity`.
- **Delete from Cart**
  - Requires `cart_item_id`.

---

### 5. Checkout

- Returns a **bill summary** for all items in the cart.
- Calculates **total bill** by summing all cart items.
- Optional **coupon code** can be applied for discounts.
- Final amount = total bill - discount.
 > Note: Checkout only calculates the bill. Order placement is not implemented as it wasn’t specified in the assignment. The purchase date shown is only for billing purposes.

---

### 6. Sales Report (Manager Only)

- Manager can view complete sales reports: product name, quantity sold, number of orders.
- Filters:
  - **Most Sold:** Sorts from most sold to least sold.
  - **Category:** Filter by product category.



---

### 7. Simple Discount System

- Users can apply a **coupon code** at checkout.
- Coupon validation checks expiry date.
- If valid, discount is applied to the total bill.
- Manager routes for coupons:
  - Add coupon
  - Delete coupon
  - Get all coupons

---

## Demo Credentials


- **Customer:**  
  - Username: `ruhi`  
  - Password: `12345678`  

- **Manager:**  
  - Username: `manager`  
  - Password: `12345678`

    

> Use the above credentials to test the API.

  The backend is **deployed on Render**:  
[https://grocery-app-k42u.onrender.com](https://grocery-app-k42u.onrender.com)

> **Note:** The above link can be used to access the APIs directly.
---

## API Routes



### Root
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Health check endpoint. Returns a simple JSON to confirm API is live. |

---

### Auth Routes
| Method | Endpoint          | Description |
|--------|-----------------|-------------|
| POST   | `/auth/signup`   | Register a new user. Requires `email`, `username`, `password`, and `role` (customer/manager). |
| POST   | `/auth/login`    | Login user using `email/username` and `password`. Returns JWT access token in cookies. |
| POST   | `/auth/logout`   | Logout user and clears JWT token from cookies. |

---

### Product Routes

#### Customer Access
| Method | Endpoint                  | Description |
|--------|---------------------------|-------------|
| GET    | `/products`               | Get all products. Supports pagination (`page`, `limit`) and filters (`category`, `most_popular`). |
| GET    | `/product/{product_id}`   | Get single product details by `product_id`. |

#### Manager Access
| Method | Endpoint                        | Description |
|--------|---------------------------------|-------------|
| POST   | `/products`                     | Add a new product. Requires `product_name`, `stock_count`, `unit_price`, `category`, and `file` (image). |
| POST   | `/products/{product_id}`        | Update product details. Requires product fields in JSON body. |
| DELETE | `/products/{product_id}`        | Delete product by `product_id`. |

---

### Wishlist Routes
| Method | Endpoint                                  | Description |
|--------|------------------------------------------|-------------|
| GET    | `/wishlists`                              | Get all wishlists of the logged-in user. |
| POST   | `/wishlists`                              | Create a new wishlist. Requires `name`. |
| DELETE | `/wishlist/{wishlist_id}`                 | Delete wishlist by `wishlist_id`. |
| POST   | `/wishlist/{wishlist_id}/item`           | Add a product to a wishlist. Requires `product_id` in body. |
| GET    | `/wishlist/{wishlist_id}/items`          | Get all items in a specific wishlist. |
| DELETE | `/wishlist/item/{item_id}`               | Remove a product from wishlist by `item_id`. |

---

### Cart Routes
| Method | Endpoint                | Description |
|--------|------------------------|-------------|
| GET    | `/cart`                 | Get all items in the user's cart. |
| POST   | `/cart`                 | Add a product to cart. Requires `product_id` and `quantity`. |
| DELETE | `/cart/{cartItemId}`    | Delete an item from the cart by `cartItemId`. |

---

### Checkout
| Method | Endpoint     | Description |
|--------|-------------|-------------|
| POST   | `/checkout` | Calculates the bill for all cart items. Optional `couponCode` can be applied for discount. Returns `total_amount`, `discount_amount`, and itemized bill. |

---

### Sales Report (Manager Only)
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET    | `/sales` | Generate sales report. Optional query parameters: `most_sold` (boolean), `category` (string). Returns product sales statistics. |

---

### Coupon Routes (Manager Only)
| Method | Endpoint               | Description |
|--------|-----------------------|-------------|
| POST   | `/coupon`             | Add a new coupon. Requires coupon details in JSON body. |
| DELETE | `/coupon/{coupon_id}` | Delete a coupon by `coupon_id`. |
