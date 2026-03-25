# Django E-commerce Website

A functional demo e-commerce website built using Django and deployed on Render.

---

## Live Demo

Visit the site:
[https://django-demo-ecommerce.onrender.com/](https://django-demo-ecommerce.onrender.com/)

---

## Features

* User authentication (login, logout)
* Product listing and detail pages
* Basic add-to-cart functionality
* Static and media file handling
* Admin dashboard for product management
* Responsive design using Bootstrap

---

## Tech Stack

* Python 3.12.11
* Django 5.2.4
* SQLite (development database)
* Render (deployment platform)
* Bootstrap 5 (frontend framework)

---

## Project Structure

```id="doxu3h"
ecommerce/
├── ecommerce/          # Project configuration
├── shop/               # Main application (products, views, models)
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, images
├── media/              # Uploaded files
├── manage.py
├── requirements.txt
├── render.yaml
└── README.md
```

---

## Deployment (Render)

### Required Files

* `requirements.txt`
* `render.yaml`

### render.yaml Configuration

```yaml
services:
  - type: web
    name: ecommerce
    env: python
    buildCommand: ""
    startCommand: gunicorn ecommerce.wsgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: ecommerce.settings
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: YOUR_RENDER_DOMAIN
```

---

## Environment Variables

Configure the following variables in the Render dashboard:

* `SECRET_KEY`: Django secret key
* `DEBUG`: False
* `DJANGO_SETTINGS_MODULE`: ecommerce.settings

---

## Development Setup

```bash
git clone https://github.com/your-username/your-repo.git
cd ecommerce
python -m venv env
source env/bin/activate   # On Windows: .\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Author

Created by Mohit
[https://github.com/Mohit26-BM](https://github.com/Mohit26-BM)
