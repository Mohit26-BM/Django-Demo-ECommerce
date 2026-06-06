# MyShop — Django E-Commerce

A full-featured e-commerce web app built with Django 5.2 and Bootstrap 5.

**Live demo:** [https://django-demo-ecommerce.onrender.com/](https://django-demo-ecommerce.onrender.com/)

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5.2 |
| Database | SQLite (dev) / PostgreSQL-ready (psycopg2 included) |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Inter font |
| Static files | WhiteNoise |
| Production server | Gunicorn |
| Image handling | Pillow |

---

## Features

### Auth

- **Sign up** — Django `UserCreationForm`, auto-login on registration
- **Sign in / Sign out** — session-based auth
- **Admin panel** — `/admin/` (create a superuser first, see setup below)

### Browsing

- Home page with hero carousel (banners), featured products, deals, and per-category sections
- Product listing with sort (price asc/desc, name)
- Category filtering
- Product detail with related products
- Search (name + description)

### Cart

- Session-based cart — works without a database, persists across pages
- Add, update quantity, remove items
- Cart badge in navbar shows item count

### Checkout & Orders

- Checkout page with payment method selection (COD / UPI / Card)
- **Payment is simulated** — selecting UPI or Card records the method but does not process any real transaction. Orders are created immediately as "Pending".
- Order confirmation page shown after placing
- Full order history with status tracking (Pending → Paid → Shipped → Delivered)
- Cancel order (Pending only), request return (Delivered only), reorder, delete from history

### Wishlist

- Add / remove products
- Dedicated wishlist page
- Duplicate prevention via `unique_together` constraint

### Admin

All models are registered with customised admin views:

- **Products** — inline edit `is_featured` / `is_active`, filter by category
- **Orders** — view line items inline, filter by status
- **Banners** — toggle active, reorder
- **Categories, Wishlist** — search and list views

---

## Project Structure

```text
ecommerce/
├── ecommerce/          # Project config (settings, urls, wsgi)
├── shop/               # Main app
│   ├── management/
│   │   └── commands/
│   │       └── seed_shop.py    # Seeds products from DummyJSON API
│   ├── migrations/
│   ├── static/shop/
│   │   ├── css/
│   │   │   ├── main.css        # Design tokens, layout, components
│   │   │   └── ecommerce.css   # Page-specific styles
│   │   ├── js/main.js          # Scroll-reveal, ripple, back-to-top, etc.
│   │   └── img/logo.svg
│   ├── templates/
│   │   ├── registration/       # login.html, signup.html
│   │   └── shop/               # All other page templates
│   ├── admin.py
│   ├── context_processors.py   # Injects categories into every template
│   ├── models.py               # Category, Product, Banner, Order, OrderItem, Wishlist
│   ├── urls.py
│   ├── utils.py                # build_cart_items helper
│   └── views.py
├── media/              # Uploaded/downloaded images
├── db.sqlite3
├── manage.py
├── requirements.txt
└── render.yaml         # Render.com deployment config
```

---

## Setup

### Prerequisites

- Python 3.10+ (or activate your conda base)
- The packages in `requirements.txt`

```bash
pip install -r requirements.txt
```

### First run

```bash
python manage.py migrate
python manage.py createsuperuser       # for /admin access
python manage.py seed_shop             # seeds 100 products from DummyJSON API
python manage.py runserver
```

Open `http://127.0.0.1:8000`

### Seed options

```bash
python manage.py seed_shop             # 100 products (default)
python manage.py seed_shop --all       # all ~194 products
python manage.py seed_shop --keep-banners   # don't overwrite banner data
python manage.py seed_shop --keep-images    # skip re-downloading existing images
```

---

## Payment

Payment is **not integrated with any gateway**. The checkout form lets users choose a method (COD, UPI, or Card) and the choice is stored on the order record. No money moves and no external API is called. To add real payments, integrate Razorpay or Stripe at the `checkout` view in `views.py`.

---

## Deployment (Render.com)

1. Set `DEBUG=False` and `ALLOWED_HOSTS=your-app.onrender.com` in environment variables
2. Set a strong `SECRET_KEY`
3. The build command in `render.yaml` runs `collectstatic` and `migrate` automatically
4. WhiteNoise serves static files in production — no separate CDN needed

> Media files (product images) are **not persistent** on Render's free tier. For production use an object store like AWS S3 or Cloudflare R2.

---

## Author

Created by Mohit — [github.com/Mohit26-BM](https://github.com/Mohit26-BM)
