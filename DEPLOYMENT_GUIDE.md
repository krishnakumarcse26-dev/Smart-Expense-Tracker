# SmartExpense — Complete Deployment Guide
## From Local Development → Live on Render (Free Tier)

---

## PART 1: LOCAL DEVELOPMENT SETUP

### Step 1 — Install Python
```bash
# Check if Python is installed (need 3.10+)
python3 --version

# If not installed, download from https://python.org
```

### Step 2 — Clone / Create Project Folder
```bash
# Navigate to where you want the project
cd ~/Desktop

# Create and enter the folder
mkdir smartexpense
cd smartexpense

# Copy all project files here, then:
```

### Step 3 — Create Virtual Environment
```bash
# A virtual environment isolates your project's dependencies.
# This means Project A's Django 5 won't conflict with Project B's Django 4.

python3 -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You'll see (venv) at the start of your terminal prompt — good!
```

### Step 4 — Install Dependencies
```bash
# Install all packages listed in requirements.txt
pip install -r requirements.txt

# Verify Django is installed:
python -m django --version
# Expected output: 5.0.6
```

### Step 5 — Configure Environment Variables
```bash
# The .env file already exists. Leave it as-is for development.
# It reads: DEBUG=True, SQLite database, etc.

# NEVER edit .env for production settings locally.
# Production env vars go directly in Render's dashboard (explained below).
```

### Step 6 — Run Migrations
```bash
# Migrations create your database tables.
# Run this every time you add/change a model.

python manage.py makemigrations
python manage.py migrate

# You should see: "Applying accounts.0001_initial... OK" etc.
```

### Step 7 — Create Superuser (Admin Account)
```bash
# This creates an admin user for /admin/ panel
python manage.py createsuperuser

# Enter:
#   Username: admin
#   Email: admin@example.com
#   Password: (choose a strong password)
```

### Step 8 — Run Development Server
```bash
python manage.py runserver

# Open: http://127.0.0.1:8000
# Admin: http://127.0.0.1:8000/admin/
```

### Step 9 — Seed Sample Data (Optional but Recommended)
```bash
# In the Django shell, create sample categories:
python manage.py shell

# Then type:
from django.contrib.auth.models import User
from transactions.models import Category
user = User.objects.first()
categories = [
    ('Food & Dining', 'bi-egg-fried', '#ef4444', 'expense'),
    ('Transport', 'bi-car-front', '#f59e0b', 'expense'),
    ('Entertainment', 'bi-film', '#8b5cf6', 'expense'),
    ('Utilities', 'bi-lightning-charge', '#06b6d4', 'expense'),
    ('Healthcare', 'bi-heart-pulse', '#10b981', 'expense'),
    ('Shopping', 'bi-bag', '#f97316', 'expense'),
    ('Salary', 'bi-briefcase', '#00d4aa', 'income'),
    ('Freelance', 'bi-laptop', '#7c3aed', 'income'),
]
for name, icon, color, ctype in categories:
    Category.objects.get_or_create(user=user, name=name, defaults={'icon': icon, 'color': color, 'category_type': ctype})
print("Categories created!")
exit()
```

---

## PART 2: GIT & GITHUB SETUP

### Step 10 — Install Git
```bash
# Check if Git is installed
git --version

# If not: https://git-scm.com/downloads
```

### Step 11 — Initialize Git Repository
```bash
# In your project root (smartexpense/)
git init

# This creates a hidden .git/ folder — Git's database
```

### Step 12 — Create .gitignore (already done)
```bash
# .gitignore tells Git which files to IGNORE.
# Critical: venv/, .env, db.sqlite3 must NEVER be committed.

# Verify .gitignore is working:
git status
# You should NOT see venv/, .env, or db.sqlite3 in the output.
```

### Step 13 — First Commit
```bash
# Stage all files (except those in .gitignore)
git add .

# Commit with a descriptive message
git commit -m "Initial commit: SmartExpense Financial Platform"

# View your commit history
git log --oneline
```

### Step 14 — Create GitHub Repository
```bash
# 1. Go to https://github.com → Sign in
# 2. Click "New Repository" (+ button top right)
# 3. Name it: smartexpense
# 4. Keep it PUBLIC (required for Render free tier)
# 5. DON'T add README/gitignore (we already have them)
# 6. Click "Create repository"
```

