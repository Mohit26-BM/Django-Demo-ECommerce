# 🛒 Django E-commerce Website

A demo functional e-commerce website built using Django, deployed on Render.

## 🌐 Live Demo

👉 [Visit the Site](https://django-demo-ecommerce.onrender.com/)

---

## 📌 Features

- User authentication (login, logout)
- Product listing and details
- Add to cart (basic)
- Static and media file handling
- Admin dashboard for product management
- Bootstrap styling

---

## 🚀 Tech Stack

- Python 3.12.11
- Django 5.2.4
- SQLite (development)
- Render (hosting)
- Bootstrap 5 (frontend)

---

## 📂 Project Structure

```
ecommerce/
├── ecommerce/          # Project settings
├── shop/               # Main app for products
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # Uploaded media
├── manage.py
├── requirements.txt
├── build.sh
├── render.yaml
└── README.md
```

---

## ⚙️ Deployment (Render)

### 1. Files needed:
- `requirements.txt`
- `render.yaml`

### 2. `render.yaml`
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

## 🔐 Environment Variables

Set these in Render dashboard:

- `SECRET_KEY`: your Django secret key
- `DEBUG`: `False`
- `DJANGO_SETTINGS_MODULE`: `ecommerce.settings`

---

## 🧪 Development Setup

```bash
git clone https://github.com/your-username/your-repo.git
cd ecommerce
python -m venv env
source env/bin/activate   # or .\env\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📝 License

MIT License. Feel free to use and customize this project.

---

## 👨‍💻 Author

Created by [Your Name](https://github.com/Mohit26-BM)
