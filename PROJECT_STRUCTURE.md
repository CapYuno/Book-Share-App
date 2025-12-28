# BookShare Project Structure

## Overview
This document provides a visual overview of the BookShare project structure created for your FYP.

## Directory Tree

```
bookshare/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── models.py                # SQLAlchemy models (Book, Borrower, Loan, etc.)
│   ├── routes/                  # Blueprint routes
│   │   ├── admin.py             # Admin panel routes
│   │   ├── books.py             # Book CRUD and search
│   │   ├── borrowers.py         # Borrower management
│   │   ├── dashboard.py         # Dashboard statistics
│   │   ├── loans.py             # Loan creation and returns
│   │   └── recommendations.py   # AI recommendations (Phase 3)
│   ├── services/                # Business logic layer
│   │   └── __init__.py          # (Placeholder for AI & email services)
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base template with navigation
│   │   └── dashboard/
│   │       └── index.html       # Dashboard page
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       └── cli.py               # Flask CLI commands
│
├── scripts/
│   └── seed.py                  # Database seeding with Faker
│
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/
│   │   └── test_models.py       # Model unit tests
│   └── functional/              # (Empty, for API tests)
│
├── migrations/                  # (Empty, for future DB migrations)
├── seed/                        # (Empty, for seed data files)
├── docs/                        # (Empty, for documentation)
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── config.py                    # Configuration classes
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

## Key Files Created

### Core Application
- **run.py**: Entry point that creates and runs the Flask app
- **config.py**: Configuration for development, production, and testing environments
- **app/__init__.py**: Application factory with extension initialization

### Database Models (app/models.py)
- **Book**: Title, author, ISBN, year, genre, description
- **Borrower**: Name, email, phone
- **Loan**: Book-borrower relationship with dates
- **Notification**: Email reminder tracking
- **Setting**: Key-value configuration store

### Routes (Blueprints)
All routes are organized as Flask blueprints:
- Dashboard with statistics
- Books with CRUD and search
- Borrowers management
- Loans (create, return, overdue filtering)
- Recommendations (placeholder for Phase 3)
- Admin panel

### Utilities
- **CLI commands**: `flask init-db`, `flask seed-db`, `flask rebuild-recs`
- **Seed script**: Generates realistic synthetic data using Faker library

### Testing
- Pytest configuration with fixtures
- Sample model tests demonstrating book availability logic

## Next Steps

1. **Initialize Git repository** (optional)
   ```bash
   cd bookshare
   git init
   git add .
   git commit -m "Initial project structure"
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize database and seed with data**
   ```bash
   flask init-db
   flask seed-db --books 1000 --borrowers 50 --loans 200
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## Implementation Phases

### ✅ Phase 0: Project Setup (COMPLETED)
- Project structure created
- Core dependencies defined
- Flask application factory configured
- Database models designed
- Basic blueprints implemented
- Seed script with Faker
- Testing infrastructure

### 🔄 Phase 1: Data Model & Core API (NEXT)
- Complete remaining CRUD operations
- Implement advanced search
- Add data validation
- Create more template pages

### 📋 Phase 2: UI Pages
- Complete all HTML templates
- Add forms for data entry
- Implement responsive design

### 🤖 Phase 3: AI Recommendation Module
- Build TF-IDF vectorizer
- Implement similarity calculation
- Create recommendation endpoints
- Add UI integration

### 📧 Phase 4: Reminder Engine
- Design reminder scheduling
- Implement SMTP email sending
- Create APScheduler jobs

### 🧪 Phase 5: Testing
- Unit tests for all models
- Functional API tests
- Performance benchmarking

### 📄 Phase 6: Documentation & Report
- Architecture diagrams
- Admin runbook
- Final report assembly

## Technologies Used

- **Flask 3.0**: Web framework
- **SQLAlchemy**: ORM for database
- **scikit-learn**: TF-IDF for AI recommendations
- **APScheduler**: Job scheduling for reminders
- **Faker**: Synthetic data generation
- **Pytest**: Testing framework
- **Tailwind CSS**: UI styling

## File Statistics

- Python files: 15+
- Templates: 2 (base + dashboard, more to come)
- Total lines of code: ~800+
- Models: 5
- Blueprints: 6
