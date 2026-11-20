# MyShop — Django E-Commerce

A full-featured e-commerce web app built with Django 5.2 and Bootstrap 5.

**Live demo:** [https://django-demo-ecommerce-h1js.onrender.com](https://django-demo-ecommerce-h1js.onrender.com)

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 5.2 (LTS) |
| Database | SQLite (add `psycopg2-binary` and a `DATABASES` change to use PostgreSQL) |
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

- Python 3.12 (a conda environment works fine)
- The four packages in `requirements.txt`: Django, gunicorn, Pillow, WhiteNoise

```bash
pip install -r requirements.txt
```

### Local configuration

Copy the example settings file once. `.env` is git-ignored and never published.

```bash
copy .env.example .env        # Windows   (macOS/Linux: cp .env.example .env)
```

`.env.example` turns on `DEBUG` for local work. Without a `.env` the app starts in production mode and asks for a `SECRET_KEY`.

### First run

```bash
python manage.py migrate              # also loads the starter catalogue (100 products, categories, banners)
python manage.py createsuperuser       # your admin login for /admin/
python manage.py runserver
```

Open `http://127.0.0.1:8000`. No user accounts are created for you and none are stored in the repository: sign up on the site, or create your admin with `createsuperuser`.

### Seed options

```bash
python manage.py seed_shop             # 100 products (default)
python manage.py seed_shop --all       # all ~194 products
python manage.py seed_shop --keep-banners   # don't overwrite banner data
python manage.py seed_shop --keep-images    # skip re-downloading existing images
python manage.py seed_shop --if-empty       # do nothing if products already exist
```

`seed_shop` is only needed to re-download the catalogue from DummyJSON. It refuses to wipe products that customer orders reference (use `--force` to override). When the database has no banners it creates four default ones from `media/banners/`.

---

## Payment

Payment is **not integrated with any gateway**. The checkout form lets users choose a method (COD, UPI, or Card) and the choice is stored on the order record. No money moves and no external API is called. To add real payments, integrate Razorpay or Stripe at the `checkout` view in `views.py`.

---

## Deployment (Render.com)

`render.yaml` is ready to use: connect the repository and Render builds it.

1. The build installs packages, runs `collectstatic`, applies migrations and creates an admin if you set the optional variables below. The migrations load the starter catalogue (from `shop/data/catalog.json`, using the images in `media/`) into an empty database, so a fresh deploy always has products, with no network access needed.
2. `SECRET_KEY` is generated for you and `DEBUG` is off. The Render host name is added to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` automatically.
3. To get an admin login without a shell, set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` in the Render dashboard (never in the repository).
4. WhiteNoise serves static files, and product images are served from the committed `media/` folder.

> **Free-tier note:** Render's free disk is not persistent. The SQLite database (accounts, orders) is recreated on every deploy, and images uploaded through the admin are lost. For real use, attach a persistent disk and set `SQLITE_PATH`, or move to PostgreSQL and an object store such as S3 or Cloudflare R2.

## Security notes

- Production defaults: debug off, HTTPS redirect with the proxy header honoured, secure cookies, HSTS, `nosniff`, frame denial.
- Cart quantities are validated and capped at 20; checkout is one database transaction; hidden (inactive) products cannot be viewed, searched or bought.
- Wishlist changes and sign-out are POST-only. `?next=` redirects only go to this site. Repeated failed logins for one account are throttled.
- Orders can only be changed by their owner.

## Author

Created by Mohit — [github.com/Mohit26-BM](https://github.com/Mohit26-BM)
