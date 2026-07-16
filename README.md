# Kay Mama Cuisine Créole - Restaurant Management Platform

A premium, production-ready, SaaS-quality restaurant management platform designed for **Kay Mama Cuisine Créole** in French Guiana (Guyane Française). Built with a clean Django architecture and dynamic frontend components (HTMX, AlpineJS, TailwindCSS, GSAP, AOS).

---

## Technical Stack
- **Backend**: Django 5, Django REST Framework, PostgreSQL, Celery, Redis, Pillow
- **Frontend**: Django Templates, HTMX, AlpineJS, Tailwind CSS
- **Animations**: GSAP, AOS, Framer Motion inspired triggers, Smooth scrolling
- **Production**: Docker, Gunicorn, Nginx, WhiteNoise

---

## Website Structure
1. **Home**: Premium hero section, Services list, presentation panels, specialties highlights, Chef section, and Google Maps embed.
2. **Menu**: Beautiful category-based tabs filter (via HTMX), text search (HTMX keyup), low stock alerts, and options selector.
3. **Cart & Checkout**: Drawer cart (AlpineJS), complete cart detail page, Cayenne delivery validators, and Stripe-like payment simulator.
4. **Reservations**: Live time-slot occupancy capacity validators, blocked dates/holidays checker, and manager status updating panels.
5. **Events**: Special catering, private chef, and cocktail quotations forms.
6. **Blog**: Articles list, recipe detailed readings, and canonical SEO meta attributes.
7. **Gallery**: Album grids and animated lightbox (AlpineJS).
8. **Account Profile**: Orders log, reservation updates, and details updater.
9. **Admin Dashboard**: Live kitchen display board (HTMX polling), charts (Chart.js), revenue metrics, reservations list, settings editor, and stock toggler.

---

## Local Development Installation

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Set Up Virtual Environment & Packages
```bash
# Clone the repository and enter
cd Mama

# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(By default, `.env` leaves `DATABASE_URL` commented out, allowing Django to fall back to an instant SQLite database for local development without manual PostgreSQL configuration).*

### 4. Create Migrations & Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed the Database
Kay Mama includes a custom programmatic database seeder containing all dishes from their marketing flyers, sample opening hours, CMS landing sections, blog posts, photo albums, and mock analytics data for charts:
```bash
python manage.py seed_restaurant
```

### 6. Create Initial Admin Credentials (Optional)
Create the superuser based on environment variables (`DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD`):
```bash
python manage.py init_admin
```

### 7. Run Server Locally
```bash
python manage.py runserver
```
Visit the platform at `http://127.0.0.1:8000/`.

- **Client access**: `http://127.0.0.1:8000/`
- **Manager Dashboard**: `http://127.0.0.1:8000/dashboard/` (Login with `admin` / `AdminSecretPassword123`)
- **Kitchen Board**: `http://127.0.0.1:8000/dashboard/kitchen/` (Login with `chef` / `Password123`)

---

## Running Automatic Tests
Run Django test runners:
```bash
python manage.py test
```

---

## Production Deployment Guide

We recommend deployment via **Docker Compose** or **Nginx + Gunicorn + Supervisor + systemd**.

### Docker Deployment (Recommended)
1. Uncomment the `DATABASE_URL` line inside your `.env` file to enable PostgreSQL integration:
   ```env
   DATABASE_URL=postgres://postgres:postgres@db:5432/kaymama
   ```
2. Build and launch services in background:
   ```bash
   docker-compose up -d --build
   ```
3. Run migrations and seed data in the web container:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py seed_restaurant
   docker-compose exec web python manage.py init_admin
   ```

### Manual Linux Deployment Configs

#### 1. Nginx Configuration
Create a configuration file at `/etc/nginx/sites-available/kaymama`:
```nginx
# Paste content of deployments/nginx.conf here
```
Enable the site and reload Nginx:
```bash
ln -s /etc/nginx/sites-available/kaymama /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 2. Process Manager (Supervisor)
To keep Gunicorn and Celery running in the background, use Supervisor:
Create config at `/etc/supervisor/conf.d/kaymama.conf`:
```ini
# Paste content of deployments/supervisor.conf here
```
Reload Supervisor:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start all
```

#### 3. Redis Setup
Ensure Redis is installed and running:
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### 4. PostgreSQL Configuration
Install PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
sudo -i -u postgres psql
CREATE DATABASE kaymama;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE kaymama TO postgres;
\q
```
