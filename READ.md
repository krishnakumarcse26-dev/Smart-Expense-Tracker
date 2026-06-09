# Smart Expense Tracker

A full-stack personal finance management application built with Django and Python.
Track your income, expenses, budgets, and savings goals through an analytics dashboard.

## Features

- User registration, login, and authentication
- Add, edit, delete income and expense transactions
- Category-wise expense tracking
- Budget management with limit tracking
- Savings goals with progress monitoring
- Subscription tracking
- Analytics dashboard with financial charts
- Financial health score and forecasting
- Reports with Excel and PDF export
- Password reset via email
- Responsive design

## Tech Stack

- **Backend:** Python 3.12, Django 5.0
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** SQLite (development), PostgreSQL (production)
- **Charts:** Chart.js
- **Forms:** django-crispy-forms with Bootstrap 5
- **Static Files:** WhiteNoise
- **Deployment:** Gunicorn, Render

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/krishnakumarcse26-dev/smart-expense-tracker.git
cd smart-expense-tracker
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Open .env and update values if needed
```

**5. Run database migrations**
```bash
python manage.py migrate
```

**6. Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

**7. Start the development server**
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000`

## Project Structure

smart-expense-tracker/
├── smartexpense/        # Django project settings
├── accounts/            # User authentication and profiles
├── transactions/        # Income and expense tracking
├── budgets/             # Budget management
├── goals/               # Savings goals
├── subscriptions/       # Subscription tracking
├── analytics/           # Dashboard and financial analytics
├── reports/             # Report generation
├── templates/           # HTML templates
├── static/              # CSS, JS, images
├── requirements.txt
└── manage.py

## Author

**Krishnakumar S**
- GitHub: [@krishnakumarcse26-dev](https://github.com/krishnakumarcse26-dev)
- LinkedIn: [linkedin.com/in/krishnakumar](https://linkedin.com/in/krishnakumar)
- Email: krishnakumarcse26@gmail.com