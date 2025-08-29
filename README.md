# Vendoro - Virtual Marketplace

## Scope
Vendoro is a virtual marketplace that connects buyers and sellers, allowing users to browse, purchase, and sell products in a user-friendly environment. The platform supports user registration, product listings, order management, and reviews.

---

## User Stories with Acceptance Criteria


### 👤 Buyer User Stories

---

#### 1. As a **buyer**, I can **register and create a profile** so that **I can browse and purchase products**.

**Acceptance criteria:**
- Buyer can sign up using email and password.
- Buyer profile is automatically created upon registration.
- Buyer can log in and log out.
- Buyer can update profile details (name, address, etc.).

---

#### 2. As a **buyer**, I can **view product listings with filters and categories** so that **I can find what I’m looking for easily**.

**Acceptance criteria:**
- Buyer can view all products in a list/grid.
- Buyer can filter by category, price range, seller, or rating.
- Buyer can search by product name or keyword.
- Buyer can sort results by price or popularity.

---

### 3. As a **buyer**, I can **add products to a wishlist** so that **I can save items I'm interested in**.

**Acceptance criteria:**
- Buyer can click a "Save" or "Wishlist" button on product listings.
- Wishlist items are stored and visible in the buyer's profile.
- Buyer can remove items from wishlist.

---

#### 4. As a **buyer**, I can **favorite sellers** so that **I can keep up with their new products**.

**Acceptance criteria:**
- Buyer can favorite/unfavorite a seller from their shop page.
- Favorite sellers appear in the buyer's profile.
- Buyer can see a feed of new products from favorited sellers.

---

#### 5. As a **buyer**, I can **view my current and past orders** so that **I can track my purchases**.

**Acceptance criteria:**
- Order history is available from the buyer dashboard.
- Each order shows status, total, product info, and date.
- Buyer can track delivery status if applicable.

---

#### 6. As a **buyer**, I can **leave reviews and ratings for products** so that **I can help other buyers**.

**Acceptance criteria:**
- Buyer can only review products they have purchased.
- Reviews include star rating and optional text.
- Reviews are publicly visible on product pages.
- Buyer can edit or delete their own reviews.

---

#### 7. As a **buyer**, I can **receive notifications about order status and promotions** so that **I stay informed**.

**Acceptance criteria:**
- Buyer receives email notifications for order confirmations and shipping updates.
- Buyer can opt-in/out of promotional emails.
- Notifications are timely and relevant.

---

#### 8. As a **buyer**, I can **view what products are hot and trending** so that **I can view and purchase items under demand**.

**Acceptance criteria:**
- Buyer can see a "Trending Products" section on the homepage.
- Trending products are determined by sales volume and ratings.
- Buyer can click on trending products to view details and purchase.


### 🛍️ Seller User Stories

---

#### 1. As a **seller**, I can **register and create a shop profile** so that **I can sell products**.

**Acceptance criteria:**
- Seller can register to become a seller through an application form.
- Upon approval, a seller profile and shop are created.
- Seller can add shop name, description, and contact details.

---

#### 2. As a **seller**, I can **customize the appearance of my shop** so that **it reflects my brand**.

**Acceptance criteria:**
- Seller can select colors, layout, and upload a banner image.
- Customizations are reflected on the public-facing shop page.
- Changes are saved and persist across sessions.

---

#### 3. As a **seller**, I can **add, edit, and delete product listings** so that **I can manage my inventory**.

**Acceptance criteria:**
- Seller can access a dashboard listing their products.
- Seller can create new products with name, description, price, and image.
- Seller can edit and delete their own products.
- Product form includes validations (e.g. price must be > 0).

---

#### 4. As a **seller**, I can **upload product images and set prices** so that **my listings are attractive and accurate**.

**Acceptance criteria:**
- Product listing supports image uploads.
- Product price and inventory fields are required.
- Images are displayed on the product detail page.

---

#### 5. As a **seller**, I can **see active and inactive products** so that **I can control what’s visible**.

**Acceptance criteria:**
- Seller dashboard shows active/inactive status for each product.
- Seller can toggle product visibility (is_active).
- Inactive products are hidden from buyers but visible to the seller.

---

#### 6. As a **seller**, I can **view order notifications** so that **I can fulfill them promptly**.

**Acceptance criteria:**
- Seller receives notification when a new order is placed.
- Orders include product, quantity, and buyer contact info.
- Seller dashboard includes a list of open and fulfilled orders.

---

#### 7. As a **seller**, I can **view my product market statistics** so that **I can monitor my marketplace activity**.

**Acceptance criteria:**
- Seller dashboard includes metrics (user counts, total sales, active products).
- Charts or tables show trends over time (optional).
- Data updates in near real-time.

---


### 🛠️ Admin User Stories

---

#### 1. As an **admin**, I can **manage user accounts** so that **I can maintain platform integrity**.

**Acceptance criteria:**
- Admin dashboard lists all users with search and filter options.
- Admin can deactivate, reactivate, or delete accounts.
- Admin can view account details and recent activity.

---

#### 2. As an **admin**, I can **approve or reject seller applications** so that **only verified users can sell**.

**Acceptance criteria:**
- Admin sees a list of pending seller applications.
- Admin can view application details and approve/reject.
- Approved users gain seller access; rejected users receive a notification.

---

#### 3. As an **admin**, I can **moderate product listings and reviews** so that **they meet community guidelines**.

**Acceptance criteria:**
- Admin can view all products and reviews site-wide.
- Admin can flag, edit, or delete inappropriate content.
- Admin actions are logged with timestamp and reason.

---

#### 4. As an **admin**, I can **view site-wide statistics** so that **I can monitor marketplace activity**.

**Acceptance criteria:**
- Admin dashboard includes metrics (user counts, total sales, active products).
- Charts or tables show trends over time (optional).
- Data updates in near real-time.

---

#### 5. As an **admin**, I can **manage reports of abuse or fraud** so that **I can take corrective action**.

**Acceptance criteria:**
- Admin can view reported users, products, or reviews.
- Reports include reporter message, timestamp, and target.
- Admin can take action (warn, suspend, ban).

---
