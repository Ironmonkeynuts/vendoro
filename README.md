# [![screenshot](documentation/vendoro.png)](https://imn-vendoro-55af0b986025.herokuapp.com)

Developer: David Doyle-Owen ([Ironmonkeynuts](https://www.github.com/Ironmonkeynuts))

[![GitHub commit activity](https://img.shields.io/github/commit-activity/t/Ironmonkeynuts/vendoro)](https://www.github.com/Ironmonkeynuts/vendoro/commits/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/Ironmonkeynuts/vendoro)](https://www.github.com/Ironmonkeynuts/vendoro/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/Ironmonkeynuts/vendoro)](https://www.github.com/Ironmonkeynuts/vendoro)
[![badge](https://img.shields.io/badge/deployment-Heroku-purple)](https://imn-vendoro-55af0b986025.herokuapp.com)

## Project Introduction & Rationale
Vendoro is a lightweight, modern marketplace web application that helps small retailers and indie makers sell products online without the overhead of a full-blown e-commerce suite. The project aims to make listing, managing, and analysing product performance simple for shop owners, while offering shoppers a clean, trustworthy browsing and checkout experience. At its core, Vendoro removes busywork—so sellers can focus on their products, not their tooling.

Today, many small sellers bounce between spreadsheets, social media DMs, and heavyweight platforms that are either too limited or too complex. Vendoro bridges that gap with a focused feature set: shop and product management, image handling, inventory tracking, customer reviews with replies, and a seller dashboard that surfaces sales, revenue, and review trends over time. It’s opinionated where it matters (clear flows, sensible defaults) and flexible where it counts (multi-shop support, CSV exports, and range-based reporting).

The primary audience is independent sellers and small shops—people who need professional tooling but don’t have a dedicated tech team. For them, Vendoro provides:

An easy way to create a branded shop and add products quickly.

Built-in reviews that foster trust and drive conversions.

A dashboard with KPIs (orders, items sold, revenue, AOV, new reviews) and time-range reports to make data-driven decisions.

CSV exports for accounting, fulfilment, or deeper analysis.

Vendoro will be useful to sellers because it eliminates friction at every step: creating a shop, uploading images, tracking stock, responding to reviews, and understanding performance without leaving the app. By exposing clear KPIs and time-series trends, it turns raw transactions into insight—highlighting best-sellers, underperformers, and seasonal patterns. This clarity supports decisions like re-stocking, pricing adjustments, or targeted promotions.

### Rationale — Why this project?

I chose this topic because marketplaces sit at the intersection of product design, data modelling, security, and real business value. Building Vendoro lets me explore challenges that matter in the real world: ensuring unique, human-friendly URLs; handling user-generated content and moderation; protecting owner-only actions; integrating third-party services like Stripe and Cloudinary; and presenting analytics that are accurate, explainable, and fast. It’s a rich, end-to-end problem space that tests architectural judgment, not just CRUD.

There’s also a clear needs gap: many small sellers either outgrow simple link-in-bio tools or feel overwhelmed by enterprise platforms. I wanted to create something approachable that still feels “professional”—the kind of tool a solo shop can adopt in an afternoon and keep using as they grow.

Finally, the project is a great vehicle for personal learning goals: strengthening Django best practices; refining UX for data-heavy screens; implementing secure auth flows with email verification and password reset; and practicing performance-minded ORM usage (aggregations, annotations, and selective prefetching). The end result is both a useful product for non-technical users and a portfolio-quality codebase that demonstrates thoughtful engineering.

In short, Vendoro is my attempt to build the right-sized marketplace: powerful enough to run a small business, simple enough to love using, and robust enough to be a credible foundation for future features like coupons, shipping labels, or vendor-to-vendor collaborations.

![screenshot](documentation/mockup.png)

source: [vendoro amiresponsive](https://ui.dev/amiresponsive?url=https://imn-vendoro-55af0b986025.herokuapp.com)

> [!IMPORTANT]  
> The examples in these templates are strongly influenced by the Code Institute walkthrough project called "Boutique Ado".

## UX

### The 5 Planes of UX

#### 1. Strategy

**Purpose**
- Provide a seamless and intuitive e-commerce experience for customers to browse, filter, and purchase products.
- Empower shop owners to manage their shop's inventory and customer orders efficiently.

**Primary User Needs**
- Guest users need to browse products and checkout with ease.
- Registered customers need a streamlined shopping experience with account and order history features.
- Shop owners need robust tools for inventory and order management.

**Business Goals**
- Drive sales by providing a user-friendly shopping experience.
- Build customer loyalty through personalized and efficient account features.
- Maintain an organized and up-to-date shop inventory.

#### 2. Scope

**[Features](#features)** (see below)

**Content Requirements**
- Product details, including name, price, description, category, and images.
- Clear prompts and instructions for browsing, filtering, and purchasing.
- Order details, confirmation pages, and email notifications.
- Secure payment processing using Stripe.
- Payment success emails sent to users.
- 404 page for lost users.

#### 3. Structure

**Information Architecture**
- **Navigation Menu**:
  - Links to Home, Products, Cart, Newsletter, and Account sections.
- **Hierarchy**:
  - Prominent product categories and filters for easy navigation.
  - Cart and checkout options displayed prominently for convenience.

**User Flow**
1. Guest user browses the store → filters and sorts products by category, price, or name.
2. Guest user adds items to the cart → proceeds to checkout.
3. Guest user creates an account or logs in during checkout → completes purchase.
4. Returning customers log in → view past orders and track purchase history.
5. Site owners manage inventory → add, update, or delete products and categories.
6. Users signup to the newsletter → potentially receive advanced notice of upcoming sales.

#### 4. Skeleton

**[Wireframes](#wireframes)** (see below)

#### 5. Surface

**Visual Design Elements**
- **[Colours](#colour-scheme)** (see below)
- **[Typography](#typography)** (see below)

### Colour Scheme

⚠️INSTRUCTIONS ⚠️

Explain your colors and color scheme. Consider adding a link and screenshot for your color scheme using [coolors](https://coolors.co/generate).

When you add a color to the palette, the URL is dynamically updated, making it easier for you to return back to your color palette later if needed. See example below:

⚠️ --- END --- ⚠️

I used [coolors.co](https://coolors.co/212529-6c757d-0d6efd-f8f9fa-ffffff) to generate my color palette.

- `#212529` primary text.
- `#6c757d` muted text.
- `#FFFFFF` buttons, navbar and hero section text.
- `#0d6efd` alt text and button background.
- `#f8f9fa` primary background.
- `#212529` navbar background.
- `#FFFFFF` welcome panel.

![screenshot](documentation/palette.png)

### Typography

Using Bootstrap 5.3.3 default system stack.

- Body + headings + buttons + forms all inherit:
  - system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif, ...emoji fallbacks


## Wireframes

To follow best practice, wireframes were developed for mobile, tablet, and desktop sizes.
I've used [Balsamiq](https://balsamiq.com/wireframes) to design my site wireframes.

| Page | Mobile | Tablet | Desktop |
| --- | --- | --- | --- |
| Register | ![screenshot](documentation/wireframes/register-mobile.png) | ![screenshot](documentation/wireframes/register-tablet.png) | ![screenshot](documentation/wireframes/register-desktop.png) |
| Login | ![screenshot](documentation/wireframes/login-mobile.png) | ![screenshot](documentation/wireframes/login-tablet.png) | ![screenshot](documentation/wireframes/login-desktop.png) |
| Profile | ![screenshot](documentation/wireframes/profile-mobile.png) | ![screenshot](documentation/wireframes/profile-tablet.png) | ![screenshot](documentation/wireframes/profile-desktop.png) |
| Home | ![screenshot](documentation/wireframes/home-mobile.png) | ![screenshot](documentation/wireframes/home-tablet.png) | ![screenshot](documentation/wireframes/home-desktop.png) |
| Product Lists | ![screenshot](documentation/wireframes/browse-mobile.png) | ![screenshot](documentation/wireframes/browse-tablet.png) | ![screenshot](documentation/wireframes/browse-desktop.png) |
| Product Details | ![screenshot](documentation/wireframes/product-mobile.png) | ![screenshot](documentation/wireframes/product-tablet.png) | ![screenshot](documentation/wireframes/product-desktop.png) |
| Cart | ![screenshot](documentation/wireframes/cart-mobile.png) | ![screenshot](documentation/wireframes/cart-tablet.png) | ![screenshot](documentation/wireframes/cart-desktop.png) |
| Checkout | ![screenshot](documentation/wireframes/checkout-mobile.png) | ![screenshot](documentation/wireframes/checkout-tablet.png) | ![screenshot](documentation/wireframes/checkout-desktop.png) |
| Checkout Success | ![screenshot](documentation/wireframes/checkout-success-mobile.png) | ![screenshot](documentation/wireframes/checkout-success-tablet.png) | ![screenshot](documentation/wireframes/checkout-success-desktop.png) |
| Order History | ![screenshot](documentation/wireframes/order-history-mobile.png) | ![screenshot](documentation/wireframes/order-history-tablet.png) | ![screenshot](documentation/wireframes/order-history-desktop.png) |
| Shop View | ![screenshot](documentation/wireframes/shop-mobile.png) | ![screenshot](documentation/wireframes/shop-tablet.png) | ![screenshot](documentation/wireframes/shop-desktop.png) |
| Shop Settings | ![screenshot](documentation/wireframes/shop-settings-mobile.png) | ![screenshot](documentation/wireframes/shop-settings-tablet.png) | ![screenshot](documentation/wireframes/shop-settings-desktop.png) |
| Add Product | ![screenshot](documentation/wireframes/add-product-mobile.png) | ![screenshot](documentation/wireframes/add-product-tablet.png) | ![screenshot](documentation/wireframes/add-product-desktop.png) |
| Edit Product | ![screenshot](documentation/wireframes/edit-product-mobile.png) | ![screenshot](documentation/wireframes/edit-product-tablet.png) | ![screenshot](documentation/wireframes/edit-product-desktop.png) |
| Seller Inventory | ![screenshot](documentation/wireframes/seller-inventory-mobile.png) | ![screenshot](documentation/wireframes/seller-inventory-tablet.png) | ![screenshot](documentation/wireframes/seller-inventory-desktop.png) |
| Seller Orders | ![screenshot](documentation/wireframes/seller-orders-mobile.png) | ![screenshot](documentation/wireframes/seller-orders-tablet.png) | ![screenshot](documentation/wireframes/seller-orders-desktop.png) |
| Seller Alerts | ![screenshot](documentation/wireframes/seller-alerts-mobile.png) | ![screenshot](documentation/wireframes/seller-alerts-tablet.png) | ![screenshot](documentation/wireframes/seller-alerts-desktop.png) |
| Seller Stats | ![screenshot](documentation/wireframes/seller-stats-mobile.png) | ![screenshot](documentation/wireframes/seller-stats-tablet.png) | ![screenshot](documentation/wireframes/seller-stats-desktop.png) |
| Admin Users | ![screenshot](documentation/wireframes/admin-users-mobile.png) | ![screenshot](documentation/wireframes/admin-users-tablet.png) | ![screenshot](documentation/wireframes/admin-users-desktop.png) |
| Admin Orders | ![screenshot](documentation/wireframes/admin-orders-mobile.png) | ![screenshot](documentation/wireframes/admin-orders-tablet.png) | ![screenshot](documentation/wireframes/admin-orders-desktop.png) |
| Admin Reviews | ![screenshot](documentation/wireframes/admin-reviews-mobile.png) | ![screenshot](documentation/wireframes/admin-reviews-tablet.png) | ![screenshot](documentation/wireframes/admin-reviews-desktop.png) |
| Admin Shops & Products | ![screenshot](documentation/wireframes/admin-shops&products-mobile.png) | ![screenshot](documentation/wireframes/admin-shops&products-tablet.png) | ![screenshot](documentation/wireframes/admin-shops&products-desktop.png) |
| Contact | ![screenshot](documentation/wireframes/contact-mobile.png) | ![screenshot](documentation/wireframes/contact-tablet.png) | ![screenshot](documentation/wireframes/contact-desktop.png) |
| Newsletter Subscription | ![screenshot](documentation/wireframes/subscription-mobile.png) | ![screenshot](documentation/wireframes/subscription-tablet.png) | ![screenshot](documentation/wireframes/subscription-desktop.png) |
| 404 | ![screenshot](documentation/wireframes/404-mobile.png) | ![screenshot](documentation/wireframes/404-tablet.png) | ![screenshot](documentation/wireframes/404-desktop.png) |

## User Stories

| Target | Expectation | Outcome |
| --- | --- | --- |
| As a guest user | I would like to browse products without needing to register | so that I can shop freely before deciding to create an account. |
| As a guest user | I would like to be prompted to create an account or log in at checkout | so that I can complete my purchase and track my order history. |
| As a user | I would like to sign up to the site's newsletter | so that I can stay up to date with any upcoming sales or promotions. |
| As a user | I would like to see a 404 error page if I get lost | so that it's obvious that I've stumbled upon a page that doesn't exist. |
| As a customer | I would like to browse various product categories (clothing, toys, jewelry, kitchen gadgets, etc.) | so that I can easily find what I'm looking for. |
| As a customer | I would like to sort products by price (low-to-high/high-to-low) and name (alphabetical) | so that I can quickly organize items in a way that suits my shopping style. |
| As a customer | I would like to filter products by category | so that I can narrow down the products to the types I am most interested in. |
| As a customer | I would like to click on individual products to view more details (description, price, image, etc.) | so that I can make an informed decision about my purchase. |
| As a customer | I would like to add items to my shopping cart using quantity increment/decrement buttons | so that I can adjust how many units of a product I want before checkout. |
| As a customer | I would like to view and manage my shopping cart | so that I can review, add, or remove items before proceeding to checkout. |
| As a customer | I would like to adjust the quantity of items in my cart | so that I can modify my purchase preferences without leaving the cart. |
| As a customer | I would like to remove items from my cart | so that I can remove products I no longer wish to buy. |
| As a customer | I would like to proceed to checkout where I see my cart items, grand total, and input my name, email, shipping address, and card details | so that I can complete my purchase. |
| As a customer | I would like to receive a confirmation email after my purchase | so that I can have a record of my transaction and order details. |
| As a customer | I would like to see an order confirmation page with a checkout order number after completing my purchase | so that I know my order has been successfully placed. |
| As a customer | I would like to securely enter my card details using Stripe at checkout | so that I can feel confident my payment information is protected. |
| As a customer | I would like to add products to a wishlist | so that I can save items I'm interested in. |
| As a customer | I would like to favorite sellers | so that I can keep up with their new products. |
| As a customer | I would like to leave reviews and ratings for products | so that I can help other buyers. |    
| As a returning customer | I would like to be able to log in and view my past orders | so that I can track my previous purchases and order history. |
| As a returning customer | I would like the checkout process to remember my shipping address | so that future purchases are quicker and easier. |
| As a shop owner | I would like to create new products with a name, description, price, images, and category | so that I can add additional items to the store inventory. |
| As a shop owner | I would like to update product details (name, price, description, image, category) at any time | so that I can keep my product listings accurate and up to date. |
| As a shop owner | I would like to delete products that are no longer available or relevant | so that I can maintain a clean and accurate inventory. |
| As a shop owner | I would like to create a shop profile | so that I can sell products. |
| As a shop owner | I would like to customize the appearance of my shop | so that it reflects my brand. |
| As a shop owner | I would like to see active and inactive products | so that I can control what’s visible. |
| As a shop owner | I would like to view order notifications | so that I can fulfill them promptly. |
| As a shop owner | I would like to view my product market statistics | so that I can monitor my marketplace activity. |
| As a shop owner | I would like to view my shop inventory | so that I can view and modify my shop products. |
| As a shop owner | I would like to view alerts of recent orders and reviews | so that I can respond and improve my offerings. |
| As an admin | I would like to manage product categories | so that I can ensure items are correctly organized and easy for customers to find. |
| As an admin | I would like to manage user accounts | so that I can maintain platform integrity. |
| As an admin | I would like to moderate product listings and reviews | so that they meet community guidelines. |
| As an admin | I would like to view site-wide statistics | so that I can monitor marketplace activity for all shops. |
| As an admin | I would like to view orders made | so that I can monitor customer purcheses and shop responses. |
| As an admin | I would like to view reviews and replies | so that I can monitor customer comments and replies by shop owners. |

## Features

### Existing Features

| Feature | Notes | Screenshot |
| --- | --- | --- |
| Register | Authentication is handled by allauth, allowing users to register accounts. | ![screenshot](documentation/features/register.png) |
| Login | Authentication is handled by allauth, allowing users to log in to their existing accounts. | ![screenshot](documentation/features/login.png) |
| Logout | Authentication is handled by allauth, allowing users to log out of their accounts. | ![screenshot](documentation/features/logout.png) |
| Product List | Users can browse all available products with sorting, filtering by categories, and search functionality. | ![screenshot](documentation/features/browse.png) |
| Product Details | Displays detailed information about a selected product, including its name, description, price, an image, and available sizes. | ![screenshot](documentation/features/product-details.png) |
| Add to Cart | Users can add items to their shopping bag, with support for selecting different sizes if applicable. | ![screenshot](documentation/features/add-to-cart.png) |
| View Cart | Users can view the contents of their shopping bag, adjust quantities, or remove items. | ![screenshot](documentation/features/view-cart.png) |
| Checkout | Users can proceed to checkout, where they provide their delivery details and payment information using Stripe integration. | ![screenshot](documentation/features/checkout.png) |
| Order Confirmation | Users receive an on-screen and email confirmation with details of their purchase. | ![screenshot](documentation/features/order-confirmation.png) |
| Profile Management | Users can manage their profile information, including their default delivery address and order history. | ![screenshot](documentation/features/profile-management.png) |
| Order History | Users can view their past orders and access details of each order, including products purchased and the delivery status. | ![screenshot](documentation/features/order-history.png) |
| Product Management | Shop owners can add, edit, and delete products from the site via a CRUD interface. | ![screenshot](documentation/features/product-management.png) |
| Newsletter | Users can register their email address to receive newsletters from the site. Currently, this only stores the email in the database. | ![screenshot](documentation/features/newsletter.png) |
| Contact | Users can submit a message via the contact form, which stores their name, email, and message in the database. | ![screenshot](documentation/features/contact.png) |
| FAQs | Admins can manage frequently asked questions, which are displayed on the site for users. | ![screenshot](documentation/features/faqs.png) |
| User Feedback | Clear and concise Django messages are used to provide feedback to users when interacting with various features (e.g., adding products to the bag, checking out, etc.). | ![screenshot](documentation/features/user-feedback.png) |
| Heroku Deployment | The site is deployed to Heroku, making it accessible online for users. | ![screenshot](documentation/features/heroku.png) |
| SEO | SEO optimization with a sitemap.xml, robots.txt, and appropriate meta tags to improve search engine visibility. | ![screenshot](documentation/features/seo.png) |
| Marketing | Social media presence is available in the footer using external links, as well as a Facebook Marketplace wireframe in the README for future integrations. | ![screenshot](documentation/features/marketing.png) |
| 404 | The 404 error page will indicate when a user has navigated to a page that doesn't exist, replacing the default Heroku 404 page with one that ties into the site's look and feel. | ![screenshot](documentation/features/404.png) |

### Future Features

- **Product Reviews & Ratings**: Allow customers to leave reviews and rate products, with admin moderation. Display average ratings and review counts on product pages.
- **Wishlist Functionality**: Enable users to save products to a personal wishlist for future purchases. Notify users if wishlist items go on sale or are back in stock.
- **Product Recommendations**: Implement a "Customers who bought this also bought" or "You might also like" feature to suggest related products.
- **Live Chat Support**: Provide real-time customer support through an integrated live chat or chatbot.
- **Abandoned Cart Recovery**: Automatically send emails to users who add items to their cart but don't complete the purchase, offering discounts or reminders.
- **Discount Codes and Vouchers**: Allow the admin to create discount codes or vouchers for promotions and marketing campaigns.
- **Loyalty Program**: Introduce a points-based loyalty system where customers earn points for purchases, which can be redeemed for discounts.
- **Product Inventory Alerts**: Notify customers when out-of-stock items are back in stock, or when low inventory is approaching.
- **Multi-Currency and Multi-Language Support**: Expand the application to support multiple currencies and languages to reach a global audience.
- **Product Bundles**: Offer discounted product bundles (e.g., buy 3 for the price of 2) or custom product kits.
- **Social Media Integration**: Enable users to share products directly to social media platforms or implement a social login for quick account creation.
- **Shipping Tracking Integration**: Provide real-time shipping updates and tracking information directly within the user’s order history.
- **Advanced Analytics Dashboard for Admin**: Offer an in-depth dashboard that displays sales trends, popular products, customer behavior, and more.
- **Subscription-Based Products**: Allow users to subscribe to certain products (e.g., monthly deliveries of consumables like coffee or skincare products).
- **Product Video Demos**: Support product videos to better showcase features, especially for high-tech or complex items.
- **Mobile App**: Develop a mobile app for iOS and Android, providing users with a more optimized shopping experience on mobile devices.

## Tools & Technologies

| Tool / Tech | Use |
| --- | --- |
| [![badge](https://img.shields.io/badge/Markdown_Builder-grey?logo=markdown&logoColor=000000)](https://markdown.2bn.dev) | Generate README and TESTING templates. |
| [![badge](https://img.shields.io/badge/Git-grey?logo=git&logoColor=F05032)](https://git-scm.com) | Version control. (`git add`, `git commit`, `git push`) |
| [![badge](https://img.shields.io/badge/GitHub-grey?logo=github&logoColor=181717)](https://github.com) | Secure online code storage. |
| [![badge](https://img.shields.io/badge/VSCode-grey?logo=htmx&logoColor=007ACC)](https://code.visualstudio.com) | Local IDE for development. |
| [![badge](https://img.shields.io/badge/HTML-grey?logo=html5&logoColor=E34F26)](https://en.wikipedia.org/wiki/HTML) | Main site content and layout. |
| [![badge](https://img.shields.io/badge/CSS-grey?logo=css&logoColor=1572B6)](https://en.wikipedia.org/wiki/CSS) | Design and layout. |
| [![badge](https://img.shields.io/badge/JavaScript-grey?logo=javascript&logoColor=F7DF1E)](https://www.javascript.com) | User interaction on the site. |
| [![badge](https://img.shields.io/badge/Python-grey?logo=python&logoColor=3776AB)](https://www.python.org) | Back-end programming language. |
| [![badge](https://img.shields.io/badge/Heroku-grey?logo=heroku&logoColor=430098)](https://www.heroku.com) | Hosting the deployed back-end site. |
| [![badge](https://img.shields.io/badge/Bootstrap-grey?logo=bootstrap&logoColor=7952B3)](https://getbootstrap.com) | Front-end CSS framework for modern responsiveness and pre-built components. |
| [![badge](https://img.shields.io/badge/Django-grey?logo=django&logoColor=092E20)](https://www.djangoproject.com) | Python framework for the site. |
| [![badge](https://img.shields.io/badge/PostgreSQL-grey?logo=postgresql&logoColor=4169E1)](https://www.postgresql.org) | Relational database management. |
| [![badge](https://img.shields.io/badge/Cloudinary-grey?logo=cloudinary&logoColor=3448C5)](https://cloudinary.com) | Online static file storage. |
| [![badge](https://img.shields.io/badge/WhiteNoise-grey?logo=python&logoColor=FFFFFF)](https://whitenoise.readthedocs.io) | Serving static files with Heroku. |
| [![badge](https://img.shields.io/badge/Stripe-grey?logo=stripe&logoColor=008CDD)](https://stripe.com) | Online secure payments of e-commerce products/services. |
| [![badge](https://img.shields.io/badge/Gmail_API-grey?logo=gmail&logoColor=EA4335)](https://mail.google.com) | Sending emails in my application. |
| [![badge](https://img.shields.io/badge/Balsamiq-grey?logo=barmenia&logoColor=CE0908)](https://balsamiq.com/wireframes) | Creating wireframes. |
| [![badge](https://img.shields.io/badge/Font_Awesome-grey?logo=fontawesome&logoColor=528DD7)](https://fontawesome.com) | Icons. |
| [![badge](https://img.shields.io/badge/ChatGPT-grey?logo=openai&logoColor=75A99C)](https://chat.openai.com) | Help debug, troubleshoot, and explain things. |
| [![badge](https://img.shields.io/badge/Mermaid-grey?logo=mermaid&logoColor=FF3670)](https://mermaid.live) | Generate an interactive diagram for the data/schema. |
| [![badge](https://img.shields.io/badge/W3Schools-grey?logo=w3schools&logoColor=04AA6D)](https://www.w3schools.com) | Tutorials/Reference Guide |
| [![badge](https://img.shields.io/badge/StackOverflow-grey?logo=stackoverflow&logoColor=F58025)](https://stackoverflow.com) | Troubleshooting and Debugging |

## Database Design

### Data Model

Entity Relationship Diagrams (ERD) help to visualize database architecture before creating models. Understanding the relationships between different tables can save time later in the project.

![screenshot](documentation/erd.png)

I have used `Mermaid` to generate an interactive ERD of my project.

```mermaid
erDiagram
  USERS_USER {
    int id
    string username
    string email
    string user_type
  }

  USERS_BUYERPROFILE {
    int id
    int user_id
    string display_name
    string default_shipping_email
    string default_shipping_telephone
    text default_shipping_address1
    text default_shipping_address2
    string default_shipping_city
    string default_shipping_postcode
    string default_shipping_country
    boolean marketing_opt_in
    boolean billing_same_as_shipping
    string default_billing_email
    string default_billing_telephone
    text default_billing_address1
    text default_billing_address2
    string default_billing_city
    string default_billing_postcode
    string default_billing_country
  }

  USERS_SELLERPROFILE {
    int id
    int user_id
    string legal_name
    string tax_id
    string contact_email
    string contact_telephone
  }

  MARKETPLACE_SHOP {
    int id
    int owner_id
    string name
    string slug
    string tagline
    string primary_color
    string highlight_color
    string banner
    string legal_name_override
    string tax_id_override
    string contact_email_override
    string contact_telephone_override
  }

  MARKETPLACE_CATEGORY {
    int id
    string name
    string slug
  }

  MARKETPLACE_PRODUCT {
    int id
    int shop_id
    string title
    string slug
    text description
    int category_id
    decimal price
    boolean is_active
    datetime created_at
    datetime updated_at
  }

  MARKETPLACE_PRODUCTIMAGE {
    int id
    int product_id
    string image
    string alt_text
  }

  MARKETPLACE_INVENTORY {
    int id
    int product_id
    int quantity
    int low_stock_threshold
    datetime updated_at
  }

  MARKETPLACE_PRODUCTREVIEW {
    int id
    int product_id
    int user_id
    int rating
    text comment
    boolean is_public
    datetime created_at
  }

  MARKETPLACE_REVIEWREPLY {
    int id
    int review_id
    int responder_id
    text body
    datetime created_at
  }

  ORDERS_CART {
    int id
    int user_id
    boolean active
    datetime created_at
  }

  ORDERS_CARTITEM {
    int id
    int cart_id
    int product_id
    int quantity
  }

  ORDERS_ORDER {
    int id
    int user_id
    int shop_id
    decimal total_amount
    string status
    string fulfillment_status
    datetime created_at
    string stripe_checkout_session_id
    string stripe_payment_intent
  }

  ORDERS_ORDERITEM {
    int id
    int order_id
    int product_id
    decimal unit_price
    int quantity
  }

  HOME_NEWSLETTERSUBSCRIPTION {
    int id
    int user_id
    string email
    boolean is_active
    string token
    datetime created_at
    datetime updated_at
  }

  USERS_USER ||--o| USERS_BUYERPROFILE : has
  USERS_USER ||--o| USERS_SELLERPROFILE : has
  USERS_USER ||--o{ MARKETPLACE_SHOP : owns
  MARKETPLACE_SHOP ||--o{ MARKETPLACE_PRODUCT : lists
  MARKETPLACE_CATEGORY ||--o{ MARKETPLACE_PRODUCT : categorizes
  MARKETPLACE_PRODUCT ||--o{ MARKETPLACE_PRODUCTIMAGE : has
  MARKETPLACE_PRODUCT ||--|| MARKETPLACE_INVENTORY : has_one
  USERS_USER ||--o{ ORDERS_CART : has
  ORDERS_CART ||--o{ ORDERS_CARTITEM : contains
  MARKETPLACE_PRODUCT ||--o{ ORDERS_CARTITEM : in_carts
  USERS_USER ||--o{ ORDERS_ORDER : places
  MARKETPLACE_SHOP ||--o{ ORDERS_ORDER : receives
  ORDERS_ORDER ||--o{ ORDERS_ORDERITEM : includes
  MARKETPLACE_PRODUCT ||--o{ ORDERS_ORDERITEM : ordered_as
  USERS_USER ||--o{ MARKETPLACE_PRODUCTREVIEW : writes
  MARKETPLACE_PRODUCT ||--o{ MARKETPLACE_PRODUCTREVIEW : reviewed
  MARKETPLACE_PRODUCTREVIEW ||--|| MARKETPLACE_REVIEWREPLY : reply
  USERS_USER ||--o{ MARKETPLACE_REVIEWREPLY : responds
  USERS_USER ||--o{ HOME_NEWSLETTERSUBSCRIPTION : subscribes
```

source: [Mermaid](https://mermaid.live/edit#pako:eNqlWG1v2joU_itRPrOqBApdvjGabehCQYFu2hVSZBI3serYubbTlpX-92sHkubNKes-lAb7vD7n-DkOL6ZPA2jaJmQ3CIQMxFtiGHdrx1176tN4Ud8NAxFhoOD4zAVDJDRSDhkBMawswhgg3BDzxD7J5F635M3-l7tfjrtyl19nc6fNj3rOtGuOA8QTDPZew3kA70GKhccjlCRywWtG0xAREMMkouRkScBn0RQCQcAg5_0zZKxudz4S-26JhHKhavKOHZoSwU6mdpRiCIgRA_YAhdqmifAQqe7uEMZqj0vYPMALW62OcmE9grlEF4C5TAd-NRGr05cWvVygE7zCyht2lX5cO_P5hxoSwxDgZjsK8FyX9CkRwBctsOY7FThP4S0m7j_OZjWfTB1v_X250sVGn0gzuEZYHKdhLc5Q4lIVShiS3bSXWGHKKjsRCiMs_0TL3g4QGYEGG48-QsZQ0AZS-14FrW6RAraKWAt-08nG-bZ0f3UQmxaxFnOyW27uphtdRXhEk3pBBBJYV5HT0eA-Q4lAlLxZ8oGAIZUVya0F0JclwqpSPqyedMQ9iQl6PC0HUlWgGBo-g_Ix8ICobaRJUNrQpzlbTL5pT0bCaJDKUtTSlUGG1XQBVvV61vma3f5wbjeaErU5Umv_pYCIgh3UCqZPHhfUf_BEJJklojj4YNau82Pm_PyTaCokoRYYEAXTZjX2aRxDIhp1S9IdRn5n3VoCPUboOqu5FjQGHxF8qgYFeUJJUAo1C21Hg_05ASzdG8Wa04m7OYss8yzPaM2mh9nGWei8-IBV4X-vQarms39nZdA40fkZFFRIkgOxGizVky2ASHll6T7F93IQqep75W3tKS1MSU6Anh9B_4GmUldOS8kQ9eN2EkvAPvMgQz61WUvSXaBSFtQyr6OaJ58SJLwSC2nQ_r5cON6t83M9dzYbGcLdl_XUna02s-Xtn8za0uTU0F1Os_QBkr8iwNIt-HD49Ike2u6tthEB3iVdvVVoxV-aU95WA523XgBaVPJJZBsYccG1c69T9TRl0G_IdZNOr3-cDkWGOuXDQUP3maZ3uvo08SnzTeGkvNiUyxrcPl4SEHkvpaYiIp4iF94Z0JE_bEO-k_iws1w1BQZ9KLuWN7ioRbwIyMdpAM_MpKyZnWfV4Wd0X3Xu2cYTQ-IjDVEYOA4fGHQP2JbmKA82ZSbB-_fDrytlU06Tdhcr2QZPd-oqtlPJmz0zlPdK0xYshT0zhkwykfxqZuS1NUUE5bXRtOVjIN_DtuaWvEqdBJB_KY1zNUbTMDLte4C5_HakndOLd7EKUkHXe-LnOtKEab-Yz6Y9uLIuBuPx9di6GljWaDy66pl70x5ZF5fWaGR9HvaHw8Hwuv_aM39nTi8vxsPBoD8aXY0vR58vR4NrGQJUM3-qZpVp962eCQMkKFscfwfIfg54_R-xtFYC)


## Agile Development Process

### GitHub Projects

[GitHub Projects](https://www.github.com/Ironmonkeynuts/vendoro/projects) served as an Agile tool for this project. Through it, EPICs, User Stories, issues/bugs, and Milestone tasks were planned, then subsequently tracked on a regular basis using the Kanban project board.

![screenshot](documentation/gh-projects.png)

### GitHub Issues

[GitHub Issues](https://www.github.com/Ironmonkeynuts/vendoro/issues) served as an another Agile tool. There, I managed my User Stories and Milestone tasks, and tracked any issues/bugs.

| Link | Screenshot |
| --- | --- |
| [![GitHub issues](https://img.shields.io/github/issues-search/Ironmonkeynuts/vendoro?query=is%3Aissue%20is%3Aopen%20-label%3Abug&label=Open%20Issues&color=yellow)](https://www.github.com/Ironmonkeynuts/vendoro/issues?q=is%3Aissue%20is%3Aopen%20-label%3Abug) | ![screenshot](documentation/gh-issues-open.png) |
| [![GitHub closed issues](https://img.shields.io/github/issues-search/Ironmonkeynuts/vendoro?query=is%3Aissue%20is%3Aclosed%20-label%3Abug&label=Closed%20Issues&color=green)](https://www.github.com/Ironmonkeynuts/vendoro/issues?q=is%3Aissue%20is%3Aclosed%20-label%3Abug) | ![screenshot](documentation/gh-issues-closed.png) |

### MoSCoW Prioritization

I've decomposed my Epics into User Stories for prioritizing and implementing them. Using this approach, I was able to apply "MoSCoW" prioritization and labels to my User Stories within the Issues tab.

- **Must Have**: guaranteed to be delivered - required to Pass the project (*max ~60% of stories*)
- **Should Have**: adds significant value, but not vital (*~20% of stories*)
- **Could Have**: has small impact if left out (*the rest ~20% of stories*)
- **Won't Have**: not a priority for this iteration - future features

## Testing

> [!NOTE]  
> For all testing, please refer to the [TESTING.md](TESTING.md) file.

## Deployment

The live deployed application can be found deployed on [Heroku](https://imn-vendoro-55af0b986025.herokuapp.com).

### Heroku Deployment

This project uses [Heroku](https://www.heroku.com), a platform as a service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud.

Deployment steps are as follows, after account setup:

- Select **New** in the top-right corner of your Heroku Dashboard, and select **Create new app** from the dropdown menu.
- Your app name must be unique, and then choose a region closest to you (EU or USA), then finally, click **Create App**.
- From the new app **Settings**, click **Reveal Config Vars**, and set your environment variables to match your private `env.py` file.

> [!IMPORTANT]  
> This is a sample only; you would replace the values with your own if cloning/forking my repository.

| Key | Value |
| --- | --- |
| `DATABASE_URL` | user-inserts-own-postgres-database-url |
| `DISABLE_COLLECTSTATIC` | 1 (*this is temporary, and can be removed for the final deployment*) |
| `EMAIL_HOST_PASS` | user-inserts-own-gmail-api-key |
| `EMAIL_HOST_USER` | user-inserts-own-gmail-email-address |
| `SECRET_KEY` | any-random-secret-key |
| `STRIPE_PUBLIC_KEY` | user-inserts-own-stripe-public-key |
| `STRIPE_SECRET_KEY` | user-inserts-own-stripe-secret-key |
| `STRIPE_WH_SECRET` | user-inserts-own-stripe-webhook-secret |
| `CLOUDINARY_NAME` | user-inserts-own-cloudinary-name |
| `CLOUDINARY_API` | user-inserts-own-cloudinary-api-key |
| `CLOUDINARY_SECRET` | user-inserts-own-cloudinary-secret-key |

Heroku needs some additional files in order to deploy properly.

- [requirements.txt](requirements.txt)
- [Procfile](Procfile)
- [.python-version](.python-version)

You can install this project's **[requirements.txt](requirements.txt)** (*where applicable*) using:

- `pip3 install -r requirements.txt`

If you have your own packages that have been installed, then the requirements file needs updated using:

- `pip3 freeze --local > requirements.txt`

The **[Procfile](Procfile)** can be created with the following command:

- `echo web: gunicorn app_name.wsgi > Procfile`
- *replace `app_name` with the name of your primary Django app name; the folder where `settings.py` is located*

The **[.python-version](.python-version)** file tells Heroku the specific version of Python to use when running your application.

- `3.12` (or similar)

For Heroku deployment, follow these steps to connect your own GitHub repository to the newly created app:

Either (*recommended*):

- Select **Automatic Deployment** from the Heroku app.

Or:

- In the Terminal/CLI, connect to Heroku using this command: `heroku login -i`
- Set the remote for Heroku: `heroku git:remote -a app_name` (*replace `app_name` with your app name*)
- After performing the standard Git `add`, `commit`, and `push` to GitHub, you can now type:
	- `git push heroku main`

The project should now be connected and deployed to Heroku!

### Cloudinary API

This project uses the [Cloudinary API](https://cloudinary.com) to store media assets online, due to the fact that Heroku doesn't persist this type of data.

To obtain your own Cloudinary API key, create an account and log in.

- For "Primary Interest", you can choose **Programmable Media for image and video API**.
- *Optional*: edit your assigned cloud name to something more memorable.
- On your Cloudinary Dashboard, you can copy your **API Environment Variable**.
- Be sure to remove the leading `CLOUDINARY_URL=` as part of the API **value**; this is the **key**.
    - `cloudinary://123456789012345:AbCdEfGhIjKlMnOpQrStuVwXyZa@1a2b3c4d5)`
- This will go into your own `env.py` file, and Heroku Config Vars, using the **key** of `CLOUDINARY_URL`.

### PostgreSQL

This project uses a [Code Institute PostgreSQL Database](https://dbs.ci-dbs.net) for the Relational Database with Django.

> [!CAUTION]
> - PostgreSQL databases by Code Institute are only available to CI Students.
> - You must acquire your own PostgreSQL database through some other method if you plan to clone/fork this repository.
> - Code Institute students are allowed a maximum of 8 databases.
> - Databases are subject to deletion after 18 months.

To obtain my own Postgres Database from Code Institute, I followed these steps:

- Submitted my email address to the CI PostgreSQL Database link above.
- An email was sent to me with my new Postgres Database.
- The Database connection string will resemble something like this:
    - `postgres://<db_username>:<db_password>@<db_host_url>/<db_name>`
- You can use the above URL with Django; simply paste it into your `env.py` file and Heroku Config Vars as `DATABASE_URL`.

### Stripe API

This project uses [Stripe](https://stripe.com) to handle the ecommerce payments.

Once you've created a Stripe account and logged-in, follow these series of steps to get your project connected.

- From your Stripe dashboard, click to expand the "Get your test API keys".
- You'll have two keys here:
	- `STRIPE_PUBLIC_KEY` = Publishable Key (starts with **pk**)
	- `STRIPE_SECRET_KEY` = Secret Key (starts with **sk**)

As a backup, in case users prematurely close the purchase-order page during payment, we can include Stripe Webhooks.

- From your Stripe dashboard, click **Developers**, and select **Webhooks**.
- From there, click **Add Endpoint**.
	- `https://imn-vendoro-55af0b986025.herokuapp.com/checkout/wh/`
- Click **receive all events**.
- Click **Add Endpoint** to complete the process.
- You'll have a new key here:
	- `STRIPE_WH_SECRET` = Signing Secret (Wehbook) Key (starts with **wh**)

### Gmail API

This project uses [Gmail](https://mail.google.com) to handle sending emails to users for purchase order confirmations.

Once you've created a Gmail (Google) account and logged-in, follow these series of steps to get your project connected.

- Click on the **Account Settings** (cog icon) in the top-right corner of Gmail.
- Click on the **Accounts and Import** tab.
- Within the section called "Change account settings", click on the link for **Other Google Account settings**.
- From this new page, select **Security** on the left.
- Select **2-Step Verification** to turn it on. (*verify your password and account*)
- Once verified, select **Turn On** for 2FA.
- Navigate back to the **Security** page, and you'll see a new option called **App passwords** (*search for it at the top, if not*).
- This might prompt you once again to confirm your password and account.
- Select **Mail** for the app type.
- Select **Other (Custom name)** for the device type.
    - Any custom name, such as "Django" or `vendoro`
- You'll be provided with a 16-character password (API key).
    - Save this somewhere locally, as you cannot access this key again later!
    - If your 16-character password contains *spaces*, make sure to remove them entirely.
    - `EMAIL_HOST_PASS` = user's 16-character API key
    - `EMAIL_HOST_USER` = user's own personal Gmail email address

### WhiteNoise

This project uses the [WhiteNoise](https://whitenoise.readthedocs.io/en/latest/) to aid with static files temporarily hosted on the live Heroku site.

To include WhiteNoise in your own projects:

- Install the latest WhiteNoise package:
    - `pip install whitenoise`
- Update the `requirements.txt` file with the newly installed package:
    - `pip freeze --local > requirements.txt`
- Edit your `settings.py` file and add WhiteNoise to the `MIDDLEWARE` list, above all other middleware (apart from Django’s "SecurityMiddleware"):

```python
# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # any additional middleware
]
```


### Local Development

This project can be cloned or forked in order to make a local copy on your own system.

For either method, you will need to install any applicable packages found within the [requirements.txt](requirements.txt) file.

- `pip3 install -r requirements.txt`.

You will need to create a new file called `env.py` at the root-level, and include the same environment variables listed above from the Heroku deployment steps.

> [!IMPORTANT]  
> This is a sample only; you would replace the values with your own if cloning/forking my repository.

Sample `env.py` file:

```python
import os

os.environ.setdefault("CLOUDINARY_NAME", "user-inserts-own-cloudinary-name")
os.environ.setdefault("CLOUDINARY_API", "user-inserts-own-cloudinary-api-key")
os.environ.setdefault("CLOUDINARY_SECRET", "user-inserts-own-cloudinary-secret-key")
os.environ.setdefault("DATABASE_URL", "user-inserts-own-postgres-database-url")
os.environ.setdefault("EMAIL_HOST_PASS", "user-inserts-own-gmail-host-api-key")
os.environ.setdefault("EMAIL_HOST_USER", "user-inserts-own-gmail-email-address")
os.environ.setdefault("SECRET_KEY", "any-random-secret-key")
os.environ.setdefault("STRIPE_PUBLIC_KEY", "user-inserts-own-stripe-public-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "user-inserts-own-stripe-secret-key")
os.environ.setdefault("STRIPE_WH_SECRET", "user-inserts-own-stripe-webhook-secret")  # only if using Stripe Webhooks

# local environment only (do not include these in production/deployment!)
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DEVELOPMENT", "True")
```

Once the project is cloned or forked, in order to run it locally, you'll need to follow these steps:

- Start the Django app: `python3 manage.py runserver`
- Stop the app once it's loaded: `CTRL+C` (*Windows/Linux*) or `⌘+C` (*Mac*)
- Make any necessary migrations: `python3 manage.py makemigrations --dry-run` then `python3 manage.py makemigrations`
- Migrate the data to the database: `python3 manage.py migrate --plan` then `python3 manage.py migrate`
- Create a superuser: `python3 manage.py createsuperuser`
- Load fixtures (*if applicable*): `python3 manage.py loaddata file-name.json` (*repeat for each file*)
- Everything should be ready now, so run the Django app again: `python3 manage.py runserver`

If you'd like to backup your database models, use the following command for each model you'd like to create a fixture for:

- `python3 manage.py dumpdata your-model > your-model.json`
- *repeat this action for each model you wish to backup*
- **NOTE**: You should never make a backup of the default *admin* or *users* data with confidential information.

#### Cloning

You can clone the repository by following these steps:

1. Go to the [GitHub repository](https://www.github.com/Ironmonkeynuts/vendoro).
2. Locate and click on the green "Code" button at the very top, above the commits and files.
3. Select whether you prefer to clone using "HTTPS", "SSH", or "GitHub CLI", and click the "copy" button to copy the URL to your clipboard.
4. Open "Git Bash" or "Terminal".
5. Change the current working directory to the location where you want the cloned directory.
6. In your IDE Terminal, type the following command to clone the repository:
	- `git clone https://www.github.com/Ironmonkeynuts/vendoro.git`
7. Press "Enter" to create your local clone.

Alternatively, if using Ona (formerly Gitpod), you can click below to create your own workspace using this repository.

[![Open in Ona-Gitpod](https://ona.com/run-in-ona.svg)](https://gitpod.io/#https://www.github.com/Ironmonkeynuts/vendoro)

**Please Note**: in order to directly open the project in Ona (Gitpod), you should have the browser extension installed. A tutorial on how to do that can be found [here](https://www.gitpod.io/docs/configure/user-settings/browser-extension).

#### Forking

By forking the GitHub Repository, you make a copy of the original repository on our GitHub account to view and/or make changes without affecting the original owner's repository. You can fork this repository by using the following steps:

1. Log in to GitHub and locate the [GitHub Repository](https://www.github.com/Ironmonkeynuts/vendoro).
2. At the top of the Repository, just below the "Settings" button on the menu, locate and click the "Fork" Button.
3. Once clicked, you should now have a copy of the original repository in your own GitHub account!

### Local VS Deployment

⚠️ INSTRUCTIONS ⚠️

Use this space to discuss any differences between the local version you've developed, and the live deployment site. Generally, there shouldn't be [m]any major differences, so if you honestly cannot find any differences, feel free to use the following example:

⚠️ --- END --- ⚠️

There are no remaining major differences between the local version when compared to the deployed version online.

## Credits

⚠️ INSTRUCTIONS ⚠️

In the following sections, you need to reference where you got your content, media, and any extra help. It is common practice to use code from other repositories and tutorials (which is totally acceptable), however, it is important to be very specific about these sources to avoid potential plagiarism.

⚠️ --- END ---⚠️

### Content

⚠️ INSTRUCTIONS ⚠️

Use this space to provide attribution links for any borrowed code snippets, elements, and resources. Ideally, you should provide an actual link to every resource used, not just a generic link to the main site. If you've used multiple components from the same source (such as Bootstrap), then you only need to list it once, but if it's multiple Codepen samples, then you should list each example individually. If you've used AI for some assistance (such as ChatGPT or Perplexity), be sure to mention that as well. A few examples have been provided below to give you some ideas.

Eventually you'll want to learn how to use Git branches. Here's a helpful tutorial called [Learn Git Branching](https://learngitbranching.js.org) to bookmark for later.

⚠️ --- END ---⚠️

| Source | Notes |
| --- | --- |
| [Markdown Builder](https://markdown.2bn.dev) | Help generating Markdown files |
| [Chris Beams](https://chris.beams.io/posts/git-commit) | "How to Write a Git Commit Message" |
| [Boutique Ado](https://codeinstitute.net) | Code Institute walkthrough project inspiration |
| [Bootstrap](https://getbootstrap.com) | Various components / responsive front-end framework |
| [Cloudinary]() | Cloud storage for static/media files |
| [Whitenoise](https://whitenoise.readthedocs.io) | Static file service |
| [Stripe](https://docs.stripe.com/payments/elements) | Online payment services |
| [Gmail API](https://developers.google.com/gmail/api/guides) | Sending payment confirmation emails |
| [Python Tutor](https://pythontutor.com) | Additional Python help |
| [ChatGPT](https://chatgpt.com) | Help with code logic and explanations. Help creating text content for site information |

### Media

| Source | Notes |
| --- | --- |
| [favicon.io](https://favicon.io) | Generating the favicon |
| [Boutique Ado](https://codeinstitute.net) | Sample images provided from the walkthrough projects |
| [ChatGPT](https://chatgpt.com) | Help with creating logo and hero images to specification |
| [Font Awesome](https://fontawesome.com) | Icons used throughout the site |

### Acknowledgements


- I would like to thank my Code Institute mentor, [Tim Nelson](https://www.github.com/TravelTimN) for the support throughout the development of this project.
- I would like to thank my Runshaw College Tutors, [Tom Cowen](https://wwww.runshaw.ac.uk) and [Kevin Loughrey](https://wwww.runshaw.ac.uk) for the support throughout the development of this project.
- I would like to thank the [Code Institute](https://codeinstitute.net) Tutor Team for their assistance with troubleshooting and debugging some project issues.
- I would like to thank the [Code Institute Slack community](https://code-institute-room.slack.com) and [Code Institute Discord community](https://discord-portal.codeinstitute.net) for the moral support; it kept me going during periods of self doubt and impostor syndrome.
- I would like to thank my fellow students on the course for support  with finding bugs and general appraisal of the project code.





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