### Step 15 — Push to GitHub
```bash
# Connect your local repo to GitHub (replace YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/smartexpense.git

# Rename default branch to 'main'
git branch -M main

# Push your code to GitHub
git push -u origin main

# Enter your GitHub username and password (or personal access token)
```

---

## PART 3: RENDER DEPLOYMENT

### Step 16 — Create Render Account
```
1. Go to https://render.com
2. Sign up with GitHub (recommended — links your repos)
3. Verify your email
```

### Step 17 — Create PostgreSQL Database on Render
```
1. Render Dashboard → "New +" → "PostgreSQL"
2. Settings:
   - Name: smartexpense-db
   - Region: Oregon (US West) — or closest to you
   - Plan: Free
3. Click "Create Database"
4. SAVE these values (you'll need them):
   - Internal Database URL: postgresql://...
   - Or individual: Host, Port, Database, Username, Password
```

### Step 18 — Create Web Service on Render
```
1. Render Dashboard → "New +" → "Web Service"
2. Connect GitHub → Select your "smartexpense" repository
3. Settings:
   - Name: smartexpense
   - Region: Oregon (same as database!)
   - Branch: main
   - Runtime: Python 3
   - Build Command: ./build.sh
   - Start Command: gunicorn smartexpense.wsgi --bind 0.0.0.0:$PORT --workers 2
   - Plan: Free
```

### Step 19 — Set Environment Variables on Render
```
In your Web Service → "Environment" tab → Add these variables:

SECRET_KEY       → (generate one: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG            → False
ALLOWED_HOSTS    → smartexpense.onrender.com

DB_ENGINE        → django.db.backends.postgresql
DB_NAME          → (from Render PostgreSQL dashboard)
DB_USER          → (from Render PostgreSQL dashboard)
DB_PASSWORD      → (from Render PostgreSQL dashboard)
DB_HOST          → (from Render PostgreSQL dashboard)
DB_PORT          → 5432
```

### Step 20 — Deploy
```
1. Click "Create Web Service"
2. Render will:
   a. Pull your code from GitHub
   b. Run: pip install -r requirements.txt
   c. Run: python manage.py collectstatic
   d. Run: python manage.py migrate
   e. Start: gunicorn smartexpense.wsgi ...
3. Watch the logs — takes 3-5 minutes first time
4. Your app will be live at: https://smartexpense.onrender.com
```

### Step 21 — Create Production Superuser
```bash
# In Render dashboard → your web service → "Shell" tab
python manage.py createsuperuser
```

### Step 22 — Auto-Deploy Setup
```
Every time you push to GitHub main branch:
  git add .
  git commit -m "Your change description"
  git push origin main

Render automatically redeploys! (Takes ~2-3 minutes)
```

---

## PART 4: COMMON ERRORS & FIXES

### Error: "Module not found"
```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Error: "no such table"
```bash
python manage.py migrate
```

### Error: "ALLOWED_HOSTS" on production
```
Add your Render domain to ALLOWED_HOSTS env var:
  smartexpense.onrender.com
```

### Error: Static files not loading on production
```bash
# Make sure build.sh runs collectstatic
# And STATICFILES_STORAGE = whitenoise... is in settings.py
python manage.py collectstatic --no-input
```

### Error: "Port already in use"
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9    # Mac/Linux
netstat -ano | findstr :8000      # Windows (then kill the PID)
```

---

## PART 5: AFTER DEPLOYMENT CHECKLIST

- [ ] App loads at your Render URL
- [ ] Registration works → creates profile
- [ ] Login/Logout works
- [ ] Can create transactions
- [ ] Dashboard charts render
- [ ] Budget creation works
- [ ] Goals and subscriptions work
- [ ] CSV/Excel export downloads
- [ ] Password reset sends email (configure SMTP)
- [ ] Admin panel accessible at /admin/

---

## ARCHITECTURE SUMMARY

```
Browser Request
      ↓
Render (HTTPS/SSL terminated)
      ↓
Gunicorn (WSGI Server — 2 workers)
      ↓
Django (smartexpense/wsgi.py)
      ↓
URL Router (smartexpense/urls.py)
      ↓
App URLs (accounts/urls.py, transactions/urls.py, ...)
      ↓
View Function (views.py)
      ↓
Business Logic (analytics/services.py)
      ↓
Django ORM
      ↓
PostgreSQL (Render managed DB)
      ↓
HTML Template → Response → Browser
```

---
